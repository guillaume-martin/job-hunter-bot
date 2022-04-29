import pytest
from src.job_search import jobs_to_html


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