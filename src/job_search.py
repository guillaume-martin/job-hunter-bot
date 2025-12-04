""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv("src/.env")

from datetime import datetime
import os
from pathlib import Path
from typing import Dict, List, Literal

from .config import Config
from .mailer import send_email
from .scrappers.scraper_factory import get_scraper
from .ai_analyzer import AIAnalyzer

date = datetime.strftime(datetime.now(), '%Y-%m-%d')

def send_results(
    context: Literal["cloud", "local"],
    selected_jobs: List[Dict],
    rejected_jobs: List[Dict],
    date: str,
) -> None:
    """Send or save job results based on the context (cloud or local)."""
    if context == "cloud":
        _send_jobs_by_email(selected_jobs, f"New Jobs Opening for {date}", date)
        _send_jobs_by_email(rejected_jobs, f"Rejected jobs for {date}", date)
    elif context == "local":
        _save_jobs_to_file(selected_jobs, "selected", date)
        _save_jobs_to_file(rejected_jobs, "rejected", date)

def _send_jobs_by_email(jobs: List[Dict], subject: str, date: str) -> None:
    """Send jobs by email.

    Args:
        jobs: List of job dictionaries.
        subject: Email subject.
        date: Date string for logging.
    """
    print(f"###############  Sending {subject}  ###############")
    print(f"Sending {len(jobs)} jobs.")
    content: str = "<p>No jobs found.</p>" if not jobs else jobs_to_html(jobs)
    send_email(subject, content)

def _save_jobs_to_file(jobs: List[Dict], suffix: str, date: str) -> None:
    """Save jobs to a file locally.

    Args:
        jobs: List of job dictionaries.
        suffix: Suffix for the filename (e.g., "selected" or "rejected").
        date: Date string for logging.
    """
    prefix = datetime.now().strftime("%Y-%m-%d")
    path = Path(Config.OUTPUT_PATH)
    file_stem = Path(Config.OUTPUT_FILE).stem
    file_extension = Path(Config.OUTPUT_FILE).suffix
    new_filename = f"{prefix}-{file_stem}-{suffix}{file_extension}"
    full_path = path / new_filename
    markdown = jobs_to_markdown(jobs)

    print(f"###############  Saving {suffix.lower()} Jobs to File  ###############")
    print(f"Saving {len(jobs)} {suffix} jobs.")
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(markdown)
    except IOError as e:
        print(f"Failed to write to file {full_path}: {e}")

def find_jobs(searches):
    """ Find jobs from search terms on multiple web sites
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
    for term in Config.SEARCHES:
        print(f"=============== {term} ===============")

        for site in Config.SITES:
            print("-" * 20)
            print(f"Searching jobs on {site}...")
            scrapper = get_scraper(site)
            scrapper.get_jobs(term)

            # Remove older jobs
            print(f"Removing jobs older than {Config.SINCE} days...")
            scrapper.remove_older_jobs(Config.SINCE)

            # Extract job descriptions
            print("Extracting job descriptions...")
            for job in scrapper.jobs:
                description = scrapper.extract_job_description(job['url'])
                job['description'] = description

            print(f"Found {len(scrapper.jobs)} jobs on {site} for term '{term}'")

            jobs += scrapper.jobs

    return jobs

def remove_duplicates(jobs: List[Dict]) -> List[Dict]:
    """emoves duplicate jobs based on their URLs.

    Jobs with missing or duplicate URLs are removed. Only the first occurrence
    of each URL is kept. Jobs with "missing" URLs are skipped.

    Args:
        jobs (List[Dict]): List of all jobs as dictionaries

    Returns:
        List[Dict]: List of unique jobs as dictionaries
    """
    single_jobs = []
    seen_urls = set()               # Set of jobs URLs that have already been seen
    seen_companies_titles = set()   # Set of companies/titles pairs that have already been seen

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

def select_jobs(jobs: List[Dict], analyzer, resume: str) -> List[Dict]:
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
    print(f"Processing {len(jobs)} jobs...")

    for job in jobs:
        try:
            if not job["description"]:
                print("Jobs does not have a description.")
                job["evaluation"] = "manual"
                selected_jobs.append(job)
                continue

            eval_result = analyzer.analyze_job(resume, job["description"])
            job["evaluation"] = eval_result

        except Exception as e:
            print(f"Failed to analyze job {job.get('title', 'Unknown')}: {e}")
            job["evaluation"] = {"error": f"Analysis failed: {e}"}

        # Only keep the jobs that are worth applying for:
        try:
            job_score = job["evaluation"]["match_score"].split("/")[0]
        except KeyError as e:
            print(f"Error: Missing {e} key in job.")
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
    """ Format jobs into an HTML output that can be sent

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

    html += "<div><table><tr><th>Title</th><th>Company</th><th>Score</th><th>Date Published</th><th>Missing Required Skills</tr>"

    for job in jobs:
        url = job.get("url", "")
        title = job.get("title", "Missing title")
        company = job.get("company", "Missing employer")
        date_published = job.get("date_published", f"Found on {date}")
        evaluation = job.get("evaluation", {})
        score = evaluation.get("match_score", "Missing score")
        missing_required = ", ".join(evaluation.get("missing_required", []))

        html += f"<tr><td><a href='{url}'>{title}</a></td><td>{company}</td><td>{score}</td><td>{date_published}</td><td>{missing_required}</tr>"

    html += "</table></div>"

    return html

def jobs_to_markdown(jobs: List[Dict]) -> str:
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
        date_published = job.get("date_published", f"Found on {date}")
        evaluation = job.get("evaluation", {})
        score = evaluation.get("match_score", "Missing score")
        missing_required = ", ".join(evaluation.get("missing_required", []))

        markdown += f"|[{title}]({url})|{company}|{score}|{date_published}|{missing_required}|\n"

    return markdown

def main(context: str) -> None:

    # Extract jobs from web sites and save them in a list
    print("###############  Searching Jobs  ###############")
    jobs = find_jobs(Config.SEARCHES)

    print("###############  Remove duplicate Jobs  ###############")
    single_jobs = remove_duplicates(jobs)

    print("###############  Selecting Jobs  ###############")
    analyzer = AIAnalyzer(
        api_key=os.getenv("AI_API_KEY"),
        model = Config.MODEL,
        api_url=Config.API_URL,
        prompt_file=Config.PROMPT_FILE,
        temperature=Config.TEMPERATURE,
        timeout=Config.TIMEOUT
    )

    # Load resume once (e.g., from a file or environment variable)
    with open(Config.RESUME_FILE, "r", encoding="utf-8") as f:
        resume = f.read()

    selected_jobs, rejected_jobs = select_jobs(single_jobs, analyzer, resume)

    send_results(context, selected_jobs, rejected_jobs, date)


def lambda_handler(event, context):
    run_context = "cloud"
    main(run_context)

if __name__ == '__main__':
    run_context = "local"
    main(run_context)
