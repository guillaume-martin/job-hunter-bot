"""
Configuration class for job search parameters and settings.
"""

import os

class Config:
    # Searches are a list of tuples (search_term, category)
    # The categories are used in remotive.io
    SEARCHES = [
        "database",
        "dba",
        "postgresql",
        "sql",
        "python",
        "aws",
        "data analyst",
        "data engineer",
        "backend engineer",
        "cloud data engineer",
        "cloud engineer",
        "cloud solution architect",
        "database engineer",
        "database administrator",
        "database manager",
        "etl developer",
        "devops engineer",
        "data manager",
        "analytics engineer",
        "data software engineer",
        "data architect",
        "dataops",
        "solution architect",
        "it manager",
    ]

    SITES = [
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
    APPLY_THRESHOLD = 80    # Minimum job `match_score` (0-100) required to select a job for application.

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
