from typing import List, Optional
import time
import random
from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource


class XingScraper(SeleniumBaseScraper):
    """XING Job-Scraper mit Selenium + BeautifulSoup"""

    def __init__(self):
        super().__init__("Xing")

    def get_search_result_urls(self, search_criteria: SearchCriteria) -> List[str]:
        """Sammelt Job-URLs von der XING-Suchseite"""
        try:
            # Client initialisieren
            self.open_client(width=400, height=900)
            if not self.driver:
                print("Client konnte nicht geöffnet werden")
                return []

            # Suchseite laden mit SearchCriteria
            search_url = self._construct_search_url(
                self.config.get("search_url_template"),
                search_criteria.to_xing_params()
            )

            if not self.load_url(search_url):
                return []

            # Seite laden lassen und scrollen
            time.sleep(5)
            self.scroll_to_bottom()
            time.sleep(2)

            # HTML parsen
            html_content = self.get_html_content()
            if not html_content:
                print("Kein HTML-Inhalt erhalten")
                return []

            # Job-URLs direkt extrahieren
            soup = BeautifulSoup(html_content, 'html.parser')

            job_url_config = self.config.get("job_url", {})
            selector = job_url_config.get("selector")
            attribute = job_url_config.get("attribute")

            if not selector or not attribute:
                print("Job-URL-Konfiguration fehlt")
                return []

            job_elements = soup.select(selector)
            job_urls = []

            for element in job_elements:
                url = element.get(attribute)
                if url:
                    if url.startswith("/"):
                        url = self.base_url + url
                    job_urls.append(url)

            print(f"✅ {len(job_urls)} Job-URLs gefunden")
            return job_urls

        except Exception as e:
            print(f"Fehler beim Sammeln der Job-URLs: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer XING Job-Seite"""
        try:
            # Client prüfen
            if not self.driver:
                self.open_client(width=400, height=900)

            if not self.driver:
                print(f"Client nicht verfügbar für: {job_page_url}")
                return None

            # Job-Seite laden
            if not self.load_url(job_page_url):
                return None

            time.sleep(random.uniform(2, 4))

            # HTML parsen
            html_content = self.get_html_content()
            if not html_content:
                print(f"Kein HTML-Inhalt für: {job_page_url}")
                return None

            # Job-Daten direkt extrahieren
            soup = BeautifulSoup(html_content, 'html.parser')

            content_selector = self.config.get("job_content_selector")
            title_selector = self.config.get("job_titel_selector")

            content_element = soup.select_one(content_selector) if content_selector else None
            title_element = soup.select_one(title_selector) if title_selector else None

            raw_text = content_element.get_text(strip=True) if content_element else "Kein Text extrahierbar"
            job_title = title_element.get_text(strip=True) if title_element else "Titel nicht extrahierbar"

            return JobDetails(
                title=job_title,
                title_clean="",  # Wird in __post_init__ gesetzt
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.XING
            )

        except Exception as e:
            print(f"Fehler beim Extrahieren von {job_page_url}: {e}")
            return None