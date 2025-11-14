""" Search jobs from remote.co
"""

import json

from .base_scraper import BaseScraper

from requests import request
from bs4 import BeautifulSoup


AJAX_URL = "https://remote.co/jm-ajax/get_listings/"


class RemoteCoScraper(BaseScraper):
    """ Scraper for remote.co jobs """
    def __init__(self):
        super().__init__(base_url="https://remote.co/remote-jobs/", name="Remote.co")

    def _build_api_payload(self, term):
        payload = {
            'search_keywords': term,
            'per_page': 50,
            'orderby':'date',
            'order': 'DESC',
            'page': 1,
            'show_pagination': 'false'
        }
        return payload

    def extract_company(self, job_element):
        return job_element.find('div', class_='company').text.strip()

    def extract_title(self, job_element):
        return job_element.find('h3').text.strip()

    def extract_url(self, job_element):
        return job_element.find('a')['href']

    def extract_date_published(self, job_element):
        return job_element.find('time')['datetime']

    def get_jobs(self, term):
        r = request("POST", AJAX_URL, params=self._build_api_payload(term))
        results = json.loads(r.content)
        soup = BeautifulSoup(results['html'], 'lxml')
        jobs_list = soup.find_all('li', class_='job_listing')

        for job in jobs_list:
            job_details = self._extract_job_details(job)
            self.jobs.append(job_details)   

