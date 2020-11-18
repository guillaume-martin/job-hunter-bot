# -*- coding: utf-8 -*-

import json 
import urllib
import logging
from datetime import datetime

import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('../logs/job_search.log')
file_handler.setFormatter(formatter)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


BASE_URL = 'https://oqubrx6zeq-3.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.0.0)%3B%20Browser%20(lite)&x-algolia-api-key=7a1d0ebc0d0e9ba3dc035fc09729f2a8&x-algolia-application-id=OQUBRX6ZEQ'

HEADERS = {
    'x-algolia-agent': 'Algolia for JavaScript (4.0.0); Browser (lite)',
    'x-algolia-api-key': '7a1d0ebc0d0e9ba3dc035fc09729f2a8',
    'x-algolia-application-id': 'OQUBRX6ZEQ',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept':'application/json, text/plain, */*',  
    'Accept-Language':'en',
    'Accept-Encoding':'gzip, deflate', 
    }

US_ONLY = 'false'


def get_jobs(term, category):

    jobs = []

    term_encoded = urllib.parse.quote(term)
    category_encoded = urllib.parse.quote(category)

    payload = {
      "requests": [
        {
          "indexName": "live_jobs",
          "params": f"query={term_encoded}&page=0&maxValuesPerFacet=1000&facets=%5B%22us_only%22%2C%22category%22%5D&tagFilters=&facetFilters=%5B%5B%22us_only%3A{US_ONLY}%22%5D%2C%5B%22category%3A{category_encoded}%22%5D%5D"
        },
        {
          "indexName": "live_jobs",
          "params": f"query={term_encoded}&page=0&maxValuesPerFacet=1000&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=us_only&facetFilters=%5B%5B%22category%3A{category_encoded}%22%5D%5D"
        },
        {
          "indexName": "live_jobs",
          "params": f"query={term_encoded}&page=0&maxValuesPerFacet=1000&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=%5B%22category%22%5D&facetFilters=%5B%5B%22us_only%3A{US_ONLY}%22%5D%5D"
        }
      ]
    }

    logger.info(f"payload = {payload}")
    r = requests.request('POST', BASE_URL, headers=HEADERS, data=json.dumps(payload))

    response = json.loads(r.content)
    results = response['results']
    jobs_list = results[0]['hits']

    for job in jobs_list:
        if job['candidate_required_location'] == 'Anywhere':
            
            date_published = datetime.utcfromtimestamp(job['publication_date'])
            
            jobs.append({
                "company":job['company_name'],
                "title": job['title'],
                "date_published": datetime.strftime(date_published, '%Y-%m-%d'),
                "url": job['url']
            })

    return jobs
