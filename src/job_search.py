""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

import config
from mailer import send_email
from scrappers import remotive
from scrappers import wwr
from scrappers import remoteok
from scrappers import worknomads
from scrappers import remoteco
from scrappers import indeed
from scrappers import tw104

# Setup paths
script_dir = Path(__file__).parent
main_dir = (script_dir / '..').resolve()
logs_dir = (main_dir / 'logs').resolve()
output_dir = (main_dir / 'output').resolve()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

date = datetime.strftime(datetime.now(), '%Y-%m-%d')
file_handler = logging.FileHandler(f'{logs_dir}/{date}.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


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
        A list of jobs saved as dictionaries.
    """
    jobs = []
    for term in searches:
        logger.info(f"=============== {term} ===============")

        # Get jobs from Remotive
        logger.info("Searching Remotive jobs...")
        new_jobs = remotive.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)

        # Get data jobs from Remotive
        logger.info("Loading Remotive Data jobs...")
        new_jobs = remotive.get_jobs_by_category('Data')
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)

        # Get jobs from wwr
        logger.info("Searching We Work Remotely jobs...")
        new_jobs = wwr.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)
        
        # Get jobs from remoteok
        logger.info("Searching remote | OK...")
        new_jobs = remoteok.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)
        
        # Get jobs from worknomads
        logger.info("Searching worknomads")
        new_jobs = worknomads.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)

        # Get jobs from remote.co
        logger.info("Searching remote.co")
        new_jobs = remoteco.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)

        # Get jobs from 104
        # logger.info("Searching 104")
        # new_jobs = tw104.get_jobs(term)
        # logger.info(f"Found {len(new_jobs)} jobs")
        # jobs += new_jobs
        # logger.info('-' * 50)

        # # Get jobs from Indeed
        # logger.info("Searching Indeed")
        # new_jobs = indeed.get_jobs(term)
        # logger.info(f"Found {len(new_jobs)} jobs")
        # jobs += new_jobs
        # logger.info('-' * 50)
        
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


def filter_titles(jobs, searches):
    """ Remove all jobs that don't have any keyword in their title
    
    Parameters
    ----------
    jobs: List
        The list of jobs to process    
    
    searches: List
        A list of search terms
    """

    jobs_to_keep = []
    jobs_to_reject = []
    for keywords in searches:
        logger.debug(f"Filtering {keywords}")
        for job in jobs:
            keywords_list = keywords.lower().split(' ')
            title_list = job['title'].lower().split(' ')
            logger.debug(f"Controlling if {keywords_list} is in {title_list}")
            if all(item in title_list for item in keywords_list):
                logger.debug("-" * 50)
                logger.debug(f"{keywords_list} in {title_list}")
                if job not in jobs_to_keep:
                    jobs_to_keep.append(job)
            else:
                if job not in jobs_to_reject:
                    jobs_to_reject.append(job)

    #send_jobs(jobs_to_reject, 'Rejected jobs')

    return jobs_to_keep


def main():
    
    # Extract jobs from web sites and save them in a list
    logger.info("###############  Searching Jobs  ###############")
    jobs = find_jobs(config.searches)
    
    logger.info("###############  Cleaning Job List  ###############")

    # Remove duplicates
    logger.info("Removing duplicates...")
    single_jobs = []
    for job in jobs:
        if job not in single_jobs:
            single_jobs.append(job)
    logger.info(f"Removed {len(jobs) - len(single_jobs)} jobs.")
            
    # Remove older posts
    logger.info("Removing older jobs...")
    before = len(single_jobs)
    old_jobs = []
    for job in single_jobs:
        date_published = datetime.strptime(job['date_published'], '%Y-%m-%d')
        days_since_published = (datetime.now() - date_published).days
        if days_since_published > config.since:
            old_jobs.append(job)

    for old_job in old_jobs:
        single_jobs.remove(old_job)

    logger.info(f"Removed {before - len(single_jobs)} jobs")

    # Keep only the good titles
    logger.info("Filtering job titles...")
    single_jobs = filter_titles(single_jobs, config.searches)

    logger.info(f"Removed {before - len(single_jobs)} jobs")
    
    # Send jobs by email
    logger.info("###############  Sending Results  ###############")
    logger.info(f"Sending {len(single_jobs)} jobs.")
    subject = f"New Remote Jobs for {date}"
    content = jobs_to_html(single_jobs)
    send_email(subject, content)


if __name__ == '__main__':
    load_dotenv(verbose=False)
    main()
