from datetime import datetime, timedelta

from src.scrappers.base_scraper import BaseScraper



class TestScraper(BaseScraper):
    def get_jobs(self, term: str) -> list:
        pass

    def extract_company(self, job_element):
        pass

    def extract_title(self, job_element):
        pass

    def extract_url(self, job_element):
        pass

    def extract_date_published(self, job_element):
        pass

    def extract_job_description(self, job_url):
        pass


def test_remove_duplicates_with_urls():
    """Test that remove_duplicates removes jobs with duplicate URLs."""

    # Setup
    scraper = TestScraper("https://example.com", "ExampleScraper")
    scraper.jobs = [
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": "2024-06-02"},
    ]

    # Exercise
    scraper.remove_duplicates()

    # Verify
    assert len(scraper.jobs) == 2
    assert scraper.jobs == [
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": "2024-06-02"},
    ]

def test_remove_duplicates_with_missing_urls():
    """Test that remove_duplicates remoces jobs with duplicate company + title"""

    # Setup
    scraper = TestScraper("https://example.com", "ExampleScraper")
    scraper.jobs = [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 1", "company": "Acme"},  # Duplicate
        {"url": "missing", "title": "Job 2", "company": "Acme"},       
    ]

    # Exercise
    scraper.remove_duplicates()

    # Verify
    assert len(scraper.jobs) == 2
    assert scraper.jobs == [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 2", "company": "Acme"},       
    ]

def test_remove_older_jobs():
    """ The _remove_older_jobs method should remove jobs older than the specified threshold
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
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": older_date},
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": recent_date1},
        {"company": "Initech", "title": "DevOps Engineer", "url": "https://example.com/job3", "date_published": recent_date2},
        {"company": "Umbrella Corp", "title": "Backend Developer", "url": "https://example.com/job4", "date_published": cutoff_date.strftime("%Y-%m-%d")},
    ]

    # Exercise
    scraper._remove_older_jobs(days_threshold=days_threshold)

    # Verify
    assert len(scraper.jobs) == 3
    assert scraper.jobs == [
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": recent_date1},
        {"company": "Initech", "title": "DevOps Engineer", "url": "https://example.com/job3", "date_published": recent_date2},
        {"company": "Umbrella Corp", "title": "Backend Developer", "url": "https://example.com/job4", "date_published": cutoff_date.strftime("%Y-%m-%d")},
    ]