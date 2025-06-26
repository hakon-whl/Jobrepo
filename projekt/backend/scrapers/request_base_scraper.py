from abc import ABC
import requests
import random
import time
from typing import Optional
from projekt.backend.core.config import app_config


class RequestBaseScraper(ABC):
    def __init__(self, site_name: str):
        self.site_name = site_name
        cfg = app_config.scraping

        self.page_request_delay_min = cfg.page_request_delay_min
        self.page_request_delay_max = cfg.page_request_delay_max

        self.max_retries = cfg.max_retries
        self.retry_delay_base = cfg.retry_delay_base
        self.retry_delay_max = cfg.retry_delay_max

        self.request_timeout = cfg.request_timeout

        self.legit_job_counter = 0
        self.max_jobs_to_prozess_session = cfg.max_jobs_to_prozess_session

        self.session: Optional[requests.Session] = None

    def open_client(self) -> None:
        self.session = requests.Session()

        # User-Agent-Rotation für bessere Anonymität
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]

        self.session.headers.update({
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        print(f"HTTP-Client für {self.site_name} initialisiert (ohne Proxies)")

    def get_html_content(self, url: str, **kwargs) -> str:
        if not self.session:
            raise RuntimeError("Client nicht initialisiert. Rufe open_client() auf.")

        # Zufällige Verzögerung zwischen Requests
        delay = random.uniform(
            self.page_request_delay_min,
            self.page_request_delay_max
        )
        time.sleep(delay)

        # Retry-Logic
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(
                    url,
                    timeout=self.request_timeout,
                    **kwargs
                )
                resp.raise_for_status()
                return resp.text

            except Exception as e:
                print(f"Attempt {attempt} fehlgeschlagen für {url}: {e}")
                if attempt >= self.max_retries:
                    raise

                # Exponential backoff
                backoff = min(
                    self.retry_delay_base * (2 ** (attempt - 1)),
                    self.retry_delay_max
                )
                print(f"Warte {backoff:.2f}s vor nächstem Versuch...")
                time.sleep(backoff)

        raise RuntimeError("get_html_content: Alle Versuche fehlgeschlagen")

    def close_client(self) -> None:
        if self.session:
            self.session.close()
            self.session = None
            print(f"HTTP-Client für {self.site_name} geschlossen")