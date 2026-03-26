import logging
from datetime import UTC, datetime
from typing import Any, cast

from bs4 import BeautifulSoup

from ..config import Config
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class WorkingNomadsScraper(BaseScraper):
    """Scraper for Working Nomads jobs"""

    def __init__(self):
        super().__init__(base_url=Config.WORKINGNOMADS_API_URL, name="WorkingNomads")
        _cfg = Config.scraper_config("workingnomads")
        self.locations: list[str] = _cfg.get("locations", ["Anywhere"])
        self.url_location: str = _cfg.get("url_location", "")
        self.since = Config.SINCE

    def _build_api_payload(self, term):
        payload = {
            "track_total_hits": True,
            "from": 0,
            "size": 100,
            "_source": [
                "company",
                "company_slug",
                "category_name",
                "locations",
                "location_base",
                "salary_range",
                "salary_range_short",
                "number_of_applicants",
                "instructions",
                "id",
                "external_id",
                "slug",
                "title",
                "pub_date",
                "tags",
                "source",
                "apply_option",
                "apply_email",
                "apply_url",
                "premium",
                "expired",
                "use_ats",
                "position_type",
                "annual_salary_usd",
                "description",
            ],
            "sort": [
                {"premium": {"order": "desc"}},
                {"_score": {"order": "desc"}},
                {"pub_date": {"order": "desc"}},
            ],
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": f'"{term}"',
                            "fields": ["title^2", "description", "company"],
                        }
                    },
                    "filter": [
                        {"terms": {"locations": self.locations}},
                        {"range": {"pub_date": {"gte": f"now-{self.since}d/d"}}},
                    ],
                }
            },
            "min_score": 2,
        }

        return payload

    def extract_company(self, job_element: dict) -> str:
        return cast(str, job_element.get("company", "unknown"))

    def extract_title(self, job_element: dict) -> str:
        return cast(str, job_element.get("title", "unknown"))

    def extract_url(self, job_element: dict) -> str:
        return cast(str, job_element.get("apply_url"))

    def extract_date_published(self, job_element: dict) -> str:
        publish_date = job_element["pub_date"]
        utc_publish_date = to_utc(publish_date)
        return datetime.strftime(utc_publish_date, "%Y-%m-%d")

    def extract_job_description(self, job_url: str) -> str:
        """Job description is included in job details. This method is not used."""
        raise NotImplementedError("Job description is included in job details.")

    def get_jobs(self, term: str) -> list[dict[str, Any]]:
        payload = self._build_api_payload(term)

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"
        )
        tag = term.replace(" ", "-")
        referer = (
            "https://www.workingnomads.com/jobs?"
            f"location={self.url_location}&"
            f"postedDate={self.since}&tag={tag}"
        )
        cookie = (
            'subscriber_source=""; '
            'subscriber_utm_source=""; '
            'subscriber_utm_medium=""; '
            'subscriber_utm_campaign=""'
        )
        headers = {
            "Host": "www.workingnomads.com",
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://www.workingnomads.com",
            "Connection": "keep-alive",
            "Referer": referer,
            "Cookie": cookie,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        r = self._request(
            method="POST", url=self.base_url, json=payload, headers=headers
        )

        if r is None:
            logger.error(f"Request failed for term: {term}.")
            return []

        response = r.json()

        try:
            data = response["hits"]["hits"]
            jobs_list = [j["_source"] for j in data]
        except (KeyError, ValueError) as e:
            logger.exception(f"Failed to parse response: {e}")
            jobs_list = []

        for job in jobs_list:
            job_details = self._extract_job_details(job)

            # The job description is included in the job details
            description_html = job.get("description", "Unknown")
            soup = BeautifulSoup(description_html, "html.parser")
            description_text = soup.get_text(separator=" ", strip=True)
            job_details["description"] = description_text

            self.jobs.append(job_details)

        return self.jobs


def to_utc(date_str):
    """
    Converts an ISO 8601 date string to a UTC datetime object.

    Args:
        date_str (str): The date string in ISO 8601 format. Can include 'Z'
        to indicate UTC.

    Returns:
        datetime: A timezone-aware datetime object in UTC.

    Raises:
        ValueError: If the input string is not a valid ISO 8601 date.
    """

    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.astimezone(UTC)
