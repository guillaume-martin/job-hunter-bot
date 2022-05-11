from datetime import date

import requests
from bs4 import BeautifulSoup


search_url = 'https://www.104.com.tw/jobs/search/'


def get_job_title(job):
    try:
        title = job.find('a', class_='js-job-link').text.strip()
    except:
        title = ''
    
    return title


def get_company_name(job):
    try:
        company_name = job.find('ul', class_='b-list-inline').find('a').text.strip()
    except:
        company_name = ''

    return company_name


def get_published_date(job):
    try:
        raw_date = job.find('span', class_='b-tit__date').text.strip()
        day = int(raw_date.split('/')[1])
        month = int(raw_date.split('/')[0])
        yr = date.today().year
        published_date = date(yr, month, day).strftime('%Y-%m-%d')
    except:
        published_date = date.today().strftime('%Y-%m-%d')
    return published_date


def get_job_url(job):
    try:
        url = "https://" + job.find('a', class_='js-job-link')['href']
    except:
        url = ''

    return url


def get_jobs(term):
    parameters = {
        'ro': '0',
        'isnew': '7',
        'kwop': '7',
        'keyword': f'"{term}"',
        'order': '15',
        'asc': '0',
        'sctp': 'M',
        'scmin': '50000',
        'scstrict': '1',
        'scneg': '0',
        'page': '1',
        'mode': 's'
    }

    jobs = []

    r = requests.get(search_url, parameters)
    soup = BeautifulSoup(r.content, 'lxml')

    jobs_list = soup.find_all('article', class_='job-list-item')

    for job in jobs_list:
        jobs.append({
            'title': get_job_title(job),
            'company': get_company_name(job),
            'date_published': get_published_date(job),
            'url': get_job_url(job)
        })

    return jobs