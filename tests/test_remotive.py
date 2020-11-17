import pytest
import remotive


def test_get_jobs_returns_dictionary():

    # Setup
    term = 'test'
    category = 'Data'

    # Exercise
    jobs = remotive.get_jobs(term, category)

    # Verify
    assert isinstance(jobs, dict) 