import logging
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from dateutil.parser import parse

from ..config import Config
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://remoteok.com"


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
)
ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": ACCEPT,
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-GPC": "1",
    "Host": "remoteok.com",
}


class RemoteOkScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url=BASE_URL, name="RemoteOK")
        _cfg = Config.scraper_config("remoteok")
        self.locations: list[str] = _cfg.get("locations", ["Worldwide"])

    def _build_search_url(self, term):
        search_url = (
            f"{self.base_url}/?location={','.join(self.locations)}&"
            f"search={term}&action=get_jobs"
        )

        return search_url

    def extract_company(self, job_element):
        company = job_element.find("h3").text
        company = company.replace("\n", "").strip()
        company = company.replace("\t", "").strip()

        return company

    def extract_title(self, job_element):
        title = job_element.find("h2").text
        title = title.replace("\n", "").strip()
        title = title.replace("\t", "").strip()

        return title

    def extract_url(self, job_element):
        try:
            source_element = job_element.find("td", class_="source")
            href = source_element.find("a")["href"]
            url = self.base_url + href
        except Exception:
            url = "no URL"
        return url

    def extract_date_published(self, job_element):
        time_tag = job_element.find("time")
        time = time_tag["datetime"]
        formatted_time = datetime.strftime(parse(time), "%Y-%m-%d")
        return formatted_time

    def extract_job_description(self, job_url: str) -> str:
        translation_table = str.maketrans({"\n": " ", "\r": " ", "\t": " "})

        r = self._request(
            method="GET", url=job_url, headers=HEADERS, allow_redirects=True
        )

        if r is None or r.status_code != 200:
            logger.error(f"Failed to fetch job description for {job_url}.")
            return "No description available"

        soup = BeautifulSoup(r.content, "lxml")
        description_div = soup.select_one("div.html, div.markdown")

        if description_div is not None:
            description: str = (
                description_div.get_text(separator=" ", strip=True)
                .replace("\\n", "")
                .translate(translation_table)
                .strip()
            )
        else:
            logger.error(f"Failed to fetch job description for {job_url}")
            description = "No description available."

        return description

    def get_jobs(self, term: str) -> list[dict[str, Any]]:
        search_url = self._build_search_url(term)
        r = self._request(method="GET", url=search_url, headers=HEADERS)
        if r:
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

        return self.jobs
