from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any

class BaseScraper(ABC):
    def __init__(self, base_url: str, name: str):
        self.base_url = base_url
        self.name = name
        self.jobs = []

    @abstractmethod
    def get_jobs(self, term: str) -> List[Dict[str, Any]]:
        """Fetch and return jobs for a given serch term."""
        pass

    def remove_older_jobs(self, days_threshold: int) -> None:
        """Removes jobs older than the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        filtered_jobs = []
        for job in self.jobs:
            job_date = datetime.strptime(job['date_published'], "%Y-%m-%d")
            if job_date.date() >= cutoff_date.date():
                filtered_jobs.append(job)
        self.jobs = filtered_jobs

    def _extract_job_details(self, job_element) -> Dict[str, Any]:
        """Extract job details from a job element. To be implemented by subclasses."""
        return {
            "company": self.extract_company(job_element), 
            "title": self.extract_title(job_element),
            "url": self.extract_url(job_element),
            "date_published": self.extract_date_published(job_element)
        }

    def _build_search_url(self, term: str) -> str:
        """Construct the search URL for the given term."""
        raise NotImplementedError("This scrapper does not use URL based search.")

    def _build_api_payload(self, term: str) -> dict:
        """Construct the API payload for the given term."""
        raise NotImplementedError("This scrapper does not use API based search.")
    
    @abstractmethod
    def extract_company(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_title(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_url(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_date_published(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_job_description(self, job_url: str) -> str:
        """Extract job description from the job URL."""
        pass

