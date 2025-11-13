# -*- coding: utf-8 -*-

from datetime import datetime
import json
from typing import Dict, List 
import urllib

from base_scraper import BaseScraper

from requests import request


BASE_URL = 'https://oqubrx6zeq-3.algolianet.com/1/indexes/*/queries'

HEADERS = {
    'x-algolia-agent': 'Algolia for JavaScript (4.0.0); Browser (lite)',
    'x-algolia-api-key': '8ad949132d497255ffc04accd141f083',
    'x-algolia-application-id': 'OQUBRX6ZEQ',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept':'application/json, text/plain, */*',  
    'Accept-Language':'en',
    'Accept-Encoding':'gzip, deflate', 
    'Referer':'https://remotive.com/'
    }

LOCATIONS = '["locations:Worldwide","locations:APAC"]'

class RemotiveScraper(BaseScraper):
    """ Scraper for remotive.io jobs """
    def __init__(self):
        super().__init__(base_url=BASE_URL, name="Remotive")

    def _build_search_url(self, term):
        return BASE_URL

    def __build_api_payload(self, term: str) -> Dict: 
        term_encoded = urllib.parse.quote(term)
        locations_encoded = urllib.parse.quote(LOCATIONS)
        params = (
            f"facetFilters=%5B{locations_encoded}%5D&"
            "facets=&"
            "maxValuesPerFacet=1000&"
            "page=0&"
            f"query=%22{term_encoded}%22&tagFilters="
        )
    
        payload = {
            "requests":[{
                "indexName":"live_jobs",
                "params":params
            }]
        }

        return payload

    def _extract_company(self, job_element):
        return job_element.get("company_name", "unknown")

    def _extract_title(self, job_element):
        return job_element.get("title", "unknown")

    def _extract_url(self, job_element):
        return job_element.get("url", "unknown")

    def _extract_date_published(self, job_element):
        utc_pub_date = datetime.utcfromtimestamp(job_element['publication_date'])
        date_published = datetime.strftime(utc_pub_date, '%Y-%m-%d')
        return date_published
   
    def get_jobs(self, term:str) -> list:
        search_url = self._build_search_url(term) 
        payload = self.__build_api_payload(term)

        r = request("POST", search_url, headers=HEADERS, data=json.dumps(payload))
        response = json.loads(r.content)
        results = response['results']
        jobs_list = results[0]['hits']

        for job in jobs_list:
            job_details = self._extract_job_details(job)
            self.jobs.append(job_details)


def get_jobs_by_category(category: str) -> List:
    """ Search jobs in a category on remotive.io 
    
    Parameters
    ----------
    category: String
        The name of the category to search.

    Returns
    -------
    List
        A list of dictionaries with jobs details    
    """
    locations_encoded = urllib.parse.quote(LOCATIONS)

    params = (
        "facetFilters="
        f"%5B{locations_encoded}%2C%"
        f"5B%22category%3A{category}%22%5D%5D&"
    )
    
    payload = {
        "requests": [
            {
                "indexName": "live_jobs",
                "params": params
            },
        ]
    }

    jobs = load_jobs(payload)
    return jobs
