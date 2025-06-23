import json
from typing import List, Optional
import re
import time
import random
from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource
import logging

from ..core import app_config

logger = logging.getLogger(__name__)


class StellenanzeigenScraper(SeleniumBaseScraper):
    """Stellenanzeigen.de Job-Scraper mit erweiterten Konfigurationen"""

    def __init__(self):
        super().__init__("Stellenanzeigen")

        # Stellenanzeigen-spezifische Konfigurationen
        self.max_jobs_limit = getattr(app_config.scraping, 'max_total_jobs_per_site', 100)

    def get_search_result_urls(self, search_criteria: SearchCriteria) -> List[str]:
        """Sammelt Job-URLs von der Stellenanzeigen.de-Suchseite mit verbesserter Logik"""
        try:
            # Client initialisieren mit Konfiguration
            self.open_client()
            if not self.driver:
                logger.error("Client konnte nicht geöffnet werden")
                return []

            # Suchseite laden mit SearchCriteria
            search_url = self._construct_search_url(
                self.config.get("search_url_template"),
                search_criteria.to_stellenanzeigen_params()
            )

            # Seite laden
            if not self.load_url(search_url):
                logger.error("Suchseite konnte nicht geladen werden")
                return []

            # Erweiterte Scroll-Strategie
            logger.info("Führe erweiterten Scroll-Prozess durch...")

            # Erst schnell scrollen für Lazy Loading
            self.scroll_to_bottom()

            # Dann langsamer für vollständiges Laden
            self.scroll_to_bottom()

            # HTML parsen
            html_content = self.get_html_content()
            if not html_content:
                logger.error("Kein HTML-Inhalt erhalten")
                return []

            # Job-URLs aus Script-Tags extrahieren
            soup = BeautifulSoup(html_content, 'html.parser')
            job_urls = []

            # Erweiterte Regex-Patterns für verschiedene URL-Formate
            patterns = [
                re.compile(r'\\"link\\":\\"([^"]+)\\"'),
                re.compile(r'"url":\s*"([^"]+)"'),
                re.compile(r'"href":\s*"([^"]+stellenanzeigen\.de/job/[^"]+)"')
            ]

            all_scripts = soup.find_all('script')
            logger.info(f"Analysiere {len(all_scripts)} <script>-Tags...")

            for script in all_scripts:
                if script.string:
                    script_content = script.string

                    # Prüfen, ob der Inhalt für uns relevant ist
                    relevant_keywords = ['preloadedState', 'initialSeedData', 'job', 'stellenanzeigen']
                    if any(keyword in script_content for keyword in relevant_keywords):
                        logger.debug("✅ Relevanter Skript-Block gefunden. Analysiere Inhalt...")

                        # Alle Patterns testen
                        for pattern in patterns:
                            matches = pattern.findall(script_content)
                            if matches:
                                logger.debug(f"Pattern gefunden: {len(matches)} Treffer")

                                for url in matches:
                                    # URL bereinigen (Escape-Sequenzen entfernen)
                                    clean_url = url.replace('\\/', '/')

                                    # Nur stellenanzeigen.de Job-URLs hinzufügen
                                    if "stellenanzeigen.de/job/" in clean_url:
                                        if not clean_url.startswith('http'):
                                            if clean_url.startswith('/'):
                                                clean_url = self.base_url + clean_url
                                            else:
                                                clean_url = self.base_url + '/' + clean_url
                                        job_urls.append(clean_url)

            # Duplikate entfernen
            unique_urls = list(set(job_urls))

            # Limit anwenden
            if len(unique_urls) > self.max_jobs_limit:
                logger.info(f"Begrenze {len(unique_urls)} URLs auf {self.max_jobs_limit}")
                unique_urls = unique_urls[:self.max_jobs_limit]

            logger.info(f"✅ {len(unique_urls)} einzigartige Job-URLs gefunden")
            return unique_urls

        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Job-URLs: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer Stellenanzeigen.de Job-Seite mit verbesserter Logik"""
        try:
            if not self.driver:
                self.open_client()
            if not self.driver:
                logger.error(f"Client nicht verfügbar für: {job_page_url}")
                return None

            # Seite laden mit intelligenter Wartezeit
            if not self.load_url(job_page_url):
                logger.warning(f"Job-Seite konnte nicht geladen werden: {job_page_url}")
                return None

            html_content = self.get_html_content()
            if not html_content:
                logger.warning(f"Kein HTML-Inhalt für: {job_page_url}")
                return None

            soup = BeautifulSoup(html_content, 'html.parser')

            # Primärer Ansatz: JSON-LD Daten
            content_selector = self.config.get("job_content_selector")
            if content_selector:
                json_ld_script = soup.select_one(content_selector)

                if json_ld_script and json_ld_script.string:
                    try:
                        job_data = json.loads(json_ld_script.string)

                        job_title = job_data.get("title", "")
                        description_html = job_data.get("description", "")

                        # HTML-Beschreibung in Text konvertieren
                        if description_html:
                            desc_soup = BeautifulSoup(description_html, 'html.parser')
                            raw_text = desc_soup.get_text(separator=' ', strip=True)
                        else:
                            raw_text = ""

                        if job_title and raw_text:
                            return JobDetails(
                                title=job_title,
                                title_clean="",
                                raw_text=raw_text,
                                url=job_page_url,
                                source_site=JobSource.STELLENANZEIGEN
                            )
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON-Parsing fehlgeschlagen für {job_page_url}: {e}")

            # Fallback-Ansatz: Direkte HTML-Extraktion
            logger.debug("Verwende Fallback-Extraktion für Stellenanzeigen")

            # Titel-Fallbacks
            title_selectors = [
                "h1[data-testid='job-title']",
                "h1.job-title",
                "h1",
                ".job-header h1",
                "[data-testid='title']"
            ]

            job_title = ""
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    job_title = title_element.get_text(strip=True)
                    logger.debug(f"Titel gefunden mit Selektor: {selector}")
                    break

            # Content-Fallbacks
            content_selectors = [
                ".job-description",
                "[data-testid='job-description']",
                ".job-content",
                ".jobad-content",
                "main .content"
            ]

            raw_text = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    raw_text = content_element.get_text(separator=' ', strip=True)
                    logger.debug(f"Content gefunden mit Selektor: {selector}")
                    break

            # Minimal-Validierung
            if not job_title:
                job_title = "Titel nicht extrahierbar"
                logger.warning(f"Kein Titel extrahierbar für {job_page_url}")

            if not raw_text:
                raw_text = "Kein Text extrahierbar"
                logger.warning(f"Kein Content extrahierbar für {job_page_url}")

            return JobDetails(
                title=job_title,
                title_clean="",
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.STELLENANZEIGEN
            )

        except Exception as e:
            logger.error(f"Fehler beim Extrahieren von {job_page_url}: {e}")
            return None