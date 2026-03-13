"""
Configuration class for job search parameters and settings.
"""

import os


class Config:
    # Searches are a list keywords searched on the job boards
    SEARCHES: list[str] = [

    ]

    # List of sites to search. They should match the names of the scrapers in 
    # `scraper_factory.py`
    SITES: list[str] = [
       "104",
       "remoteok",
       "remotive",
       "trulyremote",
       "workingnomads",
       "weworkremotely",
    ]

    # Number of days since the job was published
    # Older jobs are dropped.
    SINCE = 2

    # Scrapers requests settings
    REQUEST_RETRIES = 3     # Number of retries when requests fail.
    REQUEST_TIMEOUT = 60

    # AI settings
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    MODEL = "mistral-small-latest"
    TEMPERATURE = 0.7
    TIMEOUT = 60
    PROMPT_FILE = "src/data/prompt.txt"
    RESUME_FILE = "src/data/resume.txt"
    # Minimum job `match_score` (0-100) required to select a job for application.
    APPLY_THRESHOLD = 80

    # Output file settings
    OUTPUT_PATH = ""
    OUTPUT_FILE = "new-jobs.md"

    # ============================ #
    #      Scrapers settings       #
    # ============================ #

   # Selenium configuration
    FIREFOX_PATH = os.getenv("FIREFOX_PATH")
    GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH")

    # Working Nomads Settings
    WORKINGNOMADS_API_URL = "https://www.workingnomads.com/jobsapi/_search"
    WORKINGNOMADS_LOCATIONS = ["Anywhere", "Asia", "APAC", "Taiwan, Province of China"]
    WORKINGNOMADS_URL_LOCATION = "taiwan,-province-of-china"

    # We Work Remotely Settings
    WWR_BASE_URL = 'https://weworkremotely.com'
    WWR_REGION = "taiwan"

    # Remotive settings
    REMOTIVE_ALGOLIA_KEY = "8ad949132d497255ffc04accd141f083"
    REMOTIVE_ALGOLIA_ID = "OQUBRX6ZEQ"
