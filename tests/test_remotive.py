import pytest
import json
from unittest.mock import patch, MagicMock

from src.scrappers.remotive import RemotiveScraper


SAMPLE_RESPONSE = {
    "results": [
        {
            "hits": [
                {
                    "company_name": "Acme Inc",
                    "title": "Software Engineer",
                    "url": "https://example.com/job1",
                    "publication_date": 1634567890,
                },
                {
                    "company_name": "Globex Corp",
                    "title": "Data Scientist",
                    "url": "https://example.com/job2",
                    "publication_date": 1634567891,
                }
            ]
        }
    ]
}

def test_get_jobs_returns_list():
    """ The get_jobs method should return a list
    """

    # Setup
    scraper = RemotiveScraper()

    # Exercise
    # Mock the request function to return a fake response
    with patch("src.scrappers.remotive.request") as mock_request:
        mock_response = MagicMock()
        mock_response.content = json.dumps(SAMPLE_RESPONSE).encode("utf-8")
        mock_request.return_value = mock_response

        scraper.get_jobs("python")

        # Verify
        # get_jobs() should return a list of 2 jobs
        assert isinstance(scraper.jobs, list)
        assert len(scraper.jobs) == 2


def test_get_jobs_list_contains_dictionaries():
    """ The list returns by the get_jobs methods contains dictionaries
    """

    # Setup
    scraper = RemotiveScraper()

    # Exercise
    with patch("scrappers.remotive.request") as mock_request:
        mock_response = MagicMock()
        mock_response.content = json.dumps(SAMPLE_RESPONSE).encode("utf-8")
        mock_request.return_value = mock_response

    scraper.get_jobs("python")

    # Verify
    for job in scraper.jobs:
        assert isinstance(job, dict)


def test_extract_job_description_success():
    """Test that extract_job_description returns the job description when the request succeeds."""
    # Setup
    scraper = RemotiveScraper()

    # Mock a successful request with HTML content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <html>
        <body>
            <div class="left">Backend Engineer (Python, Django, PostgreSQL)</div>
        </body>
    </html>
    """

    with patch("requests.request", return_value=mock_response):
        # Exercise
        description = scraper.extract_job_description("http://example.com/job")

        # Verify
        assert description == "Backend Engineer (Python, Django, PostgreSQL)"

def test_extract_job_description_failure():
    """Test that extract_job_description returns 'No description available' when the request fails."""
    # Setup
    scraper = RemotiveScraper()

    # Mock a failed request
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("requests.request", return_value=mock_response):
        # Exercise
        description = scraper.extract_job_description("http://example.com/job")

        # Verify
        assert description == "No description available"

def test_extract_job_description_exception():
    """Test that extract_job_description returns 'No description available' when an exception occurs."""
    # Setup
    scraper = RemotiveScraper()

    # Exercise
    with patch("requests.request", side_effect=Exception("Network error")):
        description = scraper.extract_job_description("http://example.com/job")

        # Verify
        assert description == "No description available"