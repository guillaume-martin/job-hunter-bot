# -*- coding: utf-8 -*-
import urllib
import time
from datetime import datetime

from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


# Selenium configuration
FIREFOX_PATH = "/opt/firefox/firefox-bin"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver" # Search configuration

# Search configuration
BASE_URL = 'https://weworkremotely.com'
REGION = "taiwan"

def details_url(job):
    """ Returns the url to the job details
    """
    links = job.find_all('a')
    try:
        url = BASE_URL + "/"
        url += [link for link in links if "listings" in link][0]
    except IndexError:
        url = ""
        pass 

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
    The method extracts the value of the datetime argument and
    format it as yyyy-mm-dd
    """
    time_tag = job.find('time')
    if time_tag is None:
        # Try to get the data from the job details
        r = requests.get(f"{BASE_URL}/{details_url(job)}")
        soup = BeautifulSoup(r.content, 'html.parser')
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

    company = job.find('p', class_='new-listing__company-name').text
    title = job.find('h4', class_='new-listing__header__title').text
    # region = job.find('span', class_='region_company')
    # date_published = publication_time(job)
    job_url = f"{BASE_URL}/{details_url(job)}"

    details = {
        "company": company,
        "title": title,
        # "region": region,
        #"date_published": date_published,
        "date_published": "",
        "url": job_url
        }

    return details


def get_jobs(term, region=REGION):
    """ Returns the list of jobs from the search result

    Parameters:
    ----------
    term: String
        The keyword searched.

    region: String
        The geographic region of the jobs

    Returns:
    -------

    """
    # Setup Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.binary_location = FIREFOX_PATH

    # Specify the path to Geckodriver if not in PATH
    service = Service(GECKODRIVER_PATH)

    # Start a new browser session
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        search_url = BASE_URL + "/remote-jobs/search" + f"?term={term}"

        driver.get(search_url)
        # Wait for the page to load
        time.sleep(5)

        page_content = driver.page_source

    finally:
        driver.quit()

    soup = BeautifulSoup(page_content, "html.parser")
    jobs_list = soup.find_all('li', class_='feature')
       
    jobs = []
    for job in jobs_list:
        jobs.append(job_details(job))

    return jobs
