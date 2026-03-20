"""Searches jobs offers on a selection of web sites"""

import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

from .ai_analyzer import AIAnalyzer
from .config import Config
from .mailer import send_email
from .scrappers.scraper_factory import get_scraper

load_dotenv("src/.env")

DATE = datetime.strftime(datetime.now(), "%Y-%m-%d")

# Load the logging configuration
logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))

# Check if the log directory exists, if not create it
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

# Initialize the logger
logger = logging.getLogger(__name__)


def send_results(
    context: Literal["cloud", "local"],
    selected_jobs: list[dict],
    rejected_jobs: list[dict],
    date: str,
) -> None:
    """Send or save job results based on the context (cloud or local)."""
    if context == "cloud":
        _send_jobs_by_email(selected_jobs, f"New Jobs Opening for {date}")
        _send_jobs_by_email(rejected_jobs, f"Rejected jobs for {date}")
    elif context == "local":
        _save_jobs_to_file(selected_jobs, "selected", date)
        _save_jobs_to_file(rejected_jobs, "rejected", date)


def _send_jobs_by_email(jobs: list[dict], subject: str) -> None:
    """Send jobs by email.

    Args:
        jobs: List of job dictionaries.
        subject: Email subject.
        date: Date string for logging.
    """
    logger.info(f"###############  Sending {subject}  ###############")
    logger.info(f"Sending {len(jobs)} jobs.")
    content: str = "<p>No jobs found.</p>" if not jobs else jobs_to_html(jobs)
    send_email(subject, content)


def _save_jobs_to_file(jobs: list[dict], suffix: str, date: str) -> None:
    """Save jobs to a file locally.

    Args:
        jobs: List of job dictionaries.
        suffix: Suffix for the filename (e.g., "selected" or "rejected").
        date: Date string for logging.
    """
    path = Path(Config.OUTPUT_PATH)
    file_stem = Path(Config.OUTPUT_FILE).stem
    file_extension = Path(Config.OUTPUT_FILE).suffix
    new_filename = f"{date}-{file_stem}-{suffix}{file_extension}"
    full_path = path / new_filename
    markdown = jobs_to_markdown(jobs)

    logger.info(f"##############  Saving {suffix.lower()} Jobs to File  ##############")
    logger.info(f"Saving {len(jobs)} {suffix} jobs.")
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(markdown)
    except OSError as e:
        logger.exception(f"Failed to write to file {full_path}: {e}")


def find_jobs(searches):
    """Find jobs from search terms on multiple web sites
        The jobs are stored in a list of dictionaries.
        Each dictionary is a job post:
        {
            "company": "Acme, Inc.",
            "title": "Director of Engineering",
            "url": "https://remotive.io/dir-engineer",
            "date_published": "2020-11-12"
        }

    Parameters
    ----------
    searches: list
        List of keywords to search for on the different job boards.

    Returns
    -------
    list
        A list of jobs saved as dictionaries wchich keys are "company", "title",
        "date_published", "url"
    """
    jobs = []
    for term in searches:
        logger.info(f"=============== {term} ===============")

        for site in Config.SITES:
            logger.info("-" * 20)
            logger.info(f"Searching jobs on {site}...")
            scrapper = get_scraper(site)
            if site.lower() == "workingnomads":
                scrapper.since = Config.SINCE
            scrapper.get_jobs(term)

            # Remove older jobs
            logger.info(f"Removing jobs older than {Config.SINCE} days...")
            scrapper.remove_older_jobs(Config.SINCE)

            # Extract job descriptions
            logger.info("Extracting job descriptions...")
            for job in scrapper.jobs:
                if "description" not in job or not job["description"]:
                    description = scrapper.extract_job_description(job["url"])
                    job["description"] = description

            logger.info(f"Found {len(scrapper.jobs)} jobs on {site} for term '{term}'")

            jobs += scrapper.jobs

    return jobs


def remove_duplicates(jobs: list[dict]) -> list[dict]:
    """emoves duplicate jobs based on their URLs.

    Jobs with missing or duplicate URLs are removed. Only the first occurrence
    of each URL is kept. Jobs with "missing" URLs are skipped.

    Args:
        jobs (List[Dict]): List of all jobs as dictionaries

    Returns:
        List[Dict]: List of unique jobs as dictionaries
    """
    single_jobs = []
    # Set of jobs URLs that have already been seen
    seen_urls = set()
    # Set of companies/titles pairs that have already been seen
    seen_companies_titles = set()

    for job in jobs:
        job_url = job.get("url", "missing")
        company_title = f"{job.get('company', '')}|{job.get('title', '')}"
        if job_url != "missing" and job_url not in seen_urls:
            single_jobs.append(job)
            seen_urls.add(job_url)
            seen_companies_titles.add(company_title)
        elif company_title not in seen_companies_titles:
            single_jobs.append(job)
            seen_companies_titles.add(company_title)

    return single_jobs


