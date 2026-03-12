from datetime import date, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from bs4 import BeautifulSoup

from config import since


def load_jobs(job_title, location, since=1):
    """ Creates a soup of all jobs returned by search """
    search_params = {
        'q': f"title:({job_title})",
        'l': location,
        'salary': '$50,000',
        'fromage': since,
        'sort': 'date',
        'limit': 50
        }

    url = ('https://tw.indeed.com/jobs?' + urlencode(search_params))
    print(url)
    r = requests.get(url)
    print(r.status_code)
    soup = BeautifulSoup(r.content, 'html.parser')
    jobs_list = soup.find_all('div', class_='result')

    return jobs_list


def extract_job_title(job_elem):
    title_elem = job_elem.find('h2', class_='title')
    title = title_elem.text.replace('new', '').strip()
    return title


def extract_company(job_elem):
    company_elem = job_elem.find('span', class_='company')
    company = company_elem.text.strip()
    return company


def extract_link(job_elem):
    link = job_elem.find('a')['href']
    try:
        parsed = urlparse(link)
        job_id = parse_qs(parsed.query)['jk'][0]
        job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
    except Exception:
        job_url = f"https://www.indeed.com{link}"
    return job_url


def extract_date(job_elem):
    date_elem = job_elem.find('span', class_='date')
    date = date_elem.text.strip()
    return date


def set_date(since):
    today = date.today()
    delta = timedelta(days=since)
    job_date = today - delta
    job_date_frmt = date.strftime(job_date, '%Y-%m-%d')
    return job_date_frmt


def get_jobs(term):

    jobs = []

    jobs_list = load_jobs(term, 'Taipei', since)

    for job in jobs_list:
        jobs.append({
            'title': extract_job_title(job),
            'company': extract_company(job),
            'date_published': set_date(since),
            'url': extract_link(job)
        })

    return jobs
