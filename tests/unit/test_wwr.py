"""Unit tests for src/scrapers/wwr.py."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scrapers.wwr import WwrScraper

# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

WWR_JOB_LISTING_HTML = """
<html>
    <body>
        <ul>
            <li class="feature">
                <div>
                    <p class="new-listing__company-name">Acme Inc</p>
                    <h4 class="new-listing__header__title">Software Engineer</h4>
                    <a href="/remote-jobs/123">Apply</a>
                    <p class="new-listing__header__icons__date">3 days</p>
                </div>
            </li>
        </ul>
    </body>
</html>
"""

WWR_JOB_DESCRIPTION_HTML = """
<html>
    <body>
        <div class="lis-container__job__content">This is the job description.</div>
    </body>
</html>
"""

WWR_JOB_NEW_DATE_HTML = """
<html>
    <body>
        <li class="feature">
            <p class="new-listing__company-name">Acme Inc</p>
            <h4 class="new-listing__header__title">Software Engineer</h4>
            <a href="/remote-jobs/456">Apply</a>
            <p class="new-listing__header__icons__date">New</p>
        </li>
    </body>
</html>
"""


@pytest.fixture
def scraper() -> WwrScraper:
    """Provide a fresh WwrScraper instance for each test."""
    return WwrScraper()


@pytest.fixture
def job_element(scraper):
    """Provide a parsed BS4 job element for extraction tests."""
    soup = BeautifulSoup(WWR_JOB_LISTING_HTML, "html.parser")
    return soup.find("li", class_="feature")


# ---------------------------------------------------------------------------
# extract_company
# ---------------------------------------------------------------------------


def test_extract_company_returns_company_name(scraper, job_element):
    """extract_company should return the company name"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_company(job_element)

    # Verify
    assert result == "Acme Inc"


# ---------------------------------------------------------------------------
# extract_title
# ---------------------------------------------------------------------------


def test_extract_title_returns_job_title(scraper, job_element):
    """extract_title should return the job title"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_title(job_element)

    # Verify
    assert result == "Software Engineer"


# ---------------------------------------------------------------------------
# extract_url
# ---------------------------------------------------------------------------


def test_extract_url_returns_full_url(scraper, job_element):
    """extract_url should return the full url to the job page"""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_url(job_element)

    # Verify
    assert result.startswith("https://")
    assert "/remote-jobs/123" in result


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_calculates_days_ago(scraper, job_element):
    """extract_date_published should subtract days from today for 'X days' text."""
    # Setup
    # No setup required

    # Exercise
    result = scraper.extract_date_published(job_element)

    # Verify
    expected = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    assert result == expected


def test_extract_date_published_handles_new_label(scraper):
    """extract_date_published should return today's date when the label is 'New'."""
    # Setup
    soup = BeautifulSoup(WWR_JOB_NEW_DATE_HTML, "html.parser")
    job_element = soup.find("li", class_="feature")

    # Exercise
    result = scraper.extract_date_published(job_element)

    # Verify
    assert result == datetime.now().strftime("%Y-%m-%d")


def test_extract_date_published_returns_today_when_no_date_tag(scraper):
    """extract_date_published should return today's date when the date tag is
    absent.
    """
    # Setup
    html = "<li class='feature'><h4 class='new-listing__header__title'>Job</h4></li>"
    soup = BeautifulSoup(html, "html.parser")
    job_element = soup.find("li", class_="feature")

    # Exercise
    result = scraper.extract_date_published(job_element)

    # Verify
    assert result == datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# extract_job_description
# ---------------------------------------------------------------------------


def test_extract_job_description_returns_text(scraper):
    """extract_job_description should extract text using Selenium page source."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(
        scraper, "_retrieve_html_content", return_value=WWR_JOB_DESCRIPTION_HTML
    ):
        result = scraper.extract_job_description("https://weworkremotely.com/job/123")

    # Verify
    assert isinstance(result, str)
    assert "job description" in result


def test_extract_job_description_returns_default_when_div_missing(scraper):
    """extract_job_description should return default string when description div
    is absent.
    """
    # Setup
    html = "<html><body><div class='other'>Nothing here.</div></body></html>"

    # Exercise
    with patch.object(scraper, "_retrieve_html_content", return_value=html):
        result = scraper.extract_job_description("https://weworkremotely.com/job/123")

    # Verify
    assert result == "Description div not found in job page."


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return a list of job dicts from the scraped page."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(
        scraper, "_retrieve_html_content", return_value=WWR_JOB_LISTING_HTML
    ):
        jobs = scraper.get_jobs("python")

    # Verify
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    assert jobs[0]["company"] == "Acme Inc"


def test_get_jobs_returns_empty_list_when_no_jobs_found(scraper):
    """get_jobs should return an empty list when the page has no job listings."""
    # Setup
    empty_html = "<html><body><ul></ul></body></html>"

    # Exercise
    with patch.object(scraper, "_retrieve_html_content", return_value=empty_html):
        jobs = scraper.get_jobs("python")

    # Verify
    assert jobs == []
