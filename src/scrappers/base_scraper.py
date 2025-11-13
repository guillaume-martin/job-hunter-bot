from abc import ABC, abstractmethod
import urllib.parse

class BaseScraper(ABC):
    def __init__(self, base_url, name):
        self.base_url = base_url
        self.name = name

    @abstractmethod
    def get_jobs(self, term):
        """Fetch and return jobs for a given serch term."""
        pass

    def _build_search_url(self, term):
        """Construct the search URL for the given term."""
        return f"{self.base_url}/search?query={urllib.parse.quote(term)}"

    def _extract_job_details(self, job_element):
        """Extract job details from a job element. To be implemented by subclasses."""
        return {
            "company": self.extract_company(job_element), 
            "title": self.extract_title(job_element),
            "url": self.extract_url(job_element),
            "date_published": self.extract_date_published(job_element)
        }

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


