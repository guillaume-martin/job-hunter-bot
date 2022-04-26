# -*- coding: utf-8 -*-
import urllib
import logging
from datetime import datetime
from dateutil.parser import parse

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# file_handler = logging.FileHandler('../logs/job_search.log')
# file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
logger.addHandler(stream_handler)


BASE_URL = 'https://weworkremotely.com/remote-jobs'

REGION = '0' #'Anywhere (100% Remote) Only'
JOB_TYPE = 'Full-Time'


def details_url(job):
    """ Returns the url to the job details
    """
    links = job.find_all('a')
    url = ''
    for link in links:
        href = link['href']
        if 'remote-jobs' in href:
            url = href.split('/')[2]

    return url


def publication_time(job):
    """ Returns the formatted publication time of the post

    The time is displayed in a <time> tag:
    <time datetime="2020-10-15T02:33:05Z"
          data-local="time"
          data-format="%b %e"
          title="October 15, 2020 at 10:33am TST"
          data-localized=""
          aria-label="Oct 15">Oct 15</time>
    The method extract the value of the datetime argument and
    format it as yyyy-mm-dd
    """
    time_tag = job.find('time')
    if time_tag is None:
        # Try to get the data from the job details
        r = requests.get(f"{BASE_URL}/{details_url(job)}")
        soup = BeautifulSoup(r.content, 'lxml')
        time_tag = soup.find('time')

    time = time_tag['datetime']
    formatted_time = datetime.strftime(parse(time), '%Y-%m-%d')


    return formatted_time


def missing_date(job):
    """ Attempts to get a publication date from the job details
    """


    date_published = publication_time(soup)

    return date_published


def job_details(job):
    """ Creates a dictionary with the basic job information
    """

    company = job.find('span', class_='company').text
    title = job.find('span', class_='title').text
    # region = job.find('span', class_='region_company')
    date_published = publication_time(job)
    job_url = f"{BASE_URL}/{details_url(job)}"

    details = {
        "company": company,
        "title": title,
        # "region": region,
        "date_published": date_published,
        "url": job_url
        }

    return details


def get_jobs(term, region=REGION, job_type=JOB_TYPE):
    """ Returns the list of jobs from the search result

    Parameters:
    ----------
    term: String
        The keyword searched.

    region: String
        The geographic region of the jobs

    job_type: String
        The type of contract (contract or full time)

    Returns:
    -------

    """

    query_url = (
        f"{BASE_URL}/search?"
        f"term={urllib.parse.quote(term)}"
        f"&region[]={urllib.parse.quote(region)}"
        f"&job_listing_type[]={urllib.parse.quote(job_type)}"
        )

    logger.info(f"query_url = {query_url}")
    r = requests.get(query_url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        jobs_list = soup.find_all('li', class_='feature')

    jobs = []
    for job in jobs_list:
        jobs.append(job_details(job))

    return jobs
