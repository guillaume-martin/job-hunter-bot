"""
Configuration class for job search parameters and settings.
"""

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_SEARCH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "search_config.yaml")


def _load_search_config() -> dict[str, Any]:
    """Load search configuration from YAML file with fallback to defaults."""
    if not os.path.isfile(_SEARCH_CONFIG_PATH):
        logger.warning(
            "Search config file not found at %s. Using defaults. "
            "Copy search_config.template.yaml to search_config.yaml to customize.",
            _SEARCH_CONFIG_PATH,
        )
        return {}
    try:
        with open(_SEARCH_CONFIG_PATH, encoding="utf-8") as f:
            config: dict = yaml.safe_load(f)
            if config is None:
                return {}
            return config
    except yaml.YAMLError as e:
        logger.error("Failed to parse %s: %s. Using defaults.", _SEARCH_CONFIG_PATH, e)
        return {}


_search_config = _load_search_config()


class Config:
    # ================================== #
    #      Infrastructure settings       #
    # ================================== #
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    JOBS_TABLE = os.environ["JOBS_TABLE"]
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))

    # ============================ #
    #      Search  settings        #
    # ============================ #
    # Search parameters (loaded from search_config.yaml)
    SEARCHES: list[str] = _search_config.get("searches", ["backend engineer"])
    SITES: list[str] = _search_config.get("sites", ["remotive"])
    SINCE: int = _search_config.get("since", 2)

    @staticmethod
    def scraper_config(scraper_name: str) -> dict[str, Any]:
        """Return per-scraper settings from search_config.yaml."""
        result: dict[str, Any] = _search_config.get(scraper_name, {})
        return result

    # Scrapers requests settings
    REQUEST_RETRIES = 3  # Number of retries when requests fail.
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
    OUTPUT_PATH = "output/"
    OUTPUT_FILE = "new-jobs.md"

    # ============================ #
    #      Scrapers settings       #
    # ============================ #

    # Working Nomads Settings
    WORKINGNOMADS_API_URL = "https://www.workingnomads.com/jobsapi/_search"

    # We Work Remotely Settings
    WWR_BASE_URL = "https://weworkremotely.com"

    # Remotive settings
    REMOTIVE_ALGOLIA_KEY = "8ad949132d497255ffc04accd141f083"
    REMOTIVE_ALGOLIA_ID = "OQUBRX6ZEQ"
