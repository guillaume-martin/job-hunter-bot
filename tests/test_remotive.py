import pytest
from src.scrappers import remotive


def test_get_jobs_returns_list():
    """ The get_jobs method should return a list
    """
    
    # Setup
    term = 'test'

    # Exercise
    jobs = remotive.get_jobs(term)

    # Verify
    assert isinstance(jobs, list) 


def test_get_jobs_list_contains_dictionaries():
    """ The list returns by the get_jobs methods contains dictionaries
    """
    
    # Setup
    term = 'test'

    # Exercise
    jobs = remotive.get_jobs(term)
    for job in jobs:
        assert isinstance(job, dict)
