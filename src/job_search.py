""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from config import searches, since
from mailer import send_email
from scrappers import remotive
from scrappers import wwr
from scrappers import remoteok
from scrappers import worknomads
from scrappers import tw104


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

        # Get jobs from Remotive
        print("Searching Remotive jobs...")
        new_jobs = remotive.get_jobs(term)
        print(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        print('-' * 50)

        # Get jobs from wwr
        print("Searching We Work Remotely jobs...")
        new_jobs = wwr.get_jobs(term)
        print(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        ('-' * 50)
        
        # Get jobs from remoteok
        print("Searching remote | OK...")
        new_jobs = remoteok.get_jobs(term)
        print(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        print('-' * 50)
        
        # Get jobs from worknomads
        print("Searching worknomads")
        new_jobs = worknomads.get_jobs(term)
        print(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        print('-' * 50)

        # Get jobs from 104
        print("Searching 104.com.tw")
        new_jobs = tw104.get_jobs(term)
        print(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        print('-' * 50)

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
        print(f"Filtering {keywords}")
        for job in jobs:
            keywords_list = keywords.lower().split(' ')
            title_list = job['title'].lower().split(' ')
            print(f"Controlling if {keywords_list} is in {title_list}")
            if all(item in title_list for item in keywords_list):
                print("-" * 50)
                print(f"{keywords_list} in {title_list}")
                if job not in jobs_to_keep:
                    jobs_to_keep.append(job)
            else:
                if job not in jobs_to_reject:
                    jobs_to_reject.append(job)

    return jobs_to_keep


def main():
    
    # Extract jobs from web sites and save them in a list
    print("###############  Searching Jobs  ###############")
    jobs = find_jobs(searches)
    
    print("###############  Cleaning Job List  ###############")

    # Remove duplicates
    print("Removing duplicates...")
    single_jobs = []
    for job in jobs:
        if job not in single_jobs:
            single_jobs.append(job)
    print(f"Removed {len(jobs) - len(single_jobs)} jobs.")
            
    # Remove older posts
    print("Removing older jobs...")
    before = len(single_jobs)
    old_jobs = []
    for job in single_jobs:
        try:
            date_published = datetime.strptime(job['date_published'], '%Y-%m-%d')
            days_since_published = (datetime.now() - date_published).days
            if days_since_published > since:
                old_jobs.append(job)
        except ValueError:
            date_published = job["date_published"]
            continue

    for old_job in old_jobs:
        single_jobs.remove(old_job)

    print(f"Removed {before - len(single_jobs)} jobs")

    # Keep only the titles that contain a keyword
    print("Filtering job titles...")
    single_jobs = filter_titles(single_jobs, searches)

    print(f"Removed {before - len(single_jobs)} jobs")
    
    # Send jobs by email
    print("###############  Sending Results  ###############")
    print(f"Sending {len(single_jobs)} jobs.")
    subject = f"New Remote Jobs for {date}"
    content = jobs_to_html(single_jobs)
    send_email(subject, content)


def lambda_handler(event, context):
    main()

if __name__ == '__main__':
    main()
