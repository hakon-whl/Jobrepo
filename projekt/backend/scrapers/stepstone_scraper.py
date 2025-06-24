# stepstone_scraper.py
from typing import List, Optional
import time
import random
from .request_base_scraper import RequestBaseScraper
from bs4 import BeautifulSoup
from projekt.backend.core.models import JobDetails, SearchCriteria, JobSource
from projekt.backend.core.config import app_config
import logging

logger = logging.getLogger(__name__)


class StepstoneScraper(RequestBaseScraper):
    """StepStone Job-Scraper"""

    def __init__(self):
        super().__init__("StepStone")
        self.jobs_per_page_limit = getattr(app_config.scraping, 'jobs_per_page_limit', 100)
        self.max_pages = getattr(app_config.scraping, 'max_pages_per_site', 5)

    def get_search_result_urls(self, search_criteria: SearchCriteria) -> List[str]:
        """Sammelt Job-URLs von StepStone Suchseiten"""
        try:
            required = ["search_url_template", "job_url", "max_page_selector"]
            for key in required:
                if not self.config.get(key):
                    logger.error(f"StepStone Konfiguration fehlt: {key}")
                    return []

            params = search_criteria.to_stepstone_params()
            params["seite"] = 1

            url = self._construct_search_url(self.config["search_url_template"], params)
            html = self.get_html_content(url, is_page_request=True)
            if not html:
                logger.error("StepStone Suchseite nicht erreichbar")
                return []

            soup = BeautifulSoup(html, "lxml")

            pages_el = soup.select_one(self.config["max_page_selector"])
            if pages_el:
                try:
                    text = pages_el.get_text().rsplit(maxsplit=1)[-1]
                    available_pages = int(text)
                    total_pages = min(available_pages, self.max_pages)
                except (ValueError, IndexError):
                    total_pages = 1
            else:
                total_pages = 1

            logger.info(f"Sammle StepStone Jobs von {total_pages} Seite(n)")

            all_urls: List[str] = []
            job_conf = self.config["job_url"]
            selector = job_conf["selector"]
            attribute = job_conf["attribute"]

            def collect_page(page_num: int) -> List[str]:
                try:
                    params["seite"] = page_num
                    page_url = self._construct_search_url(self.config["search_url_template"], params)
                    html_content = self.get_html_content(page_url, is_page_request=True)

                    if not html_content:
                        return []

                    page_soup = BeautifulSoup(html_content, "lxml")
                    elements = page_soup.select(selector)

                    page_urls = []
                    for element in elements:
                        link = element.get(attribute)
                        if link:
                            if link.startswith("/"):
                                link = self.base_url + link
                            page_urls.append(link)

                    if len(page_urls) > self.jobs_per_page_limit:
                        page_urls = page_urls[:self.jobs_per_page_limit]

                    return page_urls

                except Exception as e:
                    logger.error(f"StepStone Seite {page_num} Fehler: {e}")
                    return []

            all_urls.extend(collect_page(1))

            for page_num in range(2, total_pages + 1):
                delay = random.uniform(self.page_request_delay_min, self.page_request_delay_max)
                time.sleep(delay)

                page_urls = collect_page(page_num)
                all_urls.extend(page_urls)

                if not page_urls:
                    break

            unique_urls = list(set(all_urls))

            max_total_jobs = getattr(app_config.scraping, 'max_total_jobs_per_site', 200)
            if len(unique_urls) > max_total_jobs:
                unique_urls = unique_urls[:max_total_jobs]

            logger.info(f"{len(unique_urls)} StepStone Jobs gefunden")
            return unique_urls

        except Exception as e:
            logger.error(f"StepStone URL-Sammlung fehlgeschlagen: {e}")
            return []

    def extract_job_details(self, job_page_url: str) -> Optional[JobDetails]:
        """Extrahiert Job-Details von einer StepStone Job-Seite"""
        try:
            html = self.get_html_content(job_page_url)
            if not html:
                return None

            soup = BeautifulSoup(html, "lxml")

            content_selector = self.config.get("job_content_selector", "")
            title_selector = self.config.get("job_titel_selector", "")

            if not content_selector or not title_selector:
                logger.error("StepStone Selektoren fehlen")
                return None

            content_element = soup.select_one(content_selector)
            title_element = soup.select_one(title_selector)

            raw_text = ""
            if content_element:
                raw_text = content_element.get_text(separator=' ', strip=True)
            else:
                fallback_selectors = [".job-description", "[data-testid='job-description']", ".jobad-content", "main"]
                for fallback in fallback_selectors:
                    fallback_element = soup.select_one(fallback)
                    if fallback_element:
                        raw_text = fallback_element.get_text(separator=' ', strip=True)
                        break

            job_title = ""
            if title_element:
                job_title = title_element.get_text(strip=True)
            else:
                title_fallbacks = ["h1", "title", "[data-testid='job-title']"]
                for fallback in title_fallbacks:
                    fallback_title = soup.select_one(fallback)
                    if fallback_title:
                        job_title = fallback_title.get_text(strip=True)
                        break

            if not raw_text.strip():
                raw_text = "Kein Text extrahierbar"

            if not job_title.strip():
                job_title = "Titel nicht extrahierbar"

            return JobDetails(
                title=job_title,
                title_clean="",
                raw_text=raw_text,
                url=job_page_url,
                source_site=JobSource.STEPSTONE
            )

        except Exception as e:
            logger.error(f"StepStone Job-Extraktion fehlgeschlagen: {e}")
            return None