def select_jobs(
    jobs: list[dict], analyzer, resume: str
) -> tuple[list[dict], list[dict]]:
    """Select the jobs that score over the application threshold

    Args:
        jobs: A list of jobs dictionaries.
        analyzer: An AI analyzer instance.
        resume: The resume text

    Returns:
        A list of selected jobs.
    """
    selected_jobs = []
    rejected_jobs = []
    logger.info(f"Processing {len(jobs)} jobs...")

    for job in jobs:
        try:
            if not job["description"]:
                logger.info("Jobs does not have a description.")
                job["evaluation"] = "manual"
                selected_jobs.append(job)
                continue

            eval_result = analyzer.analyze_job(resume, job["description"])
            job["evaluation"] = eval_result

        except Exception as e:
            title = job.get("title", "Unknown")
            logger.exception(f"Failed to analyze job {title}: {e}")
            job["evaluation"] = {"error": f"Analysis failed: {e}"}

        # Only keep the jobs that are worth applying for:
        try:
            job_score = job["evaluation"]["match_score"].split("/")[0]
        except KeyError as e:
            logger.exception(f"Missing {e} key in job.")
            rejected_jobs.append(job)
            continue
        except TypeError as e:
            logger.exception(f"Job evaluation has incorrect type: {e}.")
            rejected_jobs.append(job)
            continue

        # We select jobs with a score over the threshold and jobs that
        # need to be evaluated manually.
        if int(job_score) >= Config.APPLY_THRESHOLD or job["evaluation"] == "manual":
            selected_jobs.append(job)
        else:
            rejected_jobs.append(job)

    return selected_jobs, rejected_jobs


def jobs_to_html(jobs):
    """Format jobs into an HTML output that can be sent

    Parameters
    ----------
    jobs: list
        A list of jobs saved as dictionaries.
        Each dictionary should contain the keys url, title, company, and date_published.

    Returns
    -------
    str
        An HTML script showing all the jobs
    """

    html = """
        <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        }

        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        </style>
    """

    html += (
        "<div><table>"
        "<tr><th>Title</th><th>Company</th><th>Score</th>"
        "<th>Date Published</th><th>Missing Required Skills</th></tr>"
    )

    for job in jobs:
        url = job.get("url", "")
        title = job.get("title", "Missing title")
        company = job.get("company", "Missing employer")
        date_published = job.get("date_published", f"Found on {DATE}")
        evaluation = job.get("evaluation", {})
        score = evaluation.get("match_score", "Missing score")
        missing_required = ", ".join(evaluation.get("missing_required", []))

        html += (
            f"<tr><td><a href='{url}'>{title}</a></td>"
            f"<td>{company}</td>"
            f"<td>{score}</td>"
            f"<td>{date_published}</td>"
            f"<td>{missing_required}</td></tr>"
        )

    html += "</table></div>"

    return html


def jobs_to_markdown(jobs: list[dict]) -> str:
    """Format the jobs into a Markdown output that can be saved in a file

    Args:
        jobs (List[Dict]): A list of jobs stored as dictionaries.

    Returns:
        str: A Markdown formatted string.
    """
    markdown = "|Title|Company|Match Score|Date Published|Missing Required Skills|\n"
    markdown += "|-|-|-|-|-|\n"

    for job in jobs:
        url = job.get("url", "")
        title = job.get("title", "Missing title").replace("|", "\\|")
        company = job.get("company", "Missing employer")
        date_published = job.get("date_published", f"Found on {DATE}")
        evaluation = job.get("evaluation") or {}
        score = evaluation.get("match_score", "Missing score")
        missing_required = ", ".join(evaluation.get("missing_required", []))

        markdown += (
            f"|[{title}]({url})|{company}|{score}|"
            f"{date_published}|{missing_required}|\n"
        )

    return markdown


def main(context: Literal["cloud", "local"]) -> None:
    # Extract jobs from web sites and save them in a list
    logger.info("###############  Searching Jobs  ###############")
    jobs = find_jobs(Config.SEARCHES)

    logger.info("###############  Remove duplicate Jobs  ###############")
    single_jobs = remove_duplicates(jobs)

    logger.info("###############  Selecting Jobs  ###############")
    api_key = os.getenv("AI_API_KEY")
    if api_key is None:
        raise ValueError("AI_API_KEY environment variable is not set")
    analyzer = AIAnalyzer(
        api_key=api_key,
        model=Config.MODEL,
        api_url=Config.API_URL,
        prompt_file=Config.PROMPT_FILE,
        temperature=Config.TEMPERATURE,
        timeout=Config.TIMEOUT,
    )

    # Load resume once (e.g., from a file or environment variable)
    with open(Config.RESUME_FILE, encoding="utf-8") as f:
        resume = f.read()

    selected_jobs, rejected_jobs = select_jobs(single_jobs, analyzer, resume)

    send_results(context, selected_jobs, rejected_jobs, DATE)


def lambda_handler(event, context):
    run_context: Literal["cloud", "local"] = "cloud"
    main(run_context)


if __name__ == "__main__":
    run_context: Literal["cloud", "local"] = "local"
    main(run_context)
