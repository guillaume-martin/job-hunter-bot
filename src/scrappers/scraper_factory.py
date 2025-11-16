from .remoteok import RemoteOkScraper
from .remotive import RemotiveScraper
from .trulyremote import TrulyRemoteScraper
from .tw104 import Tw104Scraper

def get_scraper(site_name: str):
    scrapers = {
        "104": Tw104Scraper,
        "remoteok": RemoteOkScraper,
        "remotive": RemotiveScraper,
        "trulyremote": TrulyRemoteScraper,
    }
    return scrapers.get(site_name.lower())()

