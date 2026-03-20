"""Unit tests for src/scrapers/remotive.py.

Run with:
    pytest tests/test_remotive.py -v
"""

from unittest.mock import patch

import pytest

from src.scrapers.remotive import RemotiveScraper
from tests.conftest import FakeResponse

# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

JOB_ELEMENT = {
    "company_name": "Acme Inc",
    "title": "Software Engineer",
    "url": "https://remotive.com/job/123",
    "publication_date": 1717200000,  # 2024-06-01 as Unix timestamp
}

JOB_DESCRIPTION_HTML = """
<html>
    <body>
        <div class="left">This is the job description.</div>
    </body>
</html>
"""

API_RESPONSE = {"results": [{"hits": [JOB_ELEMENT]}]}


@pytest.fixture
def scraper() -> RemotiveScraper:
    """Provide a fresh RemotiveScraper instance for each test."""
    return RemotiveScraper()


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


def test_extract_title_returns_job_title(scraper):
    """extract_title should return the title field from the job dict."""
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


def test_extract_url_returns_url(scraper):
    """extract_url should return the url field from the job dict."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url(JOB_ELEMENT)

    # Verify
    assert result == "https://remotive.com/job/123"


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_formats_timestamp(scraper):
    """extract_date_published should convert a Unix timestamp to YYYY-MM-DD."""
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
    """extract_job_description should extract text from div.left."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(
        scraper, "_request", return_value=FakeResponse(JOB_DESCRIPTION_HTML)
    ):
        result = scraper.extract_job_description("https://remotive.com/job/123")

    # Verify
    assert isinstance(result, str)
    assert "job description" in result


def test_extract_job_description_strips_whitespace(scraper):
    """extract_job_description should remove \\n, \\r, and \\t characters."""
    # Setup
    html = "<html><body><div class='left'>Line1\nLine2\r\tEnd</div></body></html>"

    # Exercise
    with patch.object(scraper, "_request", return_value=FakeResponse(html)):
        result = scraper.extract_job_description("https://remotive.com/job/123")

    # Verify
    assert "\n" not in result
    assert "\r" not in result
    assert "\t" not in result


def test_extract_job_description_returns_default_on_failed_request(scraper):
    """extract_job_description should return the default string when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        result = scraper.extract_job_description("https://remotive.com/job/123")

    # Verify
    assert result == "Request for job page failed."


def test_extract_job_description_returns_default_when_div_missing(scraper):
    """extract_job_description should return the default string when div.left is
    absent.
    """
    # Setup
    html = "<html><body><div class='other'>No description here.</div></body></html>"

    # Exercise
    with patch.object(scraper, "_request", return_value=FakeResponse(html)):
        result = scraper.extract_job_description("https://remotive.com/job/123")

    # Verify
    assert result == "Description div not found in job page."


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return a list of job dicts parsed from the API response."""
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
