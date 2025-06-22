from abc import ABC
from typing import List, Dict, Optional, Any
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from projekt.backend.core.config import get_site_config_by_string, USER_AGENTS, app_config

logger = logging.getLogger(__name__)


class SeleniumBaseScraper(ABC):
    """Basis-Klasse für Selenium-basierte Web-Scraper mit erweiterten Konfigurationen"""

    def __init__(self, site_name: str, headless: bool = True):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)

        # Globale Selenium-Konfiguration aus app_config
        self.emulate_mobile = app_config.scraping.selenium_emulate_mobile_default
        self.wait_time = app_config.scraping.selenium_wait_time_default
        self.scroll_iterations = app_config.scraping.selenium_scroll_iterations_default
        self.scroll_wait_time = app_config.scraping.selenium_scroll_wait_time_default
        self.timeout = app_config.scraping.timeout

        # Neue erweiterte Konfigurationen
        self.default_width = getattr(app_config.scraping, 'selenium_window_width_default', 400)
        self.default_height = getattr(app_config.scraping, 'selenium_window_height_default', 900)
        self.page_load_timeout = getattr(app_config.scraping, 'page_load_timeout', 30)
        self.implicit_wait = getattr(app_config.scraping, 'implicit_wait', 10)
        self.explicit_wait = getattr(app_config.scraping, 'explicit_wait', 15)

        # Delay-Konfigurationen
        self.page_delay_min = getattr(app_config.scraping, 'page_delay_min', 3.0)
        self.page_delay_max = getattr(app_config.scraping, 'page_delay_max', 6.0)

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

    def open_client(self, width: int = None, height: int = None) -> None:
        """Öffnet den Selenium-Client falls noch nicht aktiv"""
        if self.driver:
            return

        # Nutze Config-Defaults wenn nicht angegeben
        width = width or self.default_width
        height = height or self.default_height

        self._setup_driver(width=width, height=height)

    def close_client(self) -> None:
        """Schließt den Selenium WebDriver"""
        if self.driver:
            logger.info(f"Schließe Selenium-Client für {self.site_name_str}...")
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Fehler beim Schließen des Drivers: {e}")
            finally:
                self.driver = None
                self.wait = None
            logger.info("Client erfolgreich geschlossen")
        else:
            logger.debug("Kein aktiver Client zum Schließen vorhanden")

    def _setup_driver(self, width: int = 400, height: int = 900) -> None:
        """Konfiguriert und startet den Chrome WebDriver"""
        chrome_options = Options()

        # Basis-Optimierungen
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Headless-Konfiguration
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--window-size={width},{height}")

        # Mobile-Emulation oder Desktop mit User-Agent
        if self.emulate_mobile:
            mobile_emulation = {
                "deviceMetrics": {
                    "width": width,
                    "height": height,
                    "pixelRatio": 2.75
                },
                "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        else:
            # Desktop mit zufälligem User-Agent
            random_ua = random.choice(USER_AGENTS)
            chrome_options.add_argument(f"--user-agent={random_ua}")
            logger.debug(f"Desktop User-Agent gesetzt: {random_ua[:50]}...")

        # Site-spezifische Chrome-Optionen
        site_chrome_options = self.config.get("chrome_options", [])
        for option in site_chrome_options:
            chrome_options.add_argument(option)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # WebDriver-Konfiguration
            self.driver.set_window_size(width, height)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)

            # WebDriverWait für explizite Waits
            self.wait = WebDriverWait(self.driver, self.explicit_wait)

            # Anti-Detection Script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            time.sleep(self.wait_time)
            logger.info(f"Chrome WebDriver erfolgreich gestartet für {self.site_name_str}")

        except Exception as e:
            logger.error(f"Fehler beim Starten des WebDrivers: {e}")
            self.driver = None
            self.wait = None

    def load_url(self, url: str, wait_for_element: str = None) -> bool:
        """Lädt eine URL im Browser mit optionalem Element-Wait"""
        if not self.driver:
            self.open_client()

        if not self.driver:
            logger.error(f"Kein aktiver Client zum Laden von {url}")
            return False

        try:
            logger.info(f"Lade URL: {url}")
            self.driver.get(url)

            # Intelligente Wartezeit nach dem Laden
            delay = random.uniform(self.page_delay_min, self.page_delay_max)
            logger.debug(f"Warte {delay:.2f} Sekunden nach dem Laden der Seite...")
            time.sleep(delay)

            # Optional: Warten auf spezifisches Element
            if wait_for_element and self.wait:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                    logger.debug(f"Element '{wait_for_element}' erfolgreich geladen")
                except Exception as e:
                    logger.warning(f"Element '{wait_for_element}' nicht gefunden: {e}")

            logger.info(f"URL erfolgreich geladen: {url}")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Laden der URL {url}: {e}")
            return False

    def scroll_to_bottom(self, custom_iterations: int = None, custom_wait: float = None) -> None:
        """Scrollt mehrfach zum Ende der Seite mit konfigurierbaren Parametern"""
        if not self.driver:
            logger.error("Kein aktiver Client zum Scrollen vorhanden")
            return

        iterations = custom_iterations or self.scroll_iterations
        wait_time = custom_wait or self.scroll_wait_time

        logger.info(f"Starte Scroll-Prozess: {iterations} Iterationen")

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(iterations):
            # Scroll nach unten
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug(f"Scroll-Versuch {i + 1} abgeschlossen")

            # Warten
            if i < iterations - 1:
                time.sleep(wait_time)

            # Prüfen ob neue Inhalte geladen wurden
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and i > 2:  # Nach 3 Versuchen ohne Änderung beenden
                logger.info(f"Keine neuen Inhalte nach {i + 1} Scroll-Versuchen - beende vorzeitig")
                break
            last_height = new_height

        logger.info("Scrollen beendet")

    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """Wartet auf ein Element mit CSS-Selektor"""
        if not self.wait:
            return False

        timeout = timeout or self.explicit_wait

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except Exception as e:
            logger.warning(f"Element '{selector}' nicht gefunden nach {timeout}s: {e}")
            return False

    def click_element_safe(self, selector: str) -> bool:
        """Sicheres Klicken auf ein Element"""
        if not self.driver:
            return False

        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script("arguments[0].click();", element)
            logger.debug(f"Element '{selector}' erfolgreich geklickt")
            return True
        except Exception as e:
            logger.warning(f"Fehler beim Klicken auf '{selector}': {e}")
            return False