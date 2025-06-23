from typing import List, Optional
import time
import random
from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource
import logging

from ..core import app_config

logger = logging.getLogger(__name__)


class XingScraper(SeleniumBaseScraper):
    """XING Job-Scraper mit erweiterten Konfigurationen"""

    def __init__(self):
        super().__init__("Xing")

        # XING-spezifische Konfigurationen
        self.max_jobs_limit = getattr(app_config.scraping, 'max_total_jobs_per_site', 100)

    def get_search_result_urls(self, search_criteria: SearchCriteria) -> List[str]:
        """Sammelt Job-URLs von der XING-Suchseite mit verbesserter Logik"""
        try:
            # Client initialisieren
            self.open_client()
            if not self.driver:
                logger.error("Client konnte nicht geöffnet werden")
                return []

            # Suchseite laden
            search_url = self._construct_search_url(
                self.config.get("search_url_template"),
                search_criteria.to_xing_params()
            )

            # Seite laden
            if not self.load_url(search_url):
                logger.error("XING-Suchseite konnte nicht geladen werden")
                return []

            # XING-spezifische Scroll-Strategie mit "Mehr laden" Button
            logger.info("Führe XING-spezifischen Scroll-Prozess durch...")

            # Versuche "Mehr laden" Button zu klicken
            load_more_selector = self.config.get("load_more_button_selector")
            if load_more_selector:
                for attempt in range(self.load_more_attempts):
                    logger.debug(f"Versuche 'Mehr laden' Button zu klicken (Versuch {attempt + 1})")

                    self.scroll_to_bottom()

            else:
                # Fallback: Normales Scrollen
                self.scroll_to_bottom()

            # HTML parsen
            html_content = self.get_html_content()
            if not html_content:
                logger.error("Kein HTML-Inhalt erhalten")
                return []

            # Job-URLs extrahieren
            soup = BeautifulSoup(html_content, 'html.parser')

            job_url_config = self.config.get("job_url", {})
            selector = job_url_config.get("selector")
            attribute = job_url_config.get("attribute")

            if not selector or not attribute:
                logger.error("Job-URL-Konfiguration fehlt")
                return []

            job_elements = soup.select(selector)
            job_urls = []

            for element in job_elements:
                url = element.get(attribute)
                if url:
                    # URL-Bereinigung
                    if url.startswith("/"):
                        url = self.base_url + url
                    elif not url.startswith("http"):
                        url = self.base_url + "/" + url

                    # Nur XING-URLs hinzufügen
                    if "xing.com" in url and "/jobs/" in url:
                        job_urls.append(url)

            # Duplikate entfernen
            unique_urls = list(set(job_urls))

            # Limit anwenden
            if len(unique_urls) > self.max_jobs_limit:
                logger.info(f"Begrenze {len(unique_urls)} URLs auf {self.max_jobs_limit}")
                unique_urls = unique_urls[:self.max_jobs_limit]

            logger.info(f"✅ {len(unique_urls)} einzigartige XING Job-URLs gefunden")
            return unique_urls

        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Job-URLs: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer XING Job-Seite mit verbesserter Logik"""
        try:
            # Client prüfen
            if not self.driver:
                self.open_client()

            if not self.driver:
                logger.error(f"Client nicht verfügbar für: {job_page_url}")
                return None

            # Job-Seite laden
            if not self.load_url(job_page_url):
                logger.warning(f"XING Job-Seite konnte nicht geladen werden: {job_page_url}")
                return None

            # HTML parsen
            html_content = self.get_html_content()
            if not html_content:
                logger.warning(f"Kein HTML-Inhalt für: {job_page_url}")
                return None

            soup = BeautifulSoup(html_content, 'html.parser')

            # Primäre Selektoren aus Konfiguration
            content_selector = self.config.get("job_content_selector")
            title_selector = self.config.get("job_titel_selector")

            content_element = soup.select_one(content_selector) if content_selector else None
            title_element = soup.select_one(title_selector) if title_selector else None

            # Fallback-Selektoren für XING
            if not title_element:
                title_fallbacks = [
                    "h1[data-testid='job-title']",
                    "h1.job-title",
                    "h1",
                    ".job-header h1",
                    "[data-qa='job-title']"
                ]

                for fallback in title_fallbacks:
                    title_element = soup.select_one(fallback)
                    if title_element:
                        logger.debug(f"XING Titel-Fallback verwendet: {fallback}")
                        break

            if not content_element:
                content_fallbacks = [
                    ".job-description",
                    "[data-testid='job-description']",
                    ".job-details",
                    ".job-content",
                    "[data-qa='job-description']",
                    "main .content"
                ]

                for fallback in content_fallbacks:
                    content_element = soup.select_one(fallback)
                    if content_element:
                        logger.debug(f"XING Content-Fallback verwendet: {fallback}")
                        break

            # Text extrahieren mit Bereinigung
            raw_text = ""
            if content_element:
                raw_text = content_element.get_text(separator=' ', strip=True)
                # XING-spezifische Bereinigung
                raw_text = self._clean_xing_text(raw_text)

            job_title = ""
            if title_element:
                job_title = title_element.get_text(strip=True)
                job_title = self._clean_xing_title(job_title)

            # Validierung
            if not job_title:
                job_title = "Titel nicht extrahierbar"
                logger.warning(f"Kein Titel für XING Job: {job_page_url}")

            if not raw_text:
                raw_text = "Kein Text extrahierbar"
                logger.warning(f"Kein Content für XING Job: {job_page_url}")

            return JobDetails(
                title=job_title,
                title_clean="",
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.XING
            )

        except Exception as e:
            logger.error(f"Fehler beim Extrahieren von XING Job {job_page_url}: {e}")
            return None

    def _clean_xing_text(self, text: str) -> str:
        """XING-spezifische Textbereinigung"""
        if not text:
            return text

        # Entferne XING-spezifische Störelemente
        unwanted_phrases = [
            "Jetzt bewerben",
            "Bei XING anmelden",
            "Profil vervollständigen",
            "XING Mitglied werden"
        ]

        for phrase in unwanted_phrases:
            text = text.replace(phrase, "")

        # Mehrfache Leerzeichen bereinigen
        text = " ".join(text.split())

        return text.strip()

    def _clean_xing_title(self, title: str) -> str:
        """XING-spezifische Titel-Bereinigung"""
        if not title:
            return title

        # Entferne XING-spezifische Prefixe/Suffixe
        unwanted_parts = ["| XING Jobs", "- XING", "Jobs bei"]

        for part in unwanted_parts:
            title = title.replace(part, "")

        return title.strip()