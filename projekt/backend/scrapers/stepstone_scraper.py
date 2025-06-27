from projekt.backend.core.models import JobSource, SearchCriteria, JobDetailsScraped
from projekt.backend.core.config import app_config
from .request_base_scraper import RequestBaseScraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from typing import List
import re



class StepStoneScraper(RequestBaseScraper):

    def __init__(self):
        super().__init__("StepStone")
        self.config = app_config.site_configs[JobSource.STEPSTONE.value]
        self.base_url = self.config["base_url"]

    def build_search_url(self, search_criteria: SearchCriteria, page: int = 1) -> str:
        params = search_criteria.to_stepstone_params()

        job_title_encoded = quote_plus(params["jobTitle"])
        location_encoded = quote_plus(params["location"])

        search_path = self.config["search_url_template"].format(
            jobTitle=job_title_encoded,
            location=location_encoded,
            radius=params["radius"],
            discipline=params.get("discipline", ""),
            seite=page
        )

        return urljoin(self.base_url, search_path)

    def extract_job_urls(self, url: str) -> List[str]:
        html = self.get_html_content(url)
        soup = BeautifulSoup(html, "html.parser")
        cfg = self.config["job_url"]
        selector = cfg["selector"]
        attribute = cfg["attribute"]
        links = soup.select(selector)
        urls = {
            urljoin(self.base_url, a.get(attribute))
            for a in links
            if a.get(attribute)
        }
        return list(urls)

    def get_max_pages(self, url: str) -> int:
        html = self.get_html_content(url)
        soup = BeautifulSoup(html, "html.parser")
        selector = self.config["max_page_selector"]
        element = soup.select_one(selector)
        if not element:
            return 1
        numbers = re.findall(r"\d+", element.get_text(strip=True))
        return int(numbers[-1]) if numbers else 1

    def extract_job_details_scraped(self, job_url: str) -> JobDetailsScraped | None:
        if self.legit_job_counter >= app_config.scraping.max_jobs_to_prozess_session:
            if not self.close_client:
                self.close_client()
            return None
        try:
            html = self.get_html_content(job_url)
            soup = BeautifulSoup(html, "html.parser")

            title_el = soup.select_one(self.config["job_titel_selector"])
            title = title_el.get_text(strip=True) if title_el else "Titel nicht gefunden"

            content_el = soup.select_one(self.config["job_content_selector"])
            raw_text = ""
            if content_el:
                for tag in content_el(["script", "style"]):
                    tag.decompose()
                raw_text = content_el.get_text(strip=True)

            return JobDetailsScraped(
                title=title,
                raw_text=raw_text,
                url=job_url,
                source=JobSource.STEPSTONE
            )

        except Exception as e:
            return JobDetailsScraped(
                title="Fehler beim Extrahieren",
                raw_text=f"Konnte Details nicht extrahieren: {e}",
                url=job_url,
                source=JobSource.STEPSTONE
            )