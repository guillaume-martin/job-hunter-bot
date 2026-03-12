import logging
import time
import urllib
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from ..config import Config
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class WwrScraper(BaseScraper):
    """Scraper for We Work Remotely"""
    def __init__(self):
        super().__init__(base_url=Config.WWR_BASE_URL, name="WeWorkRemotely")

    def _build_search_url(self, term):
        return Config.WWR_BASE_URL + "/remote-jobs/search" + f"?term={term}"
    
    def extract_company(self, job_element):
        return job_element.find('p', class_='new-listing__company-name').text

    def extract_title(self, job_element):
        try:
            title = job_element.find('h4', class_='new-listing__header__title').text
        except AttributeError:
            title = "Title Not Found"

        return title

    def extract_url(self, job_element):
        """ Extracts and returns the full URL to the job details page from a BeautifulSoup job element.
        Args:
            job (bs4.element.Tag): A BeautifulSoup tag representing a job listing, expected to contain anchor tags.
        Returns:
            str: The absolute URL to the job details page if found, otherwise an empty string.
        """

        links = job_element.find_all('a')
        try:
            url = Config.WWR_BASE_URL
            url += [link["href"] for link in links if link["href"].startswith("/remote-jobs/")][0]
            url = urllib.parse.urljoin(Config.WWR_BASE_URL, url)
        except IndexError:
            url = ""
            pass

        return url

    def extract_date_published(self, job_element):
        """ Extracts the publication date from a job listing element.

        Args:
            job (bs4.element.Tag): A BeautifulSoup Tag object representing a job listing.

        Returns:
                str: The formatted publication date as a string in 'YYYY-MM-DD' format.
        """

        date_tag = job_element.find('p', class_='new-listing__header__icons__date')
        
        if not date_tag:
            logger.warning("No date tag found. Assuming today's date.")
            return datetime.now().strftime('%Y-%m-%d')
        
        date_text = date_tag.text.strip()

        if date_text.lower() == "new":
            days_since_posted = 0
        else:
            # Remove non numeric characters
            days_str = ''.join(filter(str.isdigit, date_text))

            # if no digits are found, assume today's date
            if not days_str:
                logger.warning(f"Unexpected date text '{date_text}'. Assuming today's date.")
                days_since_posted = 0
            else:
                days_since_posted = int(days_str)

        date_published = datetime.now() - timedelta(days=days_since_posted)

        return date_published.strftime('%Y-%m-%d')

    def get_jobs(self, term: str) -> None:
        """
        Scrapes job listings from the WWR (We Work Remotely) website based on a search term and region.

        Args:
            term (str): The search keyword to filter job listings.
        """

        page_content = self._retrieve_html_content(self._build_search_url(term))
        soup = BeautifulSoup(page_content, "html.parser")
        jobs_list = soup.find_all('li', class_='feature')

        for job in jobs_list:
            self.jobs.append(self._extract_job_details(job))
    
    @staticmethod
    def _retrieve_html_content(url: str):
        """Extract source code of a web page from the url using Selenium.
        
        Args:
            url (str): The url of the web page to retrieve.

        Return:
            The source code of the page.
        """
        # Setup Firefox options
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.binary_location = Config.FIREFOX_PATH

        # Specify the path to Geckodriver if not in PATH
        service = Service(Config.GECKODRIVER_PATH)

        # Start a new browser session
        driver = webdriver.Firefox(service=service, options=firefox_options)

        try:
            driver.get(url)
            # Wait for the page to load
            time.sleep(5)
            page_content = driver.page_source
        except InvalidArgumentException as e:
            logger.exception(f"Failed to reach URL {url}: {e}")
            page_content = ""
        except TimeoutError:
            logger.exception("Loading took too much time!")
            page_content = ""
        finally:
            driver.quit()

        return page_content
    
    def extract_job_description(self, job_url:str) -> str:
        """Extract the job description from the job page.
        
        Args:
            job_url (str): The url of the job description.
        
        Return:
            The job description text.
        """
        translation_table = str.maketrans({
            "\n": " ",
            "\r": " ",
            "\t": " "
        })

        page_content = self._retrieve_html_content(job_url)

        soup = BeautifulSoup(page_content, "html.parser")
        try:
            description_div = soup.find_all("div", class_="lis-container__job__content")[0]
            job_description = description_div.text.translate(translation_table)
        except Exception as e:
            logger.exception(f"Failed to extract job description for {job_url}: {e}")
            job_description = "No description available"

        return job_description
