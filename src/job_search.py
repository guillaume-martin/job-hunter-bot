""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
import os
import ssl
import logging
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

import config
import remotive
import wwr
import remoteok
import worknomads
import remoteco
import indeed
import tw104


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
        The jobs are stored in a list of dictionary.
        Each dictionary is a job post:
        {
            "company": "Acme, Inc.",
            "title": "Director of Engineering",
            "url": "https://remotive.io/dir-engineer",
            "date_published": "2020-11-12"
        }
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
        logger.info("Searching 104")
        new_jobs = tw104.get_jobs(term)
        logger.info(f"Found {len(new_jobs)} jobs")
        jobs += new_jobs
        logger.info('-' * 50)

        # # Get jobs from Indeed
        # logger.info("Searching Indeed")
        # new_jobs = indeed.get_jobs(term)
        # logger.info(f"Found {len(new_jobs)} jobs")
        # jobs += new_jobs
        # logger.info('-' * 50)
        
    return jobs


def jobs_to_csv(jobs):
    
    output = "company,title,date,url\n"
    for job in jobs:
        output += '"' + job['company'] + '",'
        output += '"' + job['title'] + '",'
        output += '"' + job['date_published'] + '",'
        output += '"' + job['url'] + '"\n'
    
    with open(f'{output_dir}/{date}.csv', 'w') as file:
        file.write(output)
        

def jobs_to_html(jobs):
    
    html = '<div>'
    
    for job in jobs:
        html +=  (
            "<p>"
            f"<a href='{job['url']}'>{job['title']}</a>&nbsp@&nbsp"
            f"{job['company']}&nbsp"
            f"({job['date_published']})"
            "</p>"
            )
    
    html += '</div>'
        
    return html


def jobs_to_text(jobs):

    txt = ''
    for job in jobs:
        txt += f"{job['title']} @ {job['company']} ({job['date_published']}) - {job['url']}\n"

    return txt


def send_jobs(jobs):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_pwd = os.getenv('SMTP_PASSWORD')

    receiver_email = os.getenv('RECEIVER_EMAIL')

    message = MIMEMultipart("alternative")
    message['subject'] = 'remote job search results'
    message['from'] = smtp_user
    message['to'] = receiver_email

    text = MIMEText(jobs_to_text(jobs), 'plain')
    html = MIMEText(jobs_to_html(jobs), 'html')

    message.attach(text)
    message.attach(html)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        logger.info(f"Connect as {smtp_user} : {smtp_pwd}")
        server.login(smtp_user, smtp_pwd)
        logger.info(f"Sending email to {receiver_email}")
        server.sendmail(
            smtp_user,
            receiver_email,
            message.as_string()
        )


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
    
    # Remove unwanted jobs
    logger.info("Removing unwanted jobs...")
    before = len(single_jobs)
    unwanted_jobs = []
    for job in single_jobs:
        for exclude in config.excluded_terms:
            exclude_cleaned = exclude.lower() \
                              .replace(' ', '') \
                               .replace('-', '')
            title_cleaned = job['title'].lower() \
                                        .replace(' ', '') \
                                        .replace('-', '')

            if exclude_cleaned in title_cleaned:
                unwanted_jobs.append(job)

    for unwanted_job in unwanted_jobs:
        try:
            single_jobs.remove(unwanted_job)
        except:
            logger.info(f"Failed to remove {unwanted_job}")
            continue

    logger.info(f"Removed {before - len(single_jobs)} jobs")
    
    # Save jobs 
    jobs_to_csv(single_jobs)

    # Send jobs by email
    logger.info("###############  Sending Results  ###############")
    logger.info(f"Sending {len(single_jobs)} jobs.")
    send_jobs(single_jobs)
    

if __name__ == '__main__':
    load_dotenv(verbose=False)
    main()
