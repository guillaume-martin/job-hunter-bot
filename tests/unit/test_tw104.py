"""Unit tests for src/scrappers/tw104.py.

Run with:
    pytest tests/test_remotive.py -v
"""

from unittest.mock import patch

import pytest

from src.scrappers.tw104 import Tw104Scraper
from tests.conftest import FakeResponse

# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

JOB_ELEMENT = {
    "custName": "Acme Inc",
    "jobName": "Software Engineer",
    "link": {"job": "https://www.104.com.tw/job/abc123"},
    "appearDate": 20240601,
}

API_RESPONSE = {"data": [JOB_ELEMENT]}

JOB_DESCRIPTION_RESPONSE = {
    "data": {"jobDetail": {"jobDescription": "This is the job description."}}
}


@pytest.fixture
def scraper() -> Tw104Scraper:
    """Provide a fresh Tw104Scraper instance for each test."""
    return Tw104Scraper()


# ---------------------------------------------------------------------------
# extract_company
# ---------------------------------------------------------------------------


def test_extract_company_returns_company_name(scraper):
    """extract_company should return the company name from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company(JOB_ELEMENT)

    # Verify
    assert result == "Acme Inc"


def test_extract_company_returns_unknown_when_missing(scraper):
    """extract_company should return 'unknown' when company name is absent."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company({})
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_title
# ---------------------------------------------------------------------------


def test_extract_title_returns_job_name(scraper):
    """extract_title should return job name from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title(JOB_ELEMENT)

    # Verify
    assert result == "Software Engineer"


def test_extract_title_returns_unknown_when_missing(scraper):
    """extract_title should return unknow when the job name is missing"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title({})

    # Verify
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_url
# ---------------------------------------------------------------------------


def test_extract_url_returns_job_link(scraper):
    """extract_url should return the url field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url(JOB_ELEMENT)

    # Verify
    assert result == "https://www.104.com.tw/job/abc123"


def test_extract_url_returns_unknown_when_missing(scraper):
    """extract_url should return unknown when the url is missing"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url({})

    # Verify
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_formats_integer_date(scraper):
    """extract_date_published should convert integer YYYYMMDD to YYYY-MM-DD string."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_date_published(JOB_ELEMENT)

    # Verify
    assert result == "2024-06-01"


# ---------------------------------------------------------------------------
# extract_job_description
# ---------------------------------------------------------------------------


def test_extract_job_description_returns_text(scraper):
    """extract_job_description should extract text from the 104 JSON API response."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(
        scraper, "_request", return_value=FakeResponse(JOB_DESCRIPTION_RESPONSE)
    ):
        result = scraper.extract_job_description("https://www.104.com.tw/job/abc123")

    # Verify
    assert isinstance(result, str)
    assert "job description" in result


def test_extract_job_description_returns_default_on_failed_request(scraper):
    """extract_job_description should return the default string when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        result = scraper.extract_job_description("https://www.104.com.tw/job/abc123")

    # Verify
    assert result == "Request for job page failed."


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return new jobs not already in DynamoDB."""
    # Setup
    # No setup required

    # Exercise
    with (
        patch.object(scraper, "_request", return_value=FakeResponse(API_RESPONSE)),
        patch.object(scraper, "_get_existing_job_ids", return_value=set()),
        patch.object(scraper, "_store_new_jobs"),
    ):
        jobs = scraper.get_jobs("python")

    # Verify
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"


def test_get_jobs_skips_existing_job_ids(scraper):
    """get_jobs should skip jobs whose IDs are already in DynamoDB."""
    # Setup
    # No setup required

    # Exercise
    with (
        patch.object(scraper, "_request", return_value=FakeResponse(API_RESPONSE)),
        patch.object(scraper, "_get_existing_job_ids", return_value={"abc123"}),
        patch.object(scraper, "_store_new_jobs"),
    ):
        jobs = scraper.get_jobs("python")

    # Verify
    # Job ID "abc123" already exists — should be skipped
    assert jobs == []


def test_get_jobs_returns_empty_list_on_failed_request(scraper):
    """get_jobs shoud return an empty list when the request fails."""
    # Setup
    # No setup required

    # Exercise
    with (
        patch.object(scraper, "_request", return_value=None),
        patch.object(scraper, "_get_existing_job_ids", return_value=set()),
        patch.object(scraper, "_store_new_jobs"),
    ):
        jobs = scraper.get_jobs("python")

    # Verify
    assert jobs == []
