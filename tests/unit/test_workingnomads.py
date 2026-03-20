"""Unit tests for src/scrapers/workingnomads.py."""

from unittest.mock import patch

import pytest

from src.scrapers.workingnomads import WorkingNomadsScraper
from tests.conftest import FakeResponse

# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

JOB_ELEMENT = {
    "company": "Acme Inc",
    "title": "Software Engineer",
    "apply_url": "https://workingnomads.com/jobs/123",
    "pub_date": "2024-06-01T00:00:00Z",
    "description": "<p>This is the job description.</p>",
}

API_RESPONSE = {"hits": {"hits": [{"_source": JOB_ELEMENT}]}}


@pytest.fixture
def scraper() -> WorkingNomadsScraper:
    """Provide a fresh WorkingNomadsScraper instance for each test."""
    return WorkingNomadsScraper()


# ---------------------------------------------------------------------------
# extract_company
# ---------------------------------------------------------------------------


def test_extract_company_returns_company_name(scraper):
    """extract_company should return the company field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company(JOB_ELEMENT)

    # Verify
    assert result == "Acme Inc"


def test_extract_company_returns_unknown_when_missing(scraper):
    """extract_company should return unknown when the company name is missing"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company({})

    # Verify
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_title
# ---------------------------------------------------------------------------


def test_extract_title_returns_title(scraper):
    """extract_title should return the job title"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title(JOB_ELEMENT)

    # Verify
    assert result == "Software Engineer"


# ---------------------------------------------------------------------------
# extract_url
# ---------------------------------------------------------------------------


def test_extract_url_returns_apply_url(scraper):
    """extract_url should return the job url"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url(JOB_ELEMENT)

    # Verify
    assert result == "https://workingnomads.com/jobs/123"


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_formats_date(scraper):
    """extract_date_published should return the formated date"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_date_published(JOB_ELEMENT)

    # Verify
    assert result == "2024-06-01"


# ---------------------------------------------------------------------------
# extract_job_description
# ---------------------------------------------------------------------------


def test_extract_job_description_raises_not_implemented(scraper):
    """WorkingNomads includes description in job details — method should not be
    called.
    """
    # Setup
    # No setup required

    # Exercise
    with pytest.raises(NotImplementedError):
        scraper.extract_job_description("https://workingnomads.com/jobs/123")


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return jobs with HTML description stripped to plain text."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=FakeResponse(API_RESPONSE)):
        jobs = scraper.get_jobs("python")

    # Verify
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    assert jobs[0]["company"] == "Acme Inc"
    # Description HTML should be stripped to plain text
    assert "<p>" not in jobs[0]["description"]
    assert "job description" in jobs[0]["description"]


def test_get_jobs_returns_empty_list_on_failed_request(scraper):
    """get_jobs should return an empty list when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        jobs = scraper.get_jobs("python")

    # Verify
    assert jobs == []
