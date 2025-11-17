from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class BaseScraper(ABC):
    def __init__(self, base_url, name):
        self.base_url = base_url
        self.name = name
        self.jobs = []

    @abstractmethod
    def get_jobs(self, term: str) -> list:
        """Fetch and return jobs for a given serch term."""
        pass

    def _build_search_url(self, term):
        """Construct the search URL for the given term."""
        raise NotImplementedError("This scrapper does not use URL based search.")

    def _build_api_payload(self, term):
        """Construct the API payload for the given term."""
        raise NotImplementedError("This scrapper does not use API based search.")

    def _extract_job_details(self, job_element):
        """Extract job details from a job element. To be implemented by subclasses."""
        return {
            "company": self.extract_company(job_element), 
            "title": self.extract_title(job_element),
            "url": self.extract_url(job_element),
            "date_published": self.extract_date_published(job_element)
        }
    
    def _remove_duplicates(self):
        """Removes duplicate jobs"""
        single_jobs = []
        for jobs in self.jobs:
            if jobs not in single_jobs:
                single_jobs.append(jobs)
        self.jobs = single_jobs

    def _remove_older_jobs(self, days_threshold: int) -> None:
        """Removes jobs older than the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        filtered_jobs = []
        for job in self.jobs:
            job_date = datetime.strptime(job['date_published'], "%Y-%m-%d")
            if job_date.date() >= cutoff_date.date():
                filtered_jobs.append(job)
        self.jobs = filtered_jobs

    @abstractmethod
    def extract_company(self, job_element):
        pass

    @abstractmethod
    def extract_title(self, job_element):
        pass

    @abstractmethod
    def extract_url(self, job_element):
        pass

    @abstractmethod
    def extract_date_published(self, job_element):
        pass


