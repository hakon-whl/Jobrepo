from typing import List, Dict, Optional, Any
import re
import time
import random
# HIER IST DER WICHTIGE FIX - relativer Import statt direktem Import
from .base_scraper import BaseScraper
from projekt.backend.utils.html_parser import (
    extract_attribute_from_selector,
    extract_text_from_selector,
)


class StepstoneScraper(BaseScraper):
    def __init__(self):
        super().__init__("StepStone")

    def _extract_title_from_url_slug(self, url_slug: str) -> Optional[str]:
        """
        Extrahiert einen potenziellen Jobtitel aus dem URL-Slug.
        Beispiel: "/stellenangebote--Softwareentwickler-Python-Berlin--12345" -> "Softwareentwickler Python Berlin"
        Diese Logik basiert auf deiner `extract_between_delimiters`.
        """
        if not url_slug:
            return None
        match = re.search(r"--(.*?)(?:--\d+|$)", url_slug)
        if match:
            title_part = match.group(1)
            return title_part.replace("-", " ").strip()
        # Fallback, wenn das Muster nicht passt, aber ein Titel extrahiert werden soll
        # Teile des Pfads könnten auch nützlich sein
        parts = [p for p in url_slug.split("/") if p and not p.startswith("stellenangebote")]
        if parts:
            # Entferne IDs oder andere nicht-Titel Teile
            cleaned_parts = [re.sub(r'--\d+$', '', p).replace('-', ' ') for p in parts]
            return " ".join(cleaned_parts).strip()
        return "Unbekannter Jobtitel"

    def get_search_result_urls(
            self, search_criteria: Dict[str, Any]
    ) -> List[str]:
        all_job_detail_urls = []
        search_url_template = self.config.get("search_url_template")
        job_url_selector = self.config.get("job_url").get("selector")
        job_url_attribute = self.config.get("job_url").get("attribute")
        job_content_selector = self.config.get("job_content_selector")
        job_pages_selector = self.config.get("job_pages_selector")

        if not (
                search_url_template and job_url_selector and job_url_attribute and job_content_selector and job_pages_selector):
            print(
                "Fehlende Konfiguration für StepStone: URL-Template, Listen-Selektor oder Gesamtanzahl-Selektor."
            )
            return []

        current_page = 1

        params_for_page = {
            "jobTitle": search_criteria.get("jobTitle", ""),
            "location": search_criteria.get("location", ""),
            "radius": search_criteria.get("radius", "20"),  # Standardwert
            "discipline": search_criteria.get("discipline", ""),  # 'disciplineHierarchy' im Template
            "seite": current_page,
        }

        # Erste Seite abrufen, um Gesamtanzahl der Jobs zu ermitteln
        first_page_url = self._construct_search_url(
            search_url_template, params_for_page
        )
        html_first_page = self._fetch_html(first_page_url)

        if not html_first_page:
            print("Konnte die erste Ergebnisseite nicht laden. Versuche es später erneut.")
            return []

        # Gesamtanzahl der Jobs extrahieren mit Fehlerbehandlung
        total_jobs_pages = extract_text_from_selector(
            html_first_page, job_pages_selector
        )

        if not total_jobs_pages:
            print("Konnte die Gesamtzahl der Seiten nicht ermitteln. Verwende Standardwert von 1 Seite.")
            total_jobs_pages = "1"

        try:
            max_pages = min(int(total_jobs_pages), 3)  # Begrenze auf max. 3 Seiten für Tests
        except ValueError:
            print(f"Ungültiger Wert für Gesamtseiten: {total_jobs_pages}. Verwende 1.")
            max_pages = 1

        print(f"Verarbeite {max_pages} Seiten für StepStone...")

        for page_num in range(1, max_pages + 1):
            # Zwischen den Seitenaufrufen warten, um Rate-Limiting zu vermeiden
            if page_num > 1:
                sleep_time = random.uniform(3, 7)
                print(f"Warte {sleep_time:.2f} Sekunden vor dem Laden der nächsten Seite...")
                time.sleep(sleep_time)

            print(f"Verarbeite Seite {page_num}/{max_pages}...")
            params_for_page["seite"] = page_num
            current_search_url = self._construct_search_url(
                search_url_template, params_for_page
            )

            # Für Seite 1 haben wir den HTML-Inhalt bereits
            html_content = html_first_page if page_num == 1 else self._fetch_html(current_search_url)

            if not html_content:
                print(f"Konnte Seite {page_num} nicht laden. Überspringe...")
                continue

            page_job_urls = extract_attribute_from_selector(
                html_content, job_url_selector, job_url_attribute
            )

            if not page_job_urls:
                print(f"Keine Job-URLs auf Seite {page_num} gefunden.")
                continue

            print(f"Gefunden: {len(page_job_urls)} Job-URLs auf Seite {page_num}")

            for job_url in page_job_urls:
                if job_url.startswith("/"):
                    full_url = self.base_url + job_url
                    all_job_detail_urls.append(full_url)
                elif job_url.startswith("http"):
                    all_job_detail_urls.append(job_url)

        return list(set(all_job_detail_urls))

    def extract_job_details(
            self, job_page_url: str
    ) -> Optional[Dict[str, Any]]:
        html_content = self._fetch_html(job_page_url)
        if not html_content:
            print(f"Konnte die Job-Detailseite {job_page_url} nicht laden.")
            return None

        content_selector = self.config.get("job_content_selector")
        if not content_selector:
            print("Detailseiten-Content-Selektor fehlt in der Konfiguration.")
            return None

        raw_text = extract_text_from_selector(html_content, content_selector)
        url_path_slug = job_page_url.replace(self.base_url, "")
        job_title = self._extract_title_from_url_slug(url_path_slug)

        if not raw_text:
            print(f"Konnte keinen Textinhalt für {job_page_url} extrahieren.")
            # Manchmal ist der Titel wichtiger, also nicht sofort None zurückgeben
            # return None

        return {
            "title": job_title or "Titel nicht extrahierbar",
            "raw_text": raw_text or "Kein Text extrahierbar",
            "url": job_page_url,
        }
