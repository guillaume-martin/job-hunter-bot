# -*- coding: utf-8 -*-

from datetime import datetime
import json
from typing import Dict, List 
import urllib

import requests


BASE_URL = 'https://oqubrx6zeq-3.algolianet.com/1/indexes/*/queries'

HEADERS = {
    'x-algolia-agent': 'Algolia for JavaScript (4.0.0); Browser (lite)',
    'x-algolia-api-key': '7a1d0ebc0d0e9ba3dc035fc09729f2a8',
    'x-algolia-application-id': 'OQUBRX6ZEQ',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept':'application/json, text/plain, */*',  
    'Accept-Language':'en',
    'Accept-Encoding':'gzip, deflate', 
    'Referer':'https://remotive.com/'
    }

LOCATIONS = '[["locations:Worldwide","locations:APAC"]]'


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
        f"facetFilters={locations_encoded}&"
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


def get_jobs_by_category(category):
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

    payload = {
        "requests":[
            {
                "indexName":"live_jobs",
                f"params":"query=&page=0&maxValuesPerFacet=1000&facets=%5B%22us_only%22%2C%22category%22%5D&tagFilters=&facetFilters=%5B%5B%22us_only%3Afalse%22%5D%2C%5B%22category%3A{category}%22%5D%5D"
            },
            {
                "indexName":"live_jobs",
                f"params":"query=&page=0&maxValuesPerFacet=1000&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=us_only&facetFilters=%5B%5B%22category%3A{Category}%22%5D%5D"
            },
            {
                "indexName":"live_jobs",
                "params":"query=&page=0&maxValuesPerFacet=1000&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=%5B%22category%22%5D&facetFilters=%5B%5B%22us_only%3Afalse%22%5D%5D"
            }
        ]
    }

    jobs = load_jobs(payload)

    return jobs
