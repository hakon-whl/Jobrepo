# xing_scraper.py
from typing import List, Optional
from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource
from projekt.backend.core.config import app_config
import logging

logger = logging.getLogger(__name__)


class XingScraper(SeleniumBaseScraper):
    """XING Job-Scraper mit angepassten Konfigurationen"""

    def __init__(self):
        super().__init__("Xing")
        self.max_jobs_limit = getattr(app_config.scraping, 'max_total_jobs_per_site', 100)

    def get_search_result_urls(self, search_criteria: SearchCriteria) -> List[str]:
        """Sammelt Job-URLs von der XING-Suchseite"""
        try:
            self.open_client()
            if not self.driver:
                logger.error("XING Client konnte nicht geöffnet werden")
                return []

            search_url = self._construct_search_url(
                self.config.get("search_url_template"),
                search_criteria.to_xing_params()
            )

            if not self.load_url(search_url):
                logger.error("XING-Suchseite konnte nicht geladen werden")
                return []

            self.scroll_to_bottom()

            html_content = self.get_html_content()
            if not html_content:
                return []

            soup = BeautifulSoup(html_content, 'html.parser')

            job_url_config = self.config.get("job_url", {})
            selector = job_url_config.get("selector")
            attribute = job_url_config.get("attribute")

            if not selector or not attribute:
                logger.error("XING Job-URL-Konfiguration fehlt")
                return []

            job_elements = soup.select(selector)
            job_urls = []

            for element in job_elements:
                url = element.get(attribute)
                if url:
                    if url.startswith("/"):
                        url = self.base_url + url
                    elif not url.startswith("http"):
                        url = self.base_url + "/" + url

                    if "xing.com" in url and "/jobs/" in url:
                        job_urls.append(url)

            unique_urls = list(set(job_urls))

            if len(unique_urls) > self.max_jobs_limit:
                unique_urls = unique_urls[:self.max_jobs_limit]

            logger.info(f"{len(unique_urls)} XING Jobs gefunden")
            return unique_urls

        except Exception as e:
            logger.error(f"XING URL-Sammlung fehlgeschlagen: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer XING Job-Seite"""
        try:
            if not self.driver:
                self.open_client()

            if not self.driver or not self.load_url(job_page_url):
                return None

            html_content = self.get_html_content()
            if not html_content:
                return None

            soup = BeautifulSoup(html_content, 'html.parser')

            content_selector = self.config.get("job_content_selector")
            title_selector = self.config.get("job_titel_selector")

            content_element = soup.select_one(content_selector) if content_selector else None
            title_element = soup.select_one(title_selector) if title_selector else None

            raw_text = ""
            if content_element:
                raw_text = content_element.get_text(separator=' ', strip=True)
                raw_text = self._clean_xing_text(raw_text)

            job_title = ""
            if title_element:
                job_title = title_element.get_text(strip=True)
                job_title = self._clean_xing_title(job_title)

            if not job_title:
                job_title = "Titel nicht extrahierbar"

            if not raw_text:
                raw_text = "Kein Text extrahierbar"

            return JobDetails(
                title=job_title,
                title_clean="",
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.XING
            )

        except Exception as e:
            logger.error(f"XING Job-Extraktion fehlgeschlagen: {e}")
            return None

    def _clean_xing_text(self, text: str) -> str:
        """XING-spezifische Textbereinigung"""
        if not text:
            return text

        unwanted_phrases = [
            "Jetzt bewerben",
            "Bei XING anmelden",
            "Profil vervollständigen",
            "XING Mitglied werden"
        ]

        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")

        return " ".join(text.split()).strip()

    def _clean_xing_title(self, title: str) -> str:
        """XING-spezifische Titel-Bereinigung"""
        if not title:
            return title

        unwanted_parts = ["| XING Jobs", "- XING", "Jobs bei"]

        for part in unwanted_parts:
            title = title.replace(part, "")

        return title.strip()