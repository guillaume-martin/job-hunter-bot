
"""Module for scraping job listings from TrulyRemote API.

This module provides functions to query the TrulyRemote job listing API, filter jobs by search term and location,
and convert publish dates to UTC datetime objects.
"""
from datetime import datetime, timezone

from .base_scraper import BaseScraper

from requests import request


API_URL = "https://trulyremote.co/api/getListing"
LOCATIONS = ["Anywhere in the world","Asia"]


class TrulyRemoteScraper(BaseScraper):
    """ Scraper for trulyremote.co jobs """
    def __init__(self):
        super().__init__(base_url=API_URL, name="TrulyRemote")
        self.locations = LOCATIONS

    def _build_api_payload(self, term):
        payload = {"term": term, "locations": LOCATIONS}

        return payload

    def extract_company(self, job_element):
        return job_element.get("companyName", ["unknown"][0])

    def extract_title(self, job_element):
        return job_element.get("role", "unknown")

    def extract_url(self, job_element):
        return job_element.get("roleApplyURL", "unknown") 

    def extract_date_published(self, job_element):
        # Sometimes job posts don't have a publish date, use last modified date instead
        try:
            publish_date = job_element["publishDate"]
        except KeyError:
            publish_date = job_element.get("lastModifiedOn")
        utc_publish_date = to_utc(publish_date)
        return datetime.strftime(utc_publish_date, "%Y-%m-%d")

    def get_jobs(self, term:str) -> list:
        payload = self._build_api_payload(term)

        r = request("POST", self.base_url, json=payload)
        if r.status_code == 200:
           response = r.json()
           jobs_list = response.get("records", [])
        else:
            print(f"Error: {r.status_code} - {r.text}")
            jobs_list = []
        
        for job in jobs_list:
            job_data = job["fields"]
            job_details = self._extract_job_details(job_data)
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

