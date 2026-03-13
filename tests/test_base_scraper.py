from abc import abstractmethod
from datetime import datetime, timedelta

from src.scrappers.base_scraper import BaseScraper


class TestScraper(BaseScraper):
    @abstractmethod
    def get_jobs(self, term: str) -> list:
        pass

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

    @abstractmethod
    def extract_job_description(self, job_url):
        pass


def test_remove_older_jobs():
    """ The remove_older_jobs method should remove jobs older than the specified 
    threshold
    """

    # Setup
    days_threshold = 5
    today = datetime.now()
    cutoff_date = today - timedelta(days=days_threshold)
    older_date = (cutoff_date - timedelta(days=1)).strftime("%Y-%m-%d")
    recent_date1 = (cutoff_date + timedelta(days=1)).strftime("%Y-%m-%d")
    recent_date2 = today.strftime("%Y-%m-%d")

    scraper = TestScraper("https://example.com", "ExampleScraper")
    scraper.jobs = [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": older_date
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": recent_date1
        },
        {
            "company": "Initech",
            "title": "DevOps Engineer",
            "url": "https://example.com/job3",
            "date_published": recent_date2
        },
        {
            "company": "Umbrella Corp",
            "title": "Backend Developer",
            "url": "https://example.com/job4",
            "date_published": cutoff_date.strftime("%Y-%m-%d")
        },
    ]

    # Exercise
    scraper.remove_older_jobs(days_threshold=days_threshold)

    # Verify
    assert len(scraper.jobs) == 3
    assert scraper.jobs == [
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": recent_date1
        },
        {
            "company": "Initech",
            "title": "DevOps Engineer",
            "url": "https://example.com/job3",
            "date_published": recent_date2
        },
        {
            "company": "Umbrella Corp",
            "title": "Backend Developer",
            "url": "https://example.com/job4",
            "date_published": cutoff_date.strftime("%Y-%m-%d")
        },
    ]
