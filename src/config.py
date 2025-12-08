"""
Configuration class for job search parameters and settings.

Attributes:
    SEARCHES (list): List of search terms for job categories.
    SITES (list): List of job board sites to search.
    SINCE (int): Number of days since job was published to consider.
    API_URL (str): URL for AI API endpoint.
    MODEL (str): AI model name to use.
    TEMPERATURE (float): Temperature setting for AI model.
    TIMEOUT (int): Timeout in seconds for AI API requests.
    PROMPT_FILE (str): Path to file containing AI prompt template.
    RESUME_FILE (str): Path to file containing resume text.
    APPLY_THRESHOLD (int): Minimum match score (0-100) required to apply.
    OUTPUT_PATH (str): Path for output files.
    OUTPUT_FILE (str): Name of output file for job listings.
"""

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
        "solution architect"
    ]

    SITES = [
        # "104",
        # "remoteok",
        # "remotive",
        # "trulyremote"
        "workingnomads"
    ]

    # Number of days since the job was published
    # Older jobs are dropped.
    SINCE = 5

    # AI settings
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    MODEL = "mistral-small-latest"
    TEMPERATURE = 0.7
    TIMEOUT = 60
    PROMPT_FILE = "src/data/prompt.txt"
    RESUME_FILE = "src/data/resume.txt"
    APPLY_THRESHOLD = 50    # Minimum job `match_score` (0-100) required to select a job for application.

    # Output file settings
    OUTPUT_PATH = ""
    OUTPUT_FILE = "new-jobs.md"
