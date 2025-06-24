from abc import ABC
from typing import Dict, Optional, Any
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from projekt.backend.core.config import get_site_config_by_string, USER_AGENTS, app_config

logger = logging.getLogger(__name__)


class SeleniumBaseScraper(ABC):

    def __init__(self, site_name: str, headless: bool = True):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)

        self.emulate_mobile = getattr(app_config.scraping, 'selenium_emulate_mobile_default', False)
        self.wait_time = getattr(app_config.scraping, 'selenium_wait_time_default', 2.0)
        self.default_width = getattr(app_config.scraping, 'selenium_window_width_default', 1200)
        self.default_height = getattr(app_config.scraping, 'selenium_window_height_default', 800)

        self.scroll_iterations = getattr(app_config.scraping, 'selenium_scroll_iterations_default', 3)
        self.scroll_wait_time = getattr(app_config.scraping, 'selenium_scroll_wait_time_default', 2.0)

        self.page_load_timeout = getattr(app_config.scraping, 'page_load_timeout', 30.0)
        self.implicit_wait = getattr(app_config.scraping, 'implicit_wait', 10.0)
        self.explicit_wait = getattr(app_config.scraping, 'explicit_wait', 10.0)
        self.page_delay_min = getattr(app_config.scraping, 'page_delay_min', 1.0)
        self.page_delay_max = getattr(app_config.scraping, 'page_delay_max', 3.0)

        self.max_retries = getattr(app_config.scraping, 'max_retries', 3)
        self.retry_delay_base = getattr(app_config.scraping, 'retry_delay_base', 2.0)
        self.retry_delay_max = getattr(app_config.scraping, 'retry_delay_max', 30.0)

        self.user_agent_rotation_chance = getattr(app_config.scraping, 'user_agent_rotation_chance', 0.1)

        self.base_url = self.config.get("base_url", "")

    def _construct_search_url(self, template_path: str, params: Dict[str, Any]) -> str:
        """Ersetzt Platzhalter in einem URL-Template mit Parametern"""
        if not template_path:
            return ""

        path = template_path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", str(value))

        full_url = self.base_url + path
        return full_url

    def get_html_content(self) -> Optional[str]:
        """Gibt den HTML-Inhalt der aktuellen Seite zurück"""
        if not self.driver:
            return None

        try:
            html_content = self.driver.page_source
            return html_content
        except Exception:
            return None

    def open_client(self, width: int = None, height: int = None) -> None:
        """Öffnet den Selenium-Client falls noch nicht aktiv"""
        if self.driver:
            return

        width = width or self.default_width
        height = height or self.default_height

        self._setup_driver(width=width, height=height)

    def close_client(self) -> None:
        """Schließt den Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
                self.wait = None

    def _setup_driver(self, width: int = 400, height: int = 900) -> None:
        """Konfiguriert und startet den Chrome WebDriver"""
        chrome_options = Options()

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--window-size={width},{height}")

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
            if random.random() < self.user_agent_rotation_chance:
                random_ua = random.choice(USER_AGENTS)
                chrome_options.add_argument(f"--user-agent={random_ua}")

        site_chrome_options = self.config.get("chrome_options", [])
        for option in site_chrome_options:
            chrome_options.add_argument(option)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.set_window_size(width, height)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)

            self.wait = WebDriverWait(self.driver, self.explicit_wait)

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            time.sleep(self.wait_time)

        except Exception as e:
            logger.error(f"WebDriver Setup fehlgeschlagen: {e}")
            self.driver = None
            self.wait = None

    def load_url(self, url: str) -> bool:
        """Lädt eine URL im Browser mit Retry-Logik."""
        if not self.driver:
            self.open_client()

        if not self.driver:
            return False

        for attempt in range(self.max_retries):
            try:
                self.driver.get(url)

                delay = random.uniform(self.page_delay_min, self.page_delay_max)
                time.sleep(delay)

                return True

            except Exception as e:
                if attempt < self.max_retries - 1:
                    backoff_time = min(
                        self.retry_delay_max,
                        self.retry_delay_base * (2 ** attempt) + random.uniform(1, 5)
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(f"URL konnte nicht geladen werden: {url}")
        return False

    def scroll_to_bottom(self, custom_iterations: int = None, custom_wait: float = None) -> None:
        """Scrollt mehrfach zum Ende der Seite"""
        if not self.driver:
            return

        iterations = custom_iterations or self.scroll_iterations
        wait_time = custom_wait or self.scroll_wait_time

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(iterations):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if i < iterations - 1:
                time.sleep(wait_time)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and i > 2:
                break
            last_height = new_height