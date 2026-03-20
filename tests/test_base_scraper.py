from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import NoCredentialsError
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout

from src.scrappers.base_scraper import BaseScraper


class TestScraper(BaseScraper):
    """Minimal concrete subclass of BaseScraper for testing.

    All abstract methods return empty/default values so tests can
    instantiate BaseScraper without triggering TypeError.
    """

    def get_jobs(self, term: str) -> list:
        return []

    def extract_company(self, job_element) -> str:
        return ""

    def extract_title(self, job_element) -> str:
        return ""

    def extract_url(self, job_element) -> str:
        return ""

    def extract_date_published(self, job_element) -> str:
        return ""

    def extract_job_description(self, job_url: str) -> str:
        return ""


@pytest.fixture
def scraper() -> TestScraper:
    """Provide a fresh TestScraper instance for each test."""
    return TestScraper("https://example.com", "ExampleScraper")


# ---------------------------------------------------------------------------
# remove_older_jobs
# ---------------------------------------------------------------------------


def test_remove_older_jobs(scraper):
    """The remove_older_jobs method should remove jobs older than the specified
    threshold
    """

    # Setup
    days_threshold = 5
    today = datetime.now()
    cutoff_date = today - timedelta(days=days_threshold)
    older_date = (cutoff_date - timedelta(days=1)).strftime("%Y-%m-%d")
    recent_date1 = (cutoff_date + timedelta(days=1)).strftime("%Y-%m-%d")
    recent_date2 = today.strftime("%Y-%m-%d")

    scraper.jobs = [
        {
            "company": "Acme Inc",
            "title": "Software Engineer",
            "url": "https://example.com/job1",
            "date_published": older_date,
        },
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": recent_date1,
        },
        {
            "company": "Initech",
            "title": "DevOps Engineer",
            "url": "https://example.com/job3",
            "date_published": recent_date2,
        },
        {
            "company": "Umbrella Corp",
            "title": "Backend Developer",
            "url": "https://example.com/job4",
            "date_published": cutoff_date.strftime("%Y-%m-%d"),
        },
    ]

    # Exercise
    scraper.remove_older_jobs(days_threshold=days_threshold)

    # Verify
    assert len(scraper.jobs) == 3
    assert scraper.jobs == [
        {
            "company": "Globex Corp",
            "title": "Data Scientist",
            "url": "https://example.com/job2",
            "date_published": recent_date1,
        },
        {
            "company": "Initech",
            "title": "DevOps Engineer",
            "url": "https://example.com/job3",
            "date_published": recent_date2,
        },
        {
            "company": "Umbrella Corp",
            "title": "Backend Developer",
            "url": "https://example.com/job4",
            "date_published": cutoff_date.strftime("%Y-%m-%d"),
        },
    ]


def test_remove_older_jobs_empty_list(scraper):
    """remove_older_jobs on an empty list should leave the list empty."""
    # Setup
    scraper.jobs = []

    # Exercise
    scraper.remove_older_jobs(days_threshold=5)

    # Verify
    assert scraper.jobs == []


def test_remove_older_jobs_all_olds(scraper):
    """remove_older_jobs should return an empty list when all jobs are too old."""
    # Setup
    old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    scraper.jobs = [
        {"title": "Old Job 1", "date_published": old_date},
        {"title": "Old Job 2", "date_published": old_date},
    ]

    # Exercise
    scraper.remove_older_jobs(days_threshold=5)

    # Verify
    assert scraper.jobs == []


def test_remove_older_jobs_all_recent(scraper):
    """remove_older_jobs should keep all jobs when none exceed the threshold."""
    # Setup
    today = datetime.now().strftime("%Y-%m-%d")
    scraper.jobs = [
        {"title": "Job 1", "date_published": today},
        {"title": "Job 2", "date_published": today},
    ]

    # Exercise
    scraper.remove_older_jobs(days_threshold=5)

    # Verify
    assert len(scraper.jobs) == 2


# ---------------------------------------------------------------------------
# _request
# ---------------------------------------------------------------------------


def test_request_returns_response_on_success(scraper):
    """_request should return the response object on a successful call."""

    # Setup
    class FakeResponse:
        """Test double for a requests.Response object.

        Implements only the attributes and methods _request actually calls:
        - raise_for_status() — called after every request to check for HTTP errors
        - status_code — used by callers to inspect the response
        """

        status_code = 200

        def raise_for_status(self) -> None:
            pass

    fake_response = FakeResponse()

    # Exercise
    with patch("src.scrappers.base_scraper.request", return_value=fake_response):
        result = scraper._request(url="https://example.com")

    # Verify
    assert result == fake_response
    assert result.status_code == 200


def test_request_returns_none_after_all_retries_fail(scraper, monkeypatch):
    """_request should return None when all retru attempts are exhausted."""
    # Setup
    monkeypatch.setattr("src.scrappers.base_scraper.Config.REQUEST_RETRIES", 2)

    # Exercise
    with (
        patch(
            "src.scrappers.base_scraper.request",
            side_effect=RequestsConnectionError("fail"),
        ),
        patch("src.scrappers.base_scraper.time.sleep"),
    ):
        result = scraper._request(url="https://example.com")

    # Verify
    assert result is None


def test_request_retries_on_timeout(scraper, monkeypatch):
    """_request should retry on Timeout and eventually return None."""
    # Setup
    monkeypatch.setattr("src.scrappers.base_scraper.Config.REQUEST_RETRIES", 3)
    mock_request = MagicMock(side_effect=Timeout("timed out"))

    # Exercise
    with (
        patch("src.scrappers.base_scraper.request", mock_request),
        patch("src.scrappers.base_scraper.time.sleep"),
    ):
        result = scraper._request(url="https://example.com")

    # Verify
    assert result is None
    assert mock_request.call_count == 3  # retried exactly REQUEST_RETRIES times


# ---------------------------------------------------------------------------
# _connect_dynamodb_table
# ---------------------------------------------------------------------------


def test_connect_dynamodb_table_raises_on_empty_name(scraper):
    """_connect_dynamodb_table should raise ValueError for an empty table name."""
    # Setup
    # No Setup needed

    # Exercise
    with pytest.raises(ValueError, match="Table name cannot be empty"):
        scraper._connect_dynamodb_table("")


def test_connect_dynamodb_table_raises_on_no_credentials(scraper):
    """_connect_dynamodb_table should raise ValueError when AWS credentials
    are missing.
    """
    # Setup
    # No Setup needed

    # Exercise
    with patch("boto3.resource", side_effect=NoCredentialsError()):
        with pytest.raises(ValueError, match="AWS credentials not configured"):
            scraper._connect_dynamodb_table("my-table")


def test_connect_dynamodb_table_returns_table_on_success(scraper):
    """_connect_dynamodb_table should return a DynamoDB Table resource."""
    # Setup
    mock_table = MagicMock()
    mock_ddb = MagicMock()
    mock_ddb.Table.return_value = mock_table

    # Exercise
    with patch("boto3.resource", return_value=mock_ddb):
        result = scraper._connect_dynamodb_table("my-table")

    # Verify
    assert result == mock_table
