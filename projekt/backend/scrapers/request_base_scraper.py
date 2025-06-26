from abc import ABC
import requests
import random
import time
import asyncio
from proxybroker import Broker
from typing import List, Optional
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

        self.proxy_limit = cfg.proxy_limit
        self.proxy_countries = cfg.proxy_countries
        self.proxy_pool: List[str] = []
        self.proxy_index = 0

        self.session: Optional[requests.Session] = None

    def _find_proxies(self) -> List[str]:
        async def _async_find():
            broker = Broker(countries=self.proxy_countries)
            proxies = await broker.find_proxy(limit=self.proxy_limit)
            result = []
            for p in proxies:
                result.append(f"{p.protocol}://{p.host}:{p.port}")
            await broker.stop()
            return result

        return asyncio.run(_async_find())

    def open_client(self) -> None:
        try:
            self.proxy_pool = self._find_proxies()
            print(f"Gefundene Proxies: {len(self.proxy_pool)}")
        except Exception as e:
            print(f"Warnung: Konnte keine Proxies laden: {e}")
            self.proxy_pool = []

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        })

    def get_html_content(self, url: str, **kwargs) -> str:
        if not self.session:
            raise RuntimeError("Client nicht initialisiert. Rufe open_client() auf.")

        delay = random.uniform(
            self.page_request_delay_min,
            self.page_request_delay_max
        )
        time.sleep(delay)

        for attempt in range(1, self.max_retries + 1):
            proxy_cfg = None
            if self.proxy_pool:
                proxy_url = self.proxy_pool[self.proxy_index]
                self.proxy_index = (self.proxy_index + 1) % len(self.proxy_pool)
                proxy_cfg = {"http": proxy_url, "https": proxy_url}

            try:
                resp = self.session.get(
                    url,
                    proxies=proxy_cfg,
                    timeout=self.request_timeout,
                    **kwargs
                )
                resp.raise_for_status()
                return resp.text

            except Exception as e:
                print(f"Attempt {attempt} fehlgeschlagen: {e}")
                if attempt >= self.max_retries:
                    raise
                backoff = min(
                    self.retry_delay_base * (2 ** (attempt - 1)),
                    self.retry_delay_max
                )
                time.sleep(backoff)

        raise RuntimeError("get_html_content: Alle Versuche fehlgeschlagen")

    def close_client(self) -> None:
        if self.session:
            self.session.close()
            self.session = None

    def get_next_proxy(self) -> Optional[dict]:
        """Gibt den nächsten Proxy aus dem Pool zurück."""
        if not self.proxy_pool:
            return None
        url = self.proxy_pool[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_pool)
        return {"http": url, "https": url}