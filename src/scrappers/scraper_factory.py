from typing import Any, cast

from .base_scraper import BaseScraper
from .remoteok import RemoteOkScraper
from .remotive import RemotiveScraper
from .trulyremote import TrulyRemoteScraper
from .tw104 import Tw104Scraper
from .workingnomads import WorkingNomadsScraper
from .wwr import WwrScraper


def get_scraper(site_name: str) -> BaseScraper:
    """Return an instantiated scraper for the given site name.

    Args:
        site_name: Case-insensitive name of the job board to scrape.

    Returns:
        An instance of the appropriate BaseScraper subclass.

    Raises:
        ValueError: If site_name does not match any registered scraper.
    """
    scrapers: dict[str, Any] = {
        "104": Tw104Scraper,
        "remoteok": RemoteOkScraper,
        "remotive": RemotiveScraper,
        "trulyremote": TrulyRemoteScraper,
        "workingnomads": WorkingNomadsScraper,
        "weworkremotely": WwrScraper,
    }

    scraper_class = scrapers.get(site_name.lower())

    if scraper_class is None:
        valid_options = list(scrapers.keys())
        raise ValueError(
            f"Unknown scraper '{site_name}'. Valid options: {valid_options}"
        )

    return cast(BaseScraper, scraper_class())
