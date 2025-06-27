import time
from typing import List
from urllib.parse import quote_plus, urljoin

from httpcore import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from .selenium_base_scraper import SeleniumBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetailsScraped, SearchCriteria, JobSource
from projekt.backend.core.config import app_config
import logging

logger = logging.getLogger(__name__)


class XingScraper(SeleniumBaseScraper):
    def __init__(self):
        super().__init__("Xing")
        self.config = app_config.site_configs[JobSource.XING.value]
        self.base_url = self.config["base_url"]

        sc = app_config.scraping
        self.scroll_wait_time = sc.selenium_scroll_wait_time_default / 2
        self.scroll_load_timeout = sc.request_timeout / 3
        self.scroll_stable_checks = 1

    def build_search_url(self, search_criteria: SearchCriteria) -> str:
        params = search_criteria.to_xing_params()

        job_title_encoded = quote_plus(params["jobTitle"])
        location_encoded = quote_plus(params["location"])

        search_path = self.config["search_url_template"].format(
            jobTitle=job_title_encoded,
            location=location_encoded,
            radius=params["radius"],
            discipline=params.get("discipline", ""),
        )
        return urljoin(self.base_url, search_path)

    def extract_job_urls(self) -> List[str]:
        html = self.get_html_content()
        soup = BeautifulSoup(html, "html.parser")
        cfg = self.config["job_url"]
        selector = cfg["selector"]
        attribute = cfg["attribute"]

        links = soup.select(selector)
        urls = {
            urljoin(self.base_url, a.get(attribute))
            for a in links
            if a.get(attribute)
        }
        return list(urls)

    def extract_job_details_scraped(self, job_url: str) -> JobDetailsScraped | None:
        if self.legit_job_counter >= app_config.scraping.max_jobs_to_prozess_session:
            if not self.close_client:
                self.close_client()
            return None
        try:
            self.load_url(job_url)
            html = self.get_html_content()
            soup = BeautifulSoup(html, "html.parser")

            title_el = soup.select_one(self.config["job_titel_selector"])
            title = title_el.get_text(strip=True) if title_el else "Titel nicht gefunden"

            content_el = soup.select_one(self.config["job_content_selector"])
            raw_text = ""
            if content_el:
                for tag in content_el(["script", "style"]):
                    tag.decompose()
                raw_text = content_el.get_text(strip=True)

            return JobDetailsScraped(
                title=title,
                raw_text=raw_text,
                url=job_url,
                source=JobSource.STEPSTONE
            )

        except Exception as e:
            return JobDetailsScraped(
                title="Fehler beim Extrahieren",
                raw_text=f"Konnte Details nicht extrahieren: {e}",
                url=job_url,
                source=JobSource.STEPSTONE
            )

    def get_to_bottom(self, scroll_iterations: int) -> None:
        if not self.driver:
            return

        body = self.driver.find_element(By.TAG_NAME, "body")
        last_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight;"
        )
        stable = 0

        for _ in range(scroll_iterations):
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            )
            body.send_keys(Keys.END)

            try:
                WebDriverWait(self.driver, self.scroll_load_timeout).until(
                    lambda d: d.execute_script(
                        "return document.documentElement.scrollHeight;"
                    ) > last_height
                )
                last_height = self.driver.execute_script(
                    "return document.documentElement.scrollHeight;"
                )
                stable = 0
            except TimeoutException:
                stable += 1

            time.sleep(self.scroll_wait_time)

            if stable >= self.scroll_stable_checks:
                logger.info(
                    f"[{self.site_name}] get_to_bottom: "
                    "keine neuen Inhalte, breche ab"
                )
                break