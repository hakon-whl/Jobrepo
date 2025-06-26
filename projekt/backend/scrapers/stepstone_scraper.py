from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from typing import List
import re
from request_base_scraper import RequestBaseScraper
from projekt.backend.core.models import JobSource, SearchCriteria, JobDetailsScraped
from projekt.backend.core.config import app_config


class StepStoneScraper(RequestBaseScraper):
    def __init__(self):
        super().__init__("StepStone")
        self.config = app_config.site_configs[JobSource.STEPSTONE.value]
        self.base_url = self.config["base_url"]

    def build_search_url(self, search_criteria: SearchCriteria, initial_page: int = 1) -> str:
        params = search_criteria.to_stepstone_params()

        job_title_encoded = quote_plus(params["jobTitle"])
        location_encoded = quote_plus(params["location"])

        search_path = self.config["search_url_template"].format(
            jobTitle=job_title_encoded,
            location=location_encoded,
            radius=params["radius"],
            discipline=params.get("discipline", ""),
            seite=initial_page
        )

        return urljoin(self.base_url, search_path)

    def extract_job_urls(self, html_content: str) -> List[str]:
        soup = BeautifulSoup(html_content, 'html.parser')
        job_urls = []

        job_url_config = self.config["job_url"]
        selector = job_url_config["selector"]
        attribute = job_url_config["attribute"]

        job_links = soup.select(selector)

        for link in job_links:
            href = link.get(attribute)
            if href:
                full_url = urljoin(self.base_url, href)
                job_urls.append(full_url)

        return list(set(job_urls))

    def get_max_pages(self, html_content: str) -> int:
        soup = BeautifulSoup(html_content, 'html.parser')
        max_page_selector = self.config["max_page_selector"]

        try:
            max_page_element = soup.select_one(max_page_selector)
            if max_page_element:
                # Extrahiere Zahlen aus dem Text
                text = max_page_element.get_text(strip=True)
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[-1])
        except Exception as e:
            print(f"Fehler beim Ermitteln der max. Seiten: {e}")

        return 1

    def extract_job_details(self, job_url: str) -> JobDetailsScraped:
        html_content = self.get_html_content(job_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        title_selector = self.config["job_titel_selector"]
        title_element = soup.select_one(title_selector)
        title = title_element.get_text(strip=True) if title_element else "Titel nicht gefunden"

        content_selector = self.config["job_content_selector"]
        content_element = soup.select_one(content_selector)

        for script in content_element(["script", "style"]):
            script.decompose()
        raw_text = content_element.get_text(separator='\n', strip=True)

        return JobDetailsScraped(
            title=title,
            raw_text=raw_text,
            url=job_url,
            source=JobSource.STEPSTONE
        )


# Verwendungsbeispiel:
if __name__ == "__main__":
    from projekt.backend.core.models import SearchCriteria

    search_criteria = SearchCriteria(
        job_title="Praktikum",
        location="München",
        radius="25",
        discipline=""
    )

    scraper = StepStoneScraper()
    try:
        scraper.open_client()
        url = scraper.build_search_url(search_criteria)
        html = scraper.get_html_content(url)
        jobs = scraper.extract_job_urls(html)
        max_page = scraper.get_max_pages(html)
        print(max_page)
        for inhalt in jobs:
            print(inhalt)
        print(scraper.extract_job_details(jobs[0]))

    finally:
        scraper.close_client()