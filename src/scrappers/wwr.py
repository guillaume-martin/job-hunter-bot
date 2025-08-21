# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
import time
import urllib

from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


# Selenium configuration
FIREFOX_PATH = os.getenv("FIREFOX_PATH")
GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH")

# Search configuration
BASE_URL = 'https://weworkremotely.com'
REGION = "taiwan"

def details_url(job):
    """ Extracts and returns the full URL to the job details page from a BeautifulSoup job element.
    Args:
        job (bs4.element.Tag): A BeautifulSoup tag representing a job listing, expected to contain anchor tags.
    Returns:
        str: The absolute URL to the job details page if found, otherwise an empty string.
    """ 
    
    links = job.find_all('a')
    try:
        url = BASE_URL
        url += [link["href"] for link in links if link["href"].startswith("/remote-jobs/")][0]
        url = urllib.parse.urljoin(BASE_URL, url)
    except IndexError:
        url = ""
        pass 

    return url


def publication_time(job):
    """ Extracts the publication date from a job listing element.

    Args:
        job (bs4.element.Tag): A BeautifulSoup Tag object representing a job listing.

    Returns:
            str: The formatted publication date as a string in 'YYYY-MM-DD' format.
    """
    
    date_tag = job.find('p', class_='new-listing__header__icons__date')
    try:
        days_str = date_tag.text.strip().replace('d', '')
    except AttributeError as e:
        print(f"Error extracting date from job: {e}")
        # If we cannot find the date, we assume it's a new post.
        days_str = "New"

    # New posts are marked as "NEW".
    if days_str == "New":
        days_since_posted = 0
    else:
        days_since_posted = int(days_str)
    
    date_published = datetime.now() - timedelta(days=days_since_posted)

    formatted_time = date_published.strftime('%Y-%m-%d')
    
    return formatted_time


def job_details(job):
    """
    Extracts job details from a BeautifulSoup job listing element.

    Args:
        job (bs4.element.Tag): A BeautifulSoup Tag object representing a job listing.

    Returns:
        dict: A dictionary containing the extracted job details:
            - company (str): The name of the company.
            - title (str): The job title.
            - date_published (str): The date the job was published (currently empty).
            - url (str): The URL to the job details page.
    """
    company = job.find('p', class_='new-listing__company-name').text
    title = job.find('h4', class_='new-listing__header__title').text
    # region = job.find('span', class_='region_company')
    date_published = publication_time(job)
    job_url = details_url(job)

    details = {
        "company": company,
        "title": title,
        # "region": region,
        "date_published": date_published,
        "date_published": "",
        "url": job_url
        }

    return details


def get_jobs(term, region=REGION):
    """
    Scrapes job listings from the WWR (We Work Remotely) website based on a search term and region.
    
    Args:
        term (str): The search keyword to filter job listings.
        region (str, optional): The region to filter job listings. Defaults to REGION.
    
    Returns:
        list: A list of job details extracted from the search results.
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
