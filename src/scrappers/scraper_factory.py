from .remotive import RemotiveScraper
from .trulyremote import TrulyRemoteScraper


def get_scraper(site_name: str):
    scrapers = {
        "remotive": RemotiveScraper,
        "trulyremote": TrulyRemoteScraper,
    }
    return scrapers.get(site_name.lower())()

