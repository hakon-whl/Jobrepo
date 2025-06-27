import time
import random
import logging
from abc import ABC
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)

class SeleniumBaseScraper(ABC):
    def __init__(self, site_name: str):
        self.site_name = site_name
        cfg = app_config.scraping

        self.headless = True
        self.page_delay_min = cfg.page_request_delay_min
        self.page_delay_max = cfg.page_request_delay_max
        self.max_retries = cfg.max_retries
        self.retry_delay_base = cfg.retry_delay_base
        self.retry_delay_max = cfg.retry_delay_max

        self.startup_wait = cfg.selenium_wait_time_default
        self.window_width = cfg.selenium_window_width_default
        self.window_height = cfg.selenium_window_height_default

        self.legit_job_counter = 0
        self.driver: Optional[webdriver.Chrome] = None

        logger.debug(f"[{self.site_name}] SeleniumBaseScraper erstellt")

    def open_client(self) -> None:
        if self.driver:
            return

        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        if self.headless:
            opts.add_argument("--headless")
            opts.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        try:
            self.driver = webdriver.Chrome(service=service, options=opts)
            self.driver.set_window_size(self.window_width, self.window_height)
            time.sleep(self.startup_wait)
            logger.info(f"[{self.site_name}] WebDriver gestartet")
        except Exception as e:
            logger.error(f"[{self.site_name}] WebDriver Init fehlgeschlagen: {e}")
            self.driver = None

    def load_url(self, url: str) -> bool:
        logger.info(f"[{self.site_name}] Lade URL: {url}")
        for attempt in range(1, self.max_retries + 1):
            try:
                self.driver.get(url)
                time.sleep(random.uniform(
                    self.page_delay_min,
                    self.page_delay_max
                ))
                logger.info(f"[{self.site_name}] URL erfolgreich geladen")
                return True
            except Exception as e:
                logger.warning(
                    f"[{self.site_name}] Versuch {attempt} fehlgeschlagen: {e}"
                )
                if attempt == self.max_retries:
                    logger.error(f"[{self.site_name}] URL konnte nicht geladen werden: {url}")
                    return False
                backoff = min(
                    self.retry_delay_base * 2 ** (attempt - 1),
                    self.retry_delay_max
                )
                time.sleep(backoff)

    def get_html_content(self) -> Optional[str]:
        if not self.driver:
            logger.warning(f"[{self.site_name}] Kein WebDriver – kein HTML")
            return None
        return self.driver.page_source

    def close_client(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
            finally:
                self.driver = None
                logger.info(f"[{self.site_name}] WebDriver geschlossen")