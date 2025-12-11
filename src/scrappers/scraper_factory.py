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
    return scrapers.get(site_name.lower())()

