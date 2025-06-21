from typing import List, Optional
import re
import time
import random
from .request_base_scraper import RequestBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource


class StepstoneScraper(RequestBaseScraper):

    def __init__(self):
        super().__init__("StepStone")

    def get_search_result_urls(self, search_criteria: SearchCriteria, max_pages: int = 6) -> List[str]:
        """Sammelt Job-URLs von StepStone Suchseiten"""
        try:
            # Konfiguration validieren
            required_configs = ["search_url_template", "job_url", "max_page_selector"]
            for config_key in required_configs:
                if not self.config.get(config_key):
                    print(f"Fehlende Konfiguration für StepStone: {config_key}")
                    return []

            # URL-Parameter vorbereiten mit SearchCriteria
            params = search_criteria.to_stepstone_params()
            params["seite"] = 1  # Starte immer mit Seite 1

            # === SCHRITT 1: ERSTE SEITE LADEN UND KOMPLETT ABARBEITEN ===
            search_url = self._construct_search_url(
                self.config.get("search_url_template"), params
            )
            html_content = self.get_html_content(search_url)

            if not html_content:
                print("Konnte erste Suchseite nicht laden.")
                return []

            soup = BeautifulSoup(html_content, 'lxml')

            # Max. Seitenzahl ermitteln
            pages_element = soup.select_one(self.config.get("max_page_selector"))
            if not pages_element:
                print("Konnte maximale Seitenzahl nicht ermitteln.")
                total_pages = 1
            else:
                try:
                    max_pages_text = pages_element.get_text().rsplit(maxsplit=1)[-1]
                    total_pages = min(int(max_pages_text), max_pages)
                except (ValueError, IndexError):
                    print("Fehler beim Parsen der maximalen Seitenzahl.")
                    total_pages = 1

            print(f"🔗 Maximal verfügbare Seiten: {max_pages_text} (StepStone)")

            print(f"Verarbeite {total_pages} Seiten für StepStone...")

            all_job_urls = []

            # URLs von der ERSTEN SEITE sammeln (HTML bereits geladen)
            job_url_config = self.config.get("job_url", {})
            selector = job_url_config.get("selector")
            attribute = job_url_config.get("attribute")

            if selector and attribute:
                job_elements = soup.select(selector)
                page_urls = []

                for element in job_elements:
                    url = element.get(attribute)
                    if url:
                        if url.startswith("/"):
                            url = self.base_url + url
                        page_urls.append(url)

                all_job_urls.extend(page_urls)
                print(f"Seite 1: {len(page_urls)} Job-URLs gefunden")

            # === SCHRITT 2: WEITERE SEITEN (2 bis total_pages) ABARBEITEN ===
            if total_pages > 1:
                for page_num in range(2, total_pages + 1):
                    # Wartezeit zwischen den Seiten
                    sleep_time = random.uniform(3, 7)
                    print(f"Warte {sleep_time:.2f} Sekunden vor Seite {page_num}...")
                    time.sleep(sleep_time)

                    # URL für die nächste Seite bauen
                    params["seite"] = page_num
                    current_url = self._construct_search_url(
                        self.config.get("search_url_template"), params
                    )

                    # HTML der aktuellen Seite laden
                    html_content = self.get_html_content(current_url)
                    if not html_content:
                        print(f"Konnte Seite {page_num} nicht laden.")
                        continue

                    # URLs von der aktuellen Seite sammeln
                    soup = BeautifulSoup(html_content, 'lxml')

                    if selector and attribute:
                        job_elements = soup.select(selector)
                        page_urls = []

                        for element in job_elements:
                            url = element.get(attribute)
                            if url:
                                if url.startswith("/"):
                                    url = self.base_url + url
                                page_urls.append(url)

                        all_job_urls.extend(page_urls)
                        print(f"Seite {page_num}: {len(page_urls)} Job-URLs gefunden")

            print(f"✅ Insgesamt {len(all_job_urls)} Job-URLs gesammelt")
            return all_job_urls

        except Exception as e:
            print(f"Fehler beim Sammeln der Job-URLs: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer StepStone Job-Seite"""
        try:
            # HTML laden
            html_content = self.get_html_content(job_page_url)
            if not html_content:
                print(f"Konnte Job-Seite nicht laden: {job_page_url}")
                return None

            # HTML parsen
            soup = BeautifulSoup(html_content, 'lxml')

            # Selektoren aus Config
            content_selector = self.config.get("job_content_selector")
            title_selector = self.config.get("job_titel_selector")

            if not content_selector or not title_selector:
                print("Job-Content oder Titel-Selektor fehlt in der Konfiguration.")
                return None

            # Elemente finden und Text extrahieren
            content_element = soup.select_one(content_selector)
            title_element = soup.select_one(title_selector)

            raw_text = content_element.get_text(strip=True) if content_element else "Kein Text extrahierbar"
            job_title = title_element.get_text(strip=True) if title_element else "Titel nicht extrahierbar"

            return JobDetails(
                title=job_title,
                title_clean="",  # Wird in __post_init__ gesetzt
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.STEPSTONE
            )

        except Exception as e:
            print(f"Fehler beim Extrahieren von {job_page_url}: {e}")
            return None