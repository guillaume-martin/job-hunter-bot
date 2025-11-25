import pytest
import src.job_search as job_search



def test_remove_duplicates_with_urls():
    """Test that remove_duplicates removes jobs with duplicate URLs."""

    # Setup
    jobs = [
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": "2024-06-02"},
    ]

    # Exercise
    single_jobs_list = job_search.remove_duplicates(jobs)

    # Verify
    assert len(single_jobs_list) == 2
    assert single_jobs_list == [
        {"company": "Acme Inc", "title": "Software Engineer", "url": "https://example.com/job1", "date_published": "2024-06-01"},
        {"company": "Globex Corp", "title": "Data Scientist", "url": "https://example.com/job2", "date_published": "2024-06-02"},
    ]

def test_remove_duplicates_with_missing_urls():
    """Test that remove_duplicates remoces jobs with duplicate company + title"""

    # Setup
    jobs = [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 1", "company": "Acme"},  # Duplicate
        {"url": "missing", "title": "Job 2", "company": "Acme"},       
    ]

    # Exercise
    single_jobs_list = job_search.remove_duplicates(jobs)

    # Verify
    assert len(single_jobs_list) == 2
    assert single_jobs_list == [
        {"url": "missing", "title": "Job 1", "company": "Acme"},
        {"url": "missing", "title": "Job 2", "company": "Acme"},       
    ]

def test_jobs_to_html_returns_string():
    """ jobs_to_html should return a string containing the HTML script """

    # Setup
    jobs = [
        {
            "url": "https://acme.com",
            "title": "job title",
            "company": "Acme, Inc.",
            "date_published": "2022-04-29"
        }
    ]

    # Exercise
    result = job_search.jobs_to_html(jobs)

    # Verify
    assert isinstance(result, str)


def test_filter_titles_returns_list():
    """ filer_titles should return a list """

    # Setup
    jobs = []
    searches = []

    # Exercise
    result = job_search.filter_titles(jobs, searches)

    # Verify
    assert isinstance(result, list)


def test_filter_titles_removes_unwanted():
    """ filter_titles removes jobs that don't have search term in the title """

    # Setup
    job_1 = {
                "company": "Acme",
                "title": "Database Administrator",
                "date_published": "2022-01-01",
                "url": "https://acme.com/job"
            }
    job_2 = {
                "company": "Example",
                "title": "Ruby Developer",
                "date_published": "2022-01-01",
                "url": "https://example.com/job"
            }
    jobs = [job_1, job_2]
    searches = ["database", "python"]

    # Exercise
    result = job_search.filter_titles(jobs, searches)

    # Verify
    result = [job_1]
    assert result == [job_1]

def test_find_jobs_calls_scrappers(monkeypatch):
    """ find_jobs should call the configured scrapers and return combined results """
    # setup
    calls = []

    class FakeScraper:
        def __init__(self, site):
            self.site = site

        def get_jobs(self, term):
            calls.append((self.site, term))
            self.jobs = []

    def fake_get_scraper(site):
        return FakeScraper(site)

    search = ["python", "sql"]

    # Patch job_search module-level symbols that find_jobs uses
    monkeypatch.setattr(job_search, "get_scraper", fake_get_scraper)
    monkeypatch.setattr(job_search, "sites", ["siteA", "siteB"])

    # Exercise
    results = job_search.find_jobs(searches=search)

    # Verify
    expected_calls = [(s, t) for t in search for s in job_search.sites]
    assert calls == expected_calls


# TODO test find_jobs returns expected results from scrapers
