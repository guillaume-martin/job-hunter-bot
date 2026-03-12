from .remoteok import RemoteOkScraper
from .remotive import RemotiveScraper
from .trulyremote import TrulyRemoteScraper
from .tw104 import Tw104Scraper
from .wwr import WwrScraper
from .workingnomads import WorkingNomadsScraper

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
        raise ValueError(f"Unknown scraper '{site_name}'. Valid options: {list(scrapers.keys())}"))
    
    return scraper_class()

