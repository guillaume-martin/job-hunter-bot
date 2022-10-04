from urllib.parse import urlparse
from datetime import datetime, date, timedelta

import requests
from bs4 import BeautifulSoup
import dateutil.parser as parser


search_url = 'https://www.104.com.tw/jobs/search/'



def _published_date(job_date):
    clean_date = job_date.replace(" ", "")
    parsed_date = parser.parse(clean_date)    
    
    return parsed_date.date()


def _clean_job_link(link):
    parsed = urlparse(link)
    clean_link = "https://" + parsed.netloc + parsed.path
    return clean_link


def get_jobs(term):
    area = "6001001000,6001002000,6001004000"
    isnew = 3
    url  = (
        "https://www.104.com.tw/jobs/search/?"
        f"isnew={isnew}&"
        "kwop=1&"
        f"keyword={term}&"
        f"area={area}"
        "&mode=l&langFlag=0&langStatus=0&recommendJob=0&hotJob=0"
    )
    jobs_list = []

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    jobs_items = soup.find_all("article", {"class":"js-job-item"})
    yesterday = date.today() - timedelta(days = 1)

    for item in jobs_items:
        job = item.find("a", {"class":"js-job-link"})
        job_title = job["title"]
        job_link = _clean_job_link(job["href"])
        job_date = item.find("li", {"class":"job-mode__date"}).text
        pub_date = _published_date(job_date)
        company = item.find("li", {"class":"job-mode__company"}).find("a").text
        if pub_date == yesterday:
            jobs_list.append({
                'title': job_title,
                'company': company,
                'date_published': pub_date,
                'url': job_link
            })

    return jobs_list