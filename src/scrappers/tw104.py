from urllib.parse import urlparse

from .base_scraper import BaseScraper

from requests import request


BASE_URL = "https://www.104.com.tw/jobs/search/api/jobs?"
RESULTS_PER_PAGE = 100



class Tw104Scraper(BaseScraper):
    """ Scraper for 104.com.tw jobs. """
    def __init__(self):
        super().__init__(base_url=BASE_URL, name="104")

    def _build_search_url(self, term):
        return f"{BASE_URL}jobsource=joblist_search&keyword={urllib.parse.quote(self.term)}&mode=s&order=15&page=1&page-size={RESULTS_PER_PAGE}&searchJobs=1"

    def extract_company(self, job_element):
        return job_element.get("custName", "unknown")
    
    def extract_title(self, job_element):
        return job_element.get("jobName", "unknown")
    
    def extract_url(self, job_element):
        return job_element.get("link", {}).get("job", "unknown")
    
    def extract_date_published(self, job_element):
        date_int = int(job_element.get("appearDate", 0))
        published_date = f"{date_int // 10000}-{(date_int // 100) % 100:02}-{date_int % 100:02}"
        return published_date
    
    def get_jobs(self, term:str) -> list:
        search_url = self._build_search_url(term) 

        headers = {
            "Host": "www.104.com.tw",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": f"https://www.104.com.tw/jobs/search/?jobsource=joblist_search&keyword={term.replace(" ", "+")}&mode=s&page=1&order=16",
        }
        
        r = request("GET", search_url, headers=headers)
        if r.status_code == 200:
            response = r.json()
            jobs_list = response.get("data", [])
            
            for job in jobs_list:
                job_details = self._extract_job_details(job)
                self.jobs.append(job_details)
