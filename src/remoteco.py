""" Search jobs from remote.co
"""

import json
import logging

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

AJAX_URL = "https://remote.co/jm-ajax/get_listings/"


def load_jobs(term):

    payload = {
        'search_keywords': term,
        'per_page': 50,
        'orderby':'date',
        'order': 'DESC',
        'page': 1,
        'show_pagination': 'false'
    }

    r = requests.get(AJAX_URL, payload)
    results = json.loads(r.content)
    soup = BeautifulSoup(results['html']    , 'lxml')

    jobs_list = soup.find_all('li', class_='job_listing')
    print(f"found {len(jobs_list)} jobs")
    return jobs_list

def get_jobs(term):

    jobs = []

    jobs_list = load_jobs(term)

    for job in jobs_list:

        jobs.append({
            'title': job.find('h3').text.strip(),
            'company': job.find('div', class_='company').text.strip(),
            'url': job.find('a')['href'],
            'date_published': job.find('time')['datetime']
        })
    
    return jobs    