"""Unit tests for src/scrappers/trulyremote.py."""

from unittest.mock import patch

import pytest

from src.scrappers.trulyremote import TrulyRemoteScraper, to_utc
from tests.conftest import FakeResponse

# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

JOB_ELEMENT = {
    "companyName": "Acme Inc",
    "role": "Software Engineer",
    "roleApplyURL": "https://trulyremote.co/job/123",
    "publishDate": "2024-06-01T00:00:00Z",
}

JOB_ELEMENT_NO_PUBLISH_DATE = {
    "companyName": "Acme Inc",
    "role": "Software Engineer",
    "roleApplyURL": "https://trulyremote.co/job/123",
    "lastModifiedOn": "2024-05-15T00:00:00Z",  # fallback field
}

JOB_DESCRIPTION_HTML = """
<html>
    <body>
        <div class="job__description">This is the job description.</div>
    </body>
</html>
"""

API_RESPONSE = {"records": [{"fields": JOB_ELEMENT}]}


@pytest.fixture
def scraper() -> TrulyRemoteScraper:
    """Provide a fresh TrulyRemoteScraper instance for each test."""
    return TrulyRemoteScraper()


# ---------------------------------------------------------------------------
# extract_company
# ---------------------------------------------------------------------------


def test_extract_company_returns_company_name(scraper):
    """extract_company should return the company_name field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company(JOB_ELEMENT)

    # Verify
    assert result == "Acme Inc"


def test_extract_company_returns_unknown_when_missing(scraper):
    """extract_company should return 'unknown' when company_name is absent."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company({})

    # Verify
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_title
# ---------------------------------------------------------------------------


def test_extract_title_returns_role(scraper):
    """extract_title should return the role field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title(JOB_ELEMENT)

    # Verify
    assert result == "Software Engineer"


def test_extract_title_returns_unknown_when_missing(scraper):
    """extract_title should return 'unknown' when title is absent."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title({})

    # Verify
    assert result == "unknown"


# ---------------------------------------------------------------------------
# extract_url
# ---------------------------------------------------------------------------


def test_extract_url_returns_apply_url(scraper):
    """extract_url should return the url field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url(JOB_ELEMENT)

    # Verify
    assert result == "https://trulyremote.co/job/123"


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_uses_publish_date(scraper):
    """extract_date_published should use publishDate when available."""
    assert scraper.extract_date_published(JOB_ELEMENT) == "2024-06-01"


def test_extract_date_published_falls_back_to_last_modified(scraper):
    """extract_date_published should fall back to lastModifiedOn when publishDate
    is absent.
    """
    assert scraper.extract_date_published(JOB_ELEMENT_NO_PUBLISH_DATE) == "2024-05-15"


# ---------------------------------------------------------------------------
# extract_job_description
# ---------------------------------------------------------------------------


def test_extract_job_description_returns_text(scraper):
    """extract_job_description should extract text from the description div."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(
        scraper, "_request", return_value=FakeResponse(JOB_DESCRIPTION_HTML)
    ):
        result = scraper.extract_job_description("https://trulyremote.co/job/123")

    # Verify
    assert isinstance(result, str)
    assert "job description" in result


def test_extract_job_description_returns_default_on_failed_request(scraper):
    """extract_job_description should return the default string when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        result = scraper.extract_job_description("https://trulyremote.co/job/123")

    # Verify
    assert result == "Request for job page failed."


def test_extract_job_description_returns_default_when_div_missing(scraper):
    """extract_job_description should return the default string when div.left is
    absent.
    """
    # Setup
    html = "<html><body><div class='other'>Nothing here.</div></body></html>"

    # Exercise
    with patch.object(scraper, "_request", return_value=FakeResponse(html)):
        result = scraper.extract_job_description("https://trulyremote.co/job/123")

    # Verify
    assert result == "Description div not found in job page."


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return a list of job dicts parsed from the response."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=FakeResponse(API_RESPONSE)):
        jobs = scraper.get_jobs("python")

    # Verify
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    assert jobs[0]["company"] == "Acme Inc"


def test_get_jobs_returns_empty_list_on_failed_request(scraper):
    """get_jobs should return an empty list when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        jobs = scraper.get_jobs("python")

    # Verify
    assert jobs == []


# ---------------------------------------------------------------------------
# to_utc helper
# ---------------------------------------------------------------------------


def test_to_utc_converts_z_suffix():
    """to_utc should handle ISO 8601 strings ending in Z."""
    # Setup
    # No setup required

    # Exercise
    result = to_utc("2024-06-01T00:00:00Z")

    # Verify
    assert result.year == 2024
    assert result.month == 6
    assert result.day == 1
