from abc import ABC
from typing import List, Dict, Optional, Any
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# Importiere app_config zusätzlich
from projekt.backend.core.config import get_site_config_by_string, app_config

logger = logging.getLogger(__name__)


class SeleniumBaseScraper(ABC):
    """Basis-Klasse für Selenium-basierte Web-Scraper mit Lazy Loading"""

    def __init__(self, site_name: str, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name) # Seiten-spezifische Konfiguration (SITE_CONFIGS)

        # Globale Selenium-Konfiguration aus app_config.scraping
        self.emulate_mobile = app_config.scraping.selenium_emulate_mobile_default
        self.wait_time = app_config.scraping.selenium_wait_time_default
        self.scroll_iterations = app_config.scraping.selenium_scroll_iterations_default
        self.scroll_wait_time = app_config.scraping.selenium_scroll_wait_time_default
        self.timeout = app_config.scraping.timeout

        self.base_url = self.config.get("base_url", "")

        logger.info(f"SeleniumBaseScraper initialisiert für {site_name} (headless: {headless})")

    def _construct_search_url(self, template_path: str, params: Dict[str, Any]) -> str:
        """Ersetzt Platzhalter in einem URL-Template mit Parametern"""
        if not template_path:
            return ""

        path = template_path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", str(value))

        full_url = self.base_url + path
        logger.debug(f"Such-URL konstruiert: {full_url}")
        return full_url

    def get_html_content(self) -> Optional[str]:
        """Gibt den HTML-Inhalt der aktuellen Seite zurück"""
        if not self.driver:
            logger.error("Kein aktiver Client für HTML-Export")
            return None

        try:
            html_content = self.driver.page_source
            logger.info(f"HTML-Inhalt erfolgreich exportiert: {len(html_content)} Zeichen")
            return html_content
        except Exception as e:
            logger.error(f"Fehler beim HTML-Export: {e}")
            return None

    def open_client(self, width: int = 400, height: int = 900) -> None:
        """Öffnet den Selenium-Client falls noch nicht aktiv"""
        if self.driver:
            return
        self._setup_driver(width=width, height=height)

    def close_client(self) -> None:
        """Schließt den Selenium WebDriver"""
        if self.driver:
            logger.info(f"Schließe Selenium-Client für {self.site_name_str}...")
            self.driver.quit()
            self.driver = None
            logger.info("Client erfolgreich geschlossen")
        else:
            logger.debug("Kein aktiver Client zum Schließen vorhanden")

    def _setup_driver(self, width: int = 400, height: int = 900) -> None:
        """Konfiguriert und startet den Chrome WebDriver"""
        chrome_options = Options()

        # Headless-Konfiguration
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--window-size={width},{height}")

        # Mobile-Emulation - verwendet self.emulate_mobile
        if self.emulate_mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": width, "height": height, "pixelRatio": 2.75},
                "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(width, height)
            # Verwendet self.wait_time
            time.sleep(self.wait_time)
            logger.info(f"Chrome WebDriver erfolgreich gestartet für {self.site_name_str}")
        except Exception as e:
            logger.error(f"Fehler beim Starten des WebDrivers: {e}")
            self.driver = None

    def load_url(self, url: str) -> bool:
        """Lädt eine URL im Browser"""
        if not self.driver:
            self.open_client()

        if not self.driver:
            logger.error(f"Kein aktiver Client zum Laden von {url}")
            return False

        try:
            logger.info(f"Lade URL: {url}")
            self.driver.get(url)
            logger.info(f"URL erfolgreich geladen: {url}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Laden der URL {url}: {e}")
            return False

    def scroll_to_bottom(self) -> None:
        """Scrollt mehrfach zum Ende der Seite"""
        if not self.driver:
            logger.error("Kein aktiver Client zum Scrollen vorhanden")
            return

        # Verwendet self.scroll_iterations und self.scroll_wait_time
        logger.info(f"Starte Scroll-Prozess: {self.scroll_iterations} Iterationen")

        for i in range(self.scroll_iterations):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug(f"Scroll-Versuch {i + 1} abgeschlossen")
            if i < self.scroll_iterations - 1:
                time.sleep(self.scroll_wait_time)

        logger.info("Scrollen beendet")