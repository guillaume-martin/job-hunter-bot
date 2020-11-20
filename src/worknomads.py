# -*- coding: utf-8 -*-

import json
import logging
from dateutil.parser import parse
from datetime import datetime

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# file_handler = logging.FileHandler('../logs/job_search.log')
# file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
logger.addHandler(stream_handler)

API = 'https://www.workingnomads.co/api/exposed_jobs/'
LOCATIONS = ['global', 'asia', '100% fully remote']


def keep_job(job, term):
    term = term.lower()
    title = job['title'].lower()
    description = job['description'].lower()
    tags = job['tags'].lower()
    
    
    if job['location'].lower() not in LOCATIONS:
        return False
    
    if term in title or term in description or term in tags:
        return True
    else:
        return False
    
    
def get_jobs(term):
    logger.info(f"Locations: {', '.join(LOCATIONS)}")
    jobs = []
    r = requests.get(API)
    jobs_list = json.loads(r.content)
    
    for job in jobs_list:
        if keep_job(job, term):
            jobs.append({
                'title': job['title'],
                'company': job['company_name'],
                "date_published": datetime.strftime(parse(job['pub_date']), '%Y-%m-%d'),
                'url': job['url']
                })
            
    return jobs
