from .remotive import RemotiveScraper


def get_scraper(site_name: str):
    scrapers = {
        "remotive": RemotiveScraper,
    }
    return scrapers.get(site_name.lower())()

