# -*- coding: utf-8 -*-

from datetime import datetime, timezone

from .base_scraper import BaseScraper

from bs4 import BeautifulSoup
from dateutil.parser import parse
from requests import request


API_URL = "https://www.workingnomads.com/jobsapi/_search"
LOCATIONS = ["Anywhere", "Asia", "APAC", "Taiwan, Province of China"]
URL_LOCATION = "taiwan,-province-of-china"

class WorkingNomadsScraper(BaseScraper):
    """Scraper for Working Nomads jobs"""
    def __init__(self):
        super().__init__(base_url=API_URL, name="WorkingNomads")
        self.locations = LOCATIONS

    def _build_api_payload(self, term):
        payload = {
            "track_total_hits": True,
            "from": 0,
            "size": 100,
            "_source": [
                "company", "company_slug", "category_name", "locations", "location_base",
                "salary_range", "salary_range_short", "number_of_applicants", "instructions",
                "id", "external_id", "slug", "title", "pub_date", "tags", "source",
                "apply_option", "apply_email", "apply_url", "premium", "expired",
                "use_ats", "position_type", "annual_salary_usd", "description"
            ],
            "sort": [
                {"premium": {"order": "desc"}},
                {"_score": {"order": "desc"}},
                {"pub_date": {"order": "desc"}}
            ],
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": f"\"{term}\"",
                            "fields": ["title^2", "description", "company"]
                        }
                    },
                    "filter": [
                        {"terms": {"locations": LOCATIONS}},
                        {"range": {"pub_date": {"gte": f"now-{self.since}d/d"}}}
                    ]
                }
            },
            "min_score": 2
        }

        return payload

    def extract_company(self, job_element: dict) -> str:
        return job_element.get("company", "unknown")

    def extract_title(self, job_element: dict) -> str:
        return job_element.get("title", 'unknown')

    def extract_url(self, job_element: dict) -> str:
        return job_element.get("apply_url")

    def extract_date_published(self, job_element:dict) -> str:
        publish_date = job_element["pub_date"]
        utc_publish_date = to_utc(publish_date)
        return datetime.strftime(utc_publish_date, "%Y-%m-%d")

    def extract_job_description(self, job_url: str) -> None:
        # The job description is included in the job details.
        # We don't need to fetch it from the job post URL
        pass

    def get_jobs(self, term: str) -> list:
        payload = self._build_api_payload(term)

        headers = {
            "Host": "www.workingnomads.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.workingnomads.com",
            "Connection": "keep-alive",
            "Referer": f"https://www.workingnomads.com/jobs?location={URL_LOCATION}&postedDate={self.since}&tag={term.replace(' ', '-')}",
            "Cookie": 'subscriber_source=""; subscriber_utm_source=""; subscriber_utm_medium=""; subscriber_utm_campaign=""',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        r = request("POST", url=self.base_url, json=payload, headers=headers)
        if r.status_code == 200:
            response = r.json()
            data = response["hits"]["hits"]
            jobs_list = [j["_source"] for j in data]
        else:
            print(f"Error: {r.status_code} - {r.text}")
            jobs_list = []

        for job in jobs_list:
            job_details = self._extract_job_details(job)

            # The job description is included in the job details
            description_html = job.get("description", "Unknown")
            soup = BeautifulSoup(description_html, "html.parser")
            description_text = soup.get_text(separator=" ", strip=True)
            job_details["description"] = description_text

            self.jobs.append(job_details)


def to_utc(date_str):
    """
    Converts an ISO 8601 date string to a UTC datetime object.

    Args:
        date_str (str): The date string in ISO 8601 format. Can include 'Z' to indicate UTC.

    Returns:
        datetime: A timezone-aware datetime object in UTC.

    Raises:
        ValueError: If the input string is not a valid ISO 8601 date.
    """

    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc)
