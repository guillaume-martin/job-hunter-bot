from dateutil.parser import parse
from datetime import datetime

from .base_scraper import BaseScraper

from requests import request
from bs4 import BeautifulSoup


BASE_URL = "https://remoteok.com"
LOCATIONS = ["Worldwide", "region_AS", "TW"]
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Sec-GPC': '1',
    'Host': 'remoteok.com',
    }

class RemoteOkScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url=BASE_URL, name='RemoteOK')

    def _build_search_url(self, term):
        search_url = f"{self.base_url}/?location={",".join(LOCATIONS)}&search={term}&action=get_jobs"
        return search_url

    def extract_company(self, job_element):
        company = job_element.find('h3').text
        company = company.replace("\n", "").strip()
        company = company.replace("\t", "").strip()

        return company

    def extract_title(self, job_element):
        title = job_element.find('h2').text
        title = title.replace("\n", "").strip()
        title = title.replace("\t", "").strip()

        return title

    def extract_url(self, job_element):
        try:
            url = self.base_url + job_element.find("td", class_="source").find("a")["href"]
        except:
            url = "no URL"
        return url

    def extract_date_published(self, job_element):
        time_tag = job_element.find("time")
        time = time_tag["datetime"]
        formatted_time = datetime.strftime(parse(time), "%Y-%m-%d")
        return formatted_time

    def extract_job_description(self, job_url: str) -> str:
        translation_table = str.maketrans({
            "\n": " ",
            "\r": " ",
            "\t": " "
        })

        r = request("GET", job_url, headers=HEADERS, allow_redirects=True)
        soup = BeautifulSoup(r.content, "lxml")
        description_div = soup.select_one("div.html, div.markdown")
        if description_div:
            description = description_div.text.replace("\\n", "").translate(translation_table).strip()
        else:
            description = "No description available."
        return description


    def get_jobs(self, term: str) -> list:
        search_url = self._build_search_url(term)
        r = request("GET", search_url, headers=HEADERS)
        soup = BeautifulSoup(r.content, "lxml")

        self.jobs = [
            {
                "title": self.extract_title(job),
                "company": self.extract_company(job),
                "date_published": self.extract_date_published(job),
                "url": self.extract_url(job),
            }
            for job in soup.find_all("tr", class_="job")
        ]