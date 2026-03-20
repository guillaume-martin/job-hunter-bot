"""Unit tests for src/scrapers/remoteok.py.

Run with:
    pytest tests/test_remoteok.py -v
"""

from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from src.scrapers.remoteok import RemoteOkScraper

# ---------------------------------------------------------------------------
# Sample HTML fixtures
# ---------------------------------------------------------------------------

HTML_JOB_DESCRIPTION = """
<html>
    <body>
        <div class="html">This is a job description. With newlines and tabs.</div>
    </body>
</html>
"""

MARKDOWN_JOB_DESCRIPTION = """
<html>
    <body>
        <div class="markdown">This is a job description. With carriage returns.</div>
    </body>
</html>
"""

NO_DESCRIPTION_HTML = """
<html>
    <body>
        <div class="other-class">No description here.</div>
    </body>
</html>
"""

JOB_LISTING_HTML = """
<html>
    <body>
        <table>
            <tr class="job">
                <td class="company">
                    <h3>Acme Inc</h3>
                </td>
                <td class="position">
                    <h2>Software Engineer</h2>
                </td>
                <td class="source">
                    <a href="/jobs/123">Apply</a>
                </td>
                <td class="time">
                    <time datetime="2024-06-01T00:00:00Z">June 1, 2024</time>
                </td>
            </tr>
        </table>
    </body>
</html>
"""


# ---------------------------------------------------------------------------
# Shared helpers and fixtures
# ---------------------------------------------------------------------------


class FakeResponse:
    """Test double for requests.Response.

    Accepts bytes or str content — BeautifulSoup handles both.
    Status code defaults to 200 to simulate a successful response.
    """

    def __init__(self, content: str, status_code: int = 200) -> None:
        self.content = content.encode("utf-8")
        self.status_code = status_code

    def raise_for_status(self) -> None:
        pass


def make_mock_request(content_map: dict):
    """Return a fake request function that routes URLs to HTML content.

    Args:
        content_map: Maps URL substrings to HTML response strings.

    Returns:
        A callable that accepts (method, url, ...) and returns a FakeResponse.
    """

    def _mock_request(method, url, **kwargs):  # FIX: args[0]=method, args[1]=url
        for url_fragment, content in content_map.items():
            if url_fragment in url:
                return FakeResponse(content)
        return FakeResponse(NO_DESCRIPTION_HTML)

    return _mock_request


@pytest.fixture
def scraper() -> RemoteOkScraper:
    """Provide a fresh RemoteOkScraper instance for each test."""
    return RemoteOkScraper()


# ---------------------------------------------------------------------------
# extract_job_description
# ---------------------------------------------------------------------------


def test_extract_job_description_from_html_div(scraper):
    """extract_job_description should extract text from div.html."""
    # Setup
    mock_request = make_mock_request({"html": HTML_JOB_DESCRIPTION})

    # Exercise
    with patch("src.scrapers.base_scraper.request", side_effect=mock_request):
        description = scraper.extract_job_description("https://remoteok.com/html-job")

    # Verify
    assert isinstance(description, str)
    assert "This is a job description." in description


def test_extract_job_description_from_markdown_div(scraper):
    """extract_job_description should extract text from div.markdown."""
    # Setup
    mock_request = make_mock_request({"markdown": MARKDOWN_JOB_DESCRIPTION})

    # Exercise
    with patch("src.scrapers.base_scraper.request", side_effect=mock_request):
        description = scraper.extract_job_description(
            "https://remoteok.com/markdown-job"
        )

    # Verify
    assert isinstance(description, str)
    assert "This is a job description." in description


def test_extract_job_description_no_description(scraper):
    """extract_job_description should return the default string when no div is found."""
    # Setup
    mock_request = make_mock_request({})

    # Exercise
    with patch("src.scrapers.base_scraper.request", side_effect=mock_request):
        description = scraper.extract_job_description("https://remoteok.com/no-desc")

    # Verify
    assert description == "No description available."


def test_extract_job_description_strips_whitespace_characters(scraper):
    """extract_job_description should remove \\n, \\r, and \\t from the result."""
    # Setup
    mock_request = make_mock_request({"html": HTML_JOB_DESCRIPTION})

    # Exercise
    with patch("src.scrapers.base_scraper.request", side_effect=mock_request):
        description = scraper.extract_job_description("https://remoteok.com/html-job")

    # Verify
    assert "\n" not in description
    assert "\r" not in description
    assert "\t" not in description


def test_extract_job_description_handles_failed_request(scraper):
    """extract_job_description should return the default string when _request
    fails.
    """
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        description = scraper.extract_job_description("https://remoteok.com/any-job")

    # Verify
    assert description == "No description available"


# ---------------------------------------------------------------------------
# extract_company
# ---------------------------------------------------------------------------


def test_extract_company_returns_company_name(scraper):
    """extract_company should return the cleaned company name from a job element."""
    # Setup
    soup = BeautifulSoup(JOB_LISTING_HTML, "lxml")
    job_element = soup.find("tr", class_="job")

    # Exercise
    result = scraper.extract_company(job_element)

    # Verify
    assert result == "Acme Inc"


# ---------------------------------------------------------------------------
# extract_title
# ---------------------------------------------------------------------------


def test_extract_title_returns_job_title(scraper):
    """extract_title should return the cleaned job title from a job element."""
    # Setup
    soup = BeautifulSoup(JOB_LISTING_HTML, "lxml")
    job_element = soup.find("tr", class_="job")

    # Exercise
    result = scraper.extract_title(job_element)

    # Verify
    assert result == "Software Engineer"


# ---------------------------------------------------------------------------
# extract_url
# ---------------------------------------------------------------------------


def test_extract_url_returns_full_url(scraper):
    """extract_url should return the full URL by prepending base_url to the href."""
    # Setup
    soup = BeautifulSoup(JOB_LISTING_HTML, "lxml")
    job_element = soup.find("tr", class_="job")

    # Exercise
    result = scraper.extract_url(job_element)

    # Verify
    assert result == "https://remoteok.com/jobs/123"


# ---------------------------------------------------------------------------
# extract_date_published
# ---------------------------------------------------------------------------


def test_extract_date_published_formats_date(scraper):
    """extract_date_published should return the date formatted as YYYY-MM-DD."""
    # Setup
    soup = BeautifulSoup(JOB_LISTING_HTML, "lxml")
    job_element = soup.find("tr", class_="job")

    # Exercise
    result = scraper.extract_date_published(job_element)

    # Verify
    assert result == "2024-06-01"


# ---------------------------------------------------------------------------
# get_jobs
# ---------------------------------------------------------------------------


def test_get_jobs_returns_list_of_jobs(scraper):
    """get_jobs should return a list of job dicts parsed from the search results."""
    # Setup
    mock_request = make_mock_request({"remoteok.com": JOB_LISTING_HTML})

    # Exercise
    with patch("src.scrapers.base_scraper.request", side_effect=mock_request):
        jobs = scraper.get_jobs("python")

    # Verify
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    assert jobs[0]["company"] == "Acme Inc"
    assert jobs[0]["url"] == "https://remoteok.com/jobs/123"
    assert jobs[0]["date_published"] == "2024-06-01"


def test_get_jobs_returns_empty_list_on_failed_request(scraper):
    """get_jobs should return an empty list when _request fails."""
    # Setup
    # No setup required

    # Exercise
    with patch.object(scraper, "_request", return_value=None):
        jobs = scraper.get_jobs("python")

    # Verify
    assert jobs == []
