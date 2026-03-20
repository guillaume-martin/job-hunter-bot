import json
import logging
import urllib
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from ..config import Config
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://oqubrx6zeq-3.algolianet.com/1/indexes/*/queries"

HEADERS = {
    "x-algolia-agent": "Algolia for JavaScript (4.0.0); Browser (lite)",
    "x-algolia-api-key": Config.REMOTIVE_ALGOLIA_KEY,
    "x-algolia-application-id": Config.REMOTIVE_ALGOLIA_ID,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://remotive.com/",
}

LOCATIONS = '["locations:Worldwide","locations:APAC"]'


class RemotiveScraper(BaseScraper):
    """Scraper for remotive.io jobs"""

    def __init__(self):
        super().__init__(base_url=BASE_URL, name="Remotive")

    def __build_api_payload(self, term: str) -> dict:
        term_encoded = urllib.parse.quote(term)
        locations_encoded = urllib.parse.quote(LOCATIONS)
        params = (
            f"facetFilters=%5B{locations_encoded}%5D&"
            "facets=&"
            "maxValuesPerFacet=1000&"
            "page=0&"
            f"query=%22{term_encoded}%22&tagFilters="
        )

        payload = {"requests": [{"indexName": "live_jobs", "params": params}]}

        return payload

    def extract_company(self, job_element):
        return job_element.get("company_name", "unknown")

    def extract_title(self, job_element):
        return job_element.get("title", "unknown")

    def extract_url(self, job_element):
        return job_element.get("url", "unknown")

    def extract_date_published(self, job_element):
        utc_pub_date = datetime.utcfromtimestamp(job_element["publication_date"])
        date_published = datetime.strftime(utc_pub_date, "%Y-%m-%d")
        return date_published

    def get_jobs(self, term: str) -> list[dict[str, Any]]:
        payload = self.__build_api_payload(term)

        r = self._request(
            method="POST", url=BASE_URL, headers=HEADERS, data=json.dumps(payload)
        )

        if r is None:
            logger.error("Request failed, no response received")
            return []

        response = json.loads(r.content)
        results = response["results"]
        jobs_list = results[0]["hits"]

        for job in jobs_list:
            job_details = self._extract_job_details(job)
            self.jobs.append(job_details)

        return self.jobs

    def extract_job_description(self, job_url: str) -> str:
        """Extract the job description from the job URL

        Args:
            job_url (str): URL to the job posting

        Returns:
            str: Extracted job description, or default message if extraction fails
        """
        translation_table = str.maketrans({"\n": " ", "\r": " ", "\t": " "})

        try:
            r = self._request(method="GET", url=job_url, headers=HEADERS, timeout=20)

            if r:
                soup = BeautifulSoup(r.content, "lxml")
                description_div = soup.find("div", class_="left")

                if description_div is None:
                    logger.warning(f"Description div not found for {job_url}")
                    return "Description div not found in job page."

                job_description: str = (
                    description_div.get_text(separator=" ", strip=True)
                    .translate(translation_table)
                    .strip()
                )
            else:
                logger.error(f"Failed to fetch job description for {job_url}")
                job_description = "Request for job page failed."
        except (RequestException, IndexError) as e:
            logger.exception(f"Failed to extract job description for {job_url}: {e}")
            job_description = "Request for job page failed."

        return job_description
