import pytest
from src.job_search import jobs_to_html, filter_titles


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
    result = jobs_to_html(jobs)

    # Verify
    assert isinstance(result, str)


def test_filter_titles_returns_list():
    """ filer_titles should return a list """

    # Setup
    jobs = []
    searches = []

    # Exercise 
    result = filter_titles(jobs, searches)

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
    result = filter_titles(jobs, searches)

    # Verify
    result = [job_1]