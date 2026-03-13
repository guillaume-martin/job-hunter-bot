import argparse
import os
from unittest.mock import patch

import src.job_search as job_search


def test_remove_duplicates_with_urls():
    """Test that remove_duplicates removes jobs with duplicate URLs."""

    # Setup
    jobs = [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01"
        },
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01"
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": "2024-06-02"
        },
    ]

    # Exercise
    single_jobs_list = job_search.remove_duplicates(jobs)

    # Verify
    assert len(single_jobs_list) == 2
    assert single_jobs_list == [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": "2024-06-01"
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": "2024-06-02"
        },
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

        def remove_older_jobs(self, days_threshold):
            pass

    def fake_get_scraper(site):
        return FakeScraper(site)

    search = ["python", "sql"]

    # Patch job_search module-level symbols that find_jobs uses
    monkeypatch.setattr(job_search, "get_scraper", fake_get_scraper)
    monkeypatch.setattr(job_search, "sites", ["siteA", "siteB"])

    # Exercise
    job_search.find_jobs(searches=search)

    # Verify
    expected_calls = [(s, t) for t in search for s in job_search.sites]
    assert calls == expected_calls


# TODO test find_jobs returns expected results from scrapers


def test_find_jobs_create_file(tmp_path):
    """Test that job_search creates a file when the output is set to file"""

    # Setting
    output_file = tmp_path / "output.md"

    # Mock the jobs and other dependencies
    mock_jobs = [
        {
            "url": "https://example.com/job1",
            "title": "Job 1",
            "company": "Acme",
            "evaluation": {"match_score": "85/100", "missing_required": []}
        },
        {
            "url": "https://example.com/job2",
            "title": "Job 2",
            "company": "Acme",
            "evaluation": {"match_score": "75/100", "missing_required": ["Python"]}
        },
    ]

    # Mock functions
    with patch("src.job_search.find_jobs", return_value=mock_jobs), \
         patch("src.job_search.remove_duplicates", return_value=mock_jobs), \
         patch("src.job_search.select_jobs", return_value=(mock_jobs, [])), \
         patch(
             "argparse.ArgumentParser.parse_args",
             return_value=argparse.Namespace(output="file", file=str(output_file))
         ):

        # Exercise
        job_search.main()

    # Verify
    # Check that the file exists
    assert os.path.exists(output_file)

def test_job_to_markdown_return_string():
    """Test that file_to_markdown returns a file"""
    # Setup
    mock_jobs = [
        {
            "url": "https://example.com/job1",
            "title": "Job 1",
            "company": "Acme",
            "evaluation": {"match_score": "85/100", "missing_required": []}
        },
        {
            "url": "https://example.com/job2",
            "title": "Job 2",
            "company": "Acme",
            "evaluation": {"match_score": "75/100", "missing_required": ["Python"]}
        },
    ]

    # Exercise
    result = job_search.jobs_to_markdown(mock_jobs)

    # Verify
    assert isinstance(result, str)