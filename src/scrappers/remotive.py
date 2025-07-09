# -*- coding: utf-8 -*-

from datetime import datetime
import json
from typing import Dict, List 
import urllib

import requests


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


def load_jobs(payload: Dict) -> List:
    """ Save jobs from search result in a list """

    jobs = []

    data = json.dumps(payload)
    r = requests.request('POST', BASE_URL, headers=HEADERS, data=data)

    response = json.loads(r.content)
    results = response['results']
    jobs_list = results[0]['hits']

    for job in jobs_list:
        job_title = job.get("title", "unknown")
        company = job.get("company_name", "unknown")
        salary = job.get("salary", "N/A")
        job_link = job.get("url", "unknown")
        location = job.get("candidate_required_location", "Unknown Location")
        utc_pub_date = datetime.utcfromtimestamp(job['publication_date'])
        date_published = datetime.strftime(utc_pub_date, '%Y-%m-%d')
        jobs.append({
            "company": f"{company}({location})",
            "title": job_title,
            "date_published": date_published,
            "url": job_link
        })

    return jobs 


def get_jobs(term:str) -> List:

    term_encoded = urllib.parse.quote(term)

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

    jobs = load_jobs(payload)

    return jobs


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
