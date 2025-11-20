""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv("src/.env")

from datetime import datetime

from .config import searches, since, sites
from .mailer import send_email
from .scrappers.scraper_factory import get_scraper

date = datetime.strftime(datetime.now(), '%Y-%m-%d')


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
    for term in searches:
        print(f"=============== {term} ===============")

        for site in sites:
            print("-" * 20)
            print(f"Searching jobs on {site}...")
            scrapper = get_scraper(site)
            scrapper.get_jobs(term)

            # Remove duplicate jobs
            print("Removing duplicate jobs...")
            scrapper.remove_duplicates()

            # Remove older jobs
            print(f"Removing jobs older than {since} days...")
            scrapper.remove_older_jobs(since)

            # Extract job descriptions
            print("Extracting job descriptions...")
            for job in scrapper.jobs:
                description = scrapper.extract_job_description(job['url'])
                job['description'] = description

            print(f"Found {len(scrapper.jobs)} jobs on {site} for term '{term}'")

            jobs += scrapper.jobs

    return jobs


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

    html = "<div>"

    for job in jobs:
        url = job.get("url", "")
        title = job.get("title", "Missing title")
        company = job.get("company", "Missing employer")
        date_published = job.get("date_published", f"Found on {date}")

        html +=  (
            "<p>"
            f"<a href='{url}'>{title}</a>&nbsp;&nbsp;"
            f"{company}&nbsp;"
            f"({date_published})"
            "</p>"
            )

    html += "</div>"

    return html

def main():

    # Extract jobs from web sites and save them in a list
    print("###############  Searching Jobs  ###############")
    jobs = find_jobs(searches)

    # print("###############  Cleaning Job List  ###############")

    # Add logic for removing non relevant jobs here (ai analyzer)


    # Send jobs by email
    print("###############  Sending Results  ###############")
    print(f"Sending {len(jobs)} jobs.")
    subject = f"New Jobs Openings for {date}"
    if len(jobs) == 0:
        content = "<p>No new jobs found.</p>"
    else:
        content = jobs_to_html(jobs)

    send_email(subject, content)


def lambda_handler(event, context):
    main()

if __name__ == '__main__':
    main()
