import pytest
import json
from unittest.mock import patch, MagicMock

from src.scrappers import remotive


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
    scraper = remotive.RemotiveScraper()

    # Exercise
    # Mock the request function to return a fake response
    with patch("src.scrappers.remotive.request") as mock_request:
        mock_response = MagicMock()
        mock_response.content = json.dumps(SAMPLE_RESPONSE).encode("utf-8")
        mock_request.return_value = mock_response

        jobs = scraper.get_jobs("python")

        # Verify
        # get_jobs() should return a list of 2 jobs
        assert isinstance(jobs, list)
        assert len(jobs) == 2


def test_get_jobs_list_contains_dictionaries():
    """ The list returns by the get_jobs methods contains dictionaries
    """

    # Setup
    scraper = remotive.RemotiveScraper()

    # Exercise
    with patch("scrappers.remotive.request") as mock_request:
        mock_response = MagicMock()
        mock_response.content = json.dumps(SAMPLE_RESPONSE).encode("utf-8")
        mock_request.return_value = mock_response

    jobs = scraper.get_jobs("python")

    # Verify
    for job in jobs:
        assert isinstance(job, dict)


