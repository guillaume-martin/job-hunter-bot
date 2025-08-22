
"""Module for scraping job listings from TrulyRemote API.

This module provides functions to query the TrulyRemote job listing API, filter jobs by search term and location,
and convert publish dates to UTC datetime objects.

Functions:
    to_utc(date_str):
    request_jobs(endpoint: str, term: str, locations: List):
    get_jobs(term: str) -> List:
        Fetches job listings matching the given search term from the remote API and returns a list of job dictionaries.

Constants:
    API_URL (str): The endpoint URL for the TrulyRemote job listing API.
    LOCATIONS (List[str]): List of location filters for job search.

Dependencies:
    - requests
    - datetime
    ValueError: If date string is not a valid ISO 8601 format in to_utc().
"""
import requests
from datetime import datetime, timezone


API_URL = "https://trulyremote.co/api/getListing"
LOCATIONS = ["Anywhere in the world","Asia"]


def to_utc(date_str):
    """
    Converts an ISO 8601 date string to a UTC datetime object.

    Args:
        date_str (str): The date string in ISO 8601 format. Can include 'Z' to indicate UTC.

    Returns:
        datetime: A timezone-aware datetime object in UTC.

    Raises:
        ValueError: If the input string is not a valid ISO 8601 date.
    """

    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc)


def request_jobs(endpoint: str, term: str, locations: list):
    """
    Sends a POST request to the specified endpoint to retrieve job listings based on a search term and locations.

    Args:
        endpoint (str): The API endpoint URL to send the request to.
        term (str): The search term for job listings.
        locations (List): A list of locations to filter job listings.

    Returns:
        dict or None: The JSON response containing job listings if the request is successful, otherwise None.
    """

    payload = {"term": term, "locations": locations}
    r = requests.post(endpoint, json=payload)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error: {r.status_code} - {r.text}")
        return None
    


def get_jobs(term:str) -> list:
    """
    Fetches job listings matching the given search term from a remote API.
    Args:
        term (str): The search term to filter job listings.
    Returns:
        List[dict]: A list of dictionaries, each representing a job with the following keys:
            - 'title': The job title (str).
            - 'company': The company name (str).
            - 'url': The URL to apply for the job (str).
            - 'date_published': The UTC ISO formatted publish date (str).
    Notes:
        - If no jobs are found or the API request fails, an empty list is returned.
        - The function expects the API response to contain a "records" key with job entries.
    """

    jobs = []

    data = request_jobs(API_URL, term, LOCATIONS)
    if not data:
        return jobs
    
    jobs_list = data.get("records", [])
    for job in jobs_list:
        job_data = job["fields"]
 
        # Sometimes job posts don't have a publish date, use last modified date instead
        try:
            publish_date = job_data["publishDate"]
        except KeyError:
            publish_date = job_data.get("lastModifiedOn")
        utc_publish_date = to_utc(publish_date)
        
        jobs.append({
            "title": job_data.get("role", "unknown"),
            "company": job_data.get("companyName", ["unknown"][0]),
            "url": job_data.get("roleApplyURL", "unknown"),
            "date_published": utc_publish_date.isoformat()
        })
    
    return jobs