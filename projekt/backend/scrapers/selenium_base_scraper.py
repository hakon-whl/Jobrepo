import time
import os
from abc import ABC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from projekt.backend.core.config import get_site_config_by_string, Site, USER_AGENTS

class SeleniumBaseClient(ABC):
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless

    def _setup_driver(
        self,
        mobile_mode: bool = False,
        width: int = 1280,
        height: int = 800
    ) -> None:
        chrome_options = Options()

        # Konfiguration für den Headless-Modus
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")  # Empfohlen für Headless
            chrome_options.add_argument("--no-sandbox")  # Für Linux/Docker-Umgebungen
            chrome_options.add_argument("--disable-dev-shm-usage")  # Für Linux/Docker
            chrome_options.add_argument(f"--window-size={width},{height}")

        if mobile_mode:
            mobile_emulation = {
                "deviceMetrics": {
                    "width": width,
                    "height": height,
                    "pixelRatio": 2.75
                },
                "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
                "Mobile Safari/537.36"
            }
            chrome_options.add_experimental_option(
                "mobileEmulation",
                mobile_emulation
            )

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

            self.driver.set_window_size(width, height)
            time.sleep(1)
        except Exception as e:
            self.driver = None

    def open_client(self, width: int = 400, height: int = 900) -> None:
        if self.driver:
            return
        self._setup_driver(mobile_mode=False, width=width, height=height)

    def open_mobile_website(self, url: str, width: int = 393,
                            height: int = 851) -> None:
        if self.driver:
            print("Ein Client ist bereits aktiv. Lade URL im bestehenden Client.")
            try:
                self.driver.get(url)
                print(f"Webseite '{url}' erfolgreich geladen.")
            except Exception as e:
                print(f"Fehler beim Laden der Webseite '{url}': {e}")
            return

        print(
            f"Öffne Webseite '{url}' im Handy-Format ({width}x{height} Pixel)..."
        )
        self._setup_driver(mobile_mode=True, width=width, height=height)
        if self.driver:
            try:
                self.driver.get(url)
                print(f"Webseite '{url}' erfolgreich geladen im Handy-Format.")
            except Exception as e:
                print(f"Fehler beim Laden der Webseite '{url}': {e}")
        else:
            print(
                "Webseite konnte nicht geladen werden, da der Client nicht "
                "gestartet werden konnte."
            )

    def scroll_to_bottom(self, retries: int = 1, delay: float = 0.5) -> None:

        if not self.driver:
            print("Kein aktiver Client zum Scrollen vorhanden.")
            return

        print(f"Scrolle {retries} Mal nach ganz unten...")
        for i in range(retries):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            print(f"Scroll-Versuch {i + 1} abgeschlossen.")
            if i < retries - 1:
                time.sleep(delay)
        print("Scrollen beendet.")

    def get_html_content(self) -> str | None:
        """
        Exportiert den vollständigen HTML-Inhalt der aktuell geladenen Seite.

        Returns:
            str | None: Der HTML-Quellcode der Seite als String oder None,
                        wenn kein Client aktiv ist.
        """
        if not self.driver:
            print("Kein aktiver Client, HTML-Inhalt kann nicht abgerufen werden.")
            return None
        try:
            html_content = self.driver.page_source
            print("HTML-Inhalt erfolgreich abgerufen.")
            return html_content
        except Exception as e:
            print(f"Fehler beim Abrufen des HTML-Inhalts: {e}")
            return None

    def close_client(self) -> None:
        """
        Schließt den Selenium WebDriver (den Browser).
        """
        if self.driver:
            print("Schließe Selenium-Client...")
            self.driver.quit()
            self.driver = None
            print("Client erfolgreich geschlossen.")
        else:
            print("Kein aktiver Client zum Schließen vorhanden.")


# --- Beispiel für die Verwendung der Klasse ---
if __name__ == "__main__":
    client_desktop = SeleniumBaseClient(headless=True) # Headless für schnellere Verarbeitung
    try:
        client_desktop.open_client(width=400, height=900)
        if client_desktop.driver:
            url_desktop = (
                "https://www.xing.com/jobs/search?"
                "keywords=Softwareentwickler&location=M%C3%BCnchen&radius=25"
            )
            print(f"Lade Desktop-Webseite: {url_desktop}")
            client_desktop.driver.get(url_desktop)
            print("Warte 5 Sekunden, damit Inhalte geladen werden...")
            time.sleep(5)
            client_desktop.scroll_to_bottom(retries=4, delay=3)
            print("Warte weitere 5 Sekunden nach dem Scrollen...")
            time.sleep(5)

            # --- HTML-Inhalt abrufen und mit BeautifulSoup parsen ---
            html_source = client_desktop.get_html_content()
            job_urls = []
            base_xing_job_url = "https://www.xing.com"

            if html_source:
                soup = BeautifulSoup(html_source, "html.parser")

                # Wir suchen nach einem 'a'-Tag mit dem Attribut 'data-testid="job-search-result"'
                job_links = soup.find_all(
                    "a",
                    attrs={"data-testid": "job-search-result"}
                )

                print(f"\n--- Gefundene Job-Links ({len(job_links)}): ---")
                for link in job_links:
                    href = link.get("href")
                    if href:
                        # Füge die Basis-URL hinzu, falls der href relativ ist
                        if href.startswith("/"):
                            full_url = base_xing_job_url + href
                        else:
                            full_url = href # Falls es bereits eine absolute URL ist
                        job_urls.append(full_url)
                        print(full_url) # Gib die URL sofort aus

                print("\nAlle Job-URLs wurden extrahiert.")
                # Sie können die Liste `job_urls` nun weiterverwenden.
            else:
                print("Konnte keinen HTML-Inhalt zum Parsen abrufen.")

    finally:
        client_desktop.close_client()

    print("\nBeispiel beendet.")