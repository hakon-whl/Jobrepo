import json
from typing import List, Dict, Optional, Any
import re
import time
import random
from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup


class StellenanzeigenScraper(SeleniumBaseScraper):
    """Stellenanzeigen.de Job-Scraper mit Selenium + BeautifulSoup"""

    def __init__(self):
        super().__init__("Stellenanzeigen")

    def get_search_result_urls(self, search_criteria: Dict[str, Any]) -> List[str]:
        """Sammelt Job-URLs von der Stellenanzeigen.de-Suchseite"""
        try:
            # Client initialisieren
            self.open_client(width=400, height=900)
            if not self.driver:
                print("Client konnte nicht geöffnet werden")
                return []

            # Suchparameter vorbereiten
            search_params = {
                "jobTitle": search_criteria.get("jobTitle", ""),
                "location": search_criteria.get("location", ""),
                "radius": search_criteria.get("radius", "20"),
            }

            # Suchseite laden
            search_url = self._construct_search_url(
                self.config.get("search_url_template"), search_params
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

            # Job-URLs aus Script-Tags extrahieren
            soup = BeautifulSoup(html_content, 'html.parser')
            job_urls = []
            pattern = re.compile(r'\\"link\\":\\"([^"]+)\\"')
            all_scripts = soup.find_all('script')

            print(f"INFO: {len(all_scripts)} <script>-Tags gefunden.")

            for script in all_scripts:
                if script.string:
                    # Prüfen, ob der Inhalt für uns relevant ist
                    if 'preloadedState' in script.string or 'initialSeedData' in script.string:
                        print("✅ Relevanter Skript-Block gefunden. Analysiere Inhalt...")

                        matches = pattern.findall(script.string)

                        if matches:
                            print(f"   -> {len(matches)} Treffer im Block gefunden!")
                            # URLs von stellenanzeigen.de hinzufügen
                            for url in matches:
                                if "stellenanzeigen.de/job/" in url:
                                    job_urls.append(url)

            # Duplikate entfernen
            unique_urls = list(set(job_urls))

            print(f"✅ {len(unique_urls)} Job-URLs gefunden")
            return unique_urls

        except Exception as e:
            print(f"Fehler beim Sammeln der Job-URLs: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrahiert Job-Details von einer Stellenanzeigen.de Job-Seite
        mithilfe der in der Konfiguration definierten Selektoren.
        Erwartet, dass der 'job_content_selector' auf ein JSON-LD Script-Tag zeigt.
        """
        try:
            if not self.driver:
                self.open_client(width=400, height=900)
            if not self.driver:
                print(f"Client nicht verfügbar für: {job_page_url}")
                return None

            if not self.load_url(job_page_url):
                return None

            time.sleep(random.uniform(2, 4))

            html_content = self.get_html_content()
            if not html_content:
                print(f"Kein HTML-Inhalt für: {job_page_url}")
                return None

            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. Lade den Selektor aus der Konfigurationsdatei
            content_selector = self.config.get("job_content_selector")
            if not content_selector:
                print("Fehler: 'job_content_selector' nicht in der Konfiguration gefunden.")
                return None

            # 2. Finde das Script-Tag mit dem konfigurierten Selektor
            json_ld_script_element = soup.select_one(content_selector)

            if not json_ld_script_element:
                print(f"Kein Element für Selektor '{content_selector}' auf {job_page_url} gefunden.")
                return None

            # 3. Lade den Inhalt des Scripts als JSON
            job_data = json.loads(json_ld_script_element.string)

            # 4. Extrahiere Titel und Beschreibung aus den JSON-Daten
            job_title = job_data.get("title", "Titel nicht extrahierbar")
            description_html = job_data.get("description", "")

            # 5. Konvertiere die HTML-Beschreibung in reinen Text
            description_soup = BeautifulSoup(description_html, 'html.parser')
            raw_text = description_soup.get_text(separator=' ', strip=True)

            job_title_clean = re.sub(r'[^a-zA-Z0-9 ]', '', job_title) if job_title else ""

            return {
                "title": job_title,
                "title_clean": job_title_clean,
                "raw_text": raw_text,
                "url": job_page_url,
            }

        except json.JSONDecodeError:
            print(f"Fehler beim Parsen der JSON-Daten von {job_page_url}")
            return None
        except Exception as e:
            print(f"Fehler beim Extrahieren von {job_page_url}: {e}")
            return None