import logging
from dateutil.parser import parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('../logs/job_search.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


BASE_URL = 'https://remoteok.io'
LOCATION = 'worldwide'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Sec-GPC': '1',
    'Host': 'remoteok.io',
    }

def publication_time(job):
    time_tag = job.find('time')

    time = time_tag['datetime']
    formatted_time = datetime.strftime(parse(time), '%Y-%m-%d')

    return formatted_time


def get_jobs(term):
    
    jobs = []
   
    query_url = f"{BASE_URL}/remote-{term}-jobs?location={LOCATION}"
    logger.info(f"query_url = {query_url}")

    r = requests.get(query_url, headers=HEADERS)
    
    soup = BeautifulSoup(r.content, 'lxml')

    jobs_list = soup.find_all('tr', class_='job')

    for job in jobs_list:
        title = job.find('h2').text
        company = job.find('h3').text
        date_published = publication_time(job)   
        try:
            url = BASE_URL + job.find('td', class_='source').find('a')['href']
        except:
            url = 'no URL'
        
        jobs.append({
            'title': title,
            'company': company,
            'date_published': date_published,
            'url': url
            })
        
    return jobs
