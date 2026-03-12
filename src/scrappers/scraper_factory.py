from .remoteok import RemoteOkScraper
from .remotive import RemotiveScraper
from .trulyremote import TrulyRemoteScraper
from .tw104 import Tw104Scraper
from .workingnomads import WorkingNomadsScraper
from .wwr import WwrScraper


def get_scraper(site_name: str):
    scrapers = {
        "104": Tw104Scraper,
        "remoteok": RemoteOkScraper,
        "remotive": RemotiveScraper,
        "trulyremote": TrulyRemoteScraper,
        "workingnomads": WorkingNomadsScraper,
        "weworkremotely": WwrScraper
    }

    scraper_class = scrapers.get(site_name.lower())
    if scraper_class is None:
        valid_options = list(scrapers.keys())
        raise ValueError(
            f"Unknown scraper '{site_name}'. Valid options: {valid_options}"
        )
    
    return scraper_class()

