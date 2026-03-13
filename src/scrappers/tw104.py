import logging
import urllib
from typing import Any

from .base_scraper import BaseScraper

BASE_URL = "https://www.104.com.tw/jobs/search/api/jobs?"
RESULTS_PER_PAGE = 100

logger = logging.getLogger(__name__)

class Tw104Scraper(BaseScraper):
    """ Scraper for 104.com.tw jobs. """
    def __init__(self):
        super().__init__(base_url=BASE_URL, name="104")

    def _build_search_url(self, term):
        keyword = urllib.parse.quote(term)
        return (
            f"{BASE_URL}jobsource=joblist_search&keyword={keyword}&mode=s&"
            f"order=15&page=1&page-size={RESULTS_PER_PAGE}&searchJobs=1"
        )

    def extract_company(self, job_element):
        return job_element.get("custName", "unknown")

    def extract_title(self, job_element):
        return job_element.get("jobName", "unknown")

    def extract_url(self, job_element):
        return job_element.get("link", {}).get("job", "unknown")

    def extract_date_published(self, job_element):
        date_int = int(job_element.get("appearDate", 0))
        published_date = (
            f"{date_int // 10000}-{(date_int // 100) % 100:02}-{date_int % 100:02}"
        )
        return published_date

    def get_jobs(self, term:str) -> list[dict[str, Any]]:
        existing_job_ids = self._get_existing_job_ids()
        search_url = self._build_search_url(term)

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"
        )
        keyword = term.replace(" ", "+")
        referer = (
            "https://www.104.com.tw/jobs/search/?"
            f"jobsource=joblist_search&keyword={keyword}&mode=s&page=1&order=16"
        )
        headers = {
            "Host": "www.104.com.tw",
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": referer,
        }

        new_jobs = set()    # Use a set to avoid duplicates

        r = self._request(method="GET", url=search_url, headers=headers)
        if r:
            response = r.json()
            jobs_list = response.get("data", [])

            for job in jobs_list:
                job_details = self._extract_job_details(job)
                job_url = job_details.get("url", "unknown")
                job_id = job_url.split("/")[-1]
                if job_id not in existing_job_ids:
                    self.jobs.append(job_details)
                    new_jobs.add(job_id)


        self._store_new_jobs(new_jobs)

        return self.jobs

    def extract_job_description(self, job_url: str) -> str:
        translation_table = str.maketrans({
            "\n": " ",
            "\r": " ",
            "\t": " "
        })

        # Get the job id from the job's URL
        job_id = job_url.split("/")[-1]

        request_url = f"https://www.104.com.tw/job/ajax/content/{job_id}"
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"
        )
        headers = {
            "Host": "www.104.com.tw",
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Referer": f"https://www.104.com.tw/job/{job_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        try:
            r = self._request(method="GET", url=request_url, headers=headers)

            if r:
                data = r.json()["data"]
                job_description: str = data["jobDetail"]["jobDescription"]
                description = job_description.translate(translation_table).strip()
            else:
                logger.error(f"Failed to fetch job description for {job_url}")
                description = "No description available"
        except Exception as e:
            logger.exception(
                f"Failed to extract job description for {request_url}: {e}"
            )
            description = "No description available"
        return description
