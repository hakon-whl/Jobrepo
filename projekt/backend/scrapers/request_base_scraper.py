from abc import ABC
from typing import Dict, Optional, Any, List
import httpx
import time
import random
import logging
import os

from projekt.backend.core.config import get_site_config_by_string, USER_AGENTS, app_config

logger = logging.getLogger(__name__)


class RequestBaseScraper(ABC):
    def __init__(self, site_name: str):
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)

        self.max_retries = getattr(app_config.scraping, 'max_retries', 3)
        self.retry_delay_base = getattr(app_config.scraping, 'retry_delay_base', 2.0)
        self.retry_delay_max = getattr(app_config.scraping, 'retry_delay_max', 30.0)
        self.retry_on_status_codes = getattr(app_config.scraping, 'retry_on_status_codes', [429, 503, 502, 500])

        self.request_timeout = getattr(app_config.scraping, 'request_timeout', 30.0)

        self.page_request_delay_min = getattr(app_config.scraping, 'page_request_delay_min', 2.0)
        self.page_request_delay_max = getattr(app_config.scraping, 'page_request_delay_max', 5.0)
        self.item_request_delay_min = getattr(app_config.scraping, 'item_request_delay_min', 1.0)
        self.item_request_delay_max = getattr(app_config.scraping, 'item_request_delay_max', 3.0)

        self.user_agent_rotation_chance = getattr(app_config.scraping, 'user_agent_rotation_chance', 0.1)

        self.use_proxies = getattr(app_config.scraping, 'use_proxies', False)
        self.proxy_list_path = getattr(app_config.scraping, 'proxy_list_path', 'proxies.txt')
        self._proxies: List[str] = []

        if self.use_proxies:
            self._load_proxies()

        self.base_url = self.config.get("base_url", "")
        self.http_client = None

        self.open_client()

    def _load_proxies(self) -> None:
        """Lädt Proxies aus einer Textdatei."""
        try:
            full_path = os.path.join(getattr(app_config.paths, 'logs_dir', './logs'), self.proxy_list_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.proxy_list_path)
                if not os.path.exists(full_path):
                    full_path = os.path.join(getattr(app_config.paths, 'ROOT_DIR', './'), self.proxy_list_path)

            with open(full_path, 'r', encoding='utf-8') as f:
                self._proxies = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            if not self._proxies:
                self.use_proxies = False
        except:
            self.use_proxies = False

    def _construct_search_url(self, template_path: str, params: Dict[str, Any]) -> str:
        """Konstruiert URL aus Template und Parametern"""
        path = template_path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", str(value))

        full_url = self.base_url + path
        return full_url

    def open_client(self) -> None:
        """Öffnet HTTP-Client falls noch nicht aktiv"""
        if self.http_client:
            return
        self._setup_client()

    def _setup_client(self) -> None:
        """Konfiguriert und startet den HTTP-Client"""
        try:
            headers = self.config.get("headers", {}).copy()
            if not any(k.lower() == 'user-agent' for k in headers.keys()):
                headers['User-Agent'] = random.choice(USER_AGENTS)

            client_kwargs = {
                'headers': headers,
                'timeout': self.request_timeout,
                'follow_redirects': True
            }

            if self.use_proxies and self._proxies:
                selected_proxy = random.choice(self._proxies)
                client_kwargs['proxies'] = {
                    "http://": selected_proxy,
                    "https://": selected_proxy
                }
            elif self.use_proxies and not self._proxies:
                self.use_proxies = False

            self.http_client = httpx.Client(**client_kwargs)

        except Exception as e:
            logger.error(f"HTTP-Client Setup fehlgeschlagen: {e}")
            self.http_client = None

    def _apply_anti_bot_measures(self, is_page_request: bool = False) -> None:
        """Wendet Anti-Bot-Maßnahmen an"""
        if not self.http_client:
            return

        if "headers" in self.config:
            user_agent_keys = [k for k in self.http_client.headers.keys()
                               if k.lower() == 'user-agent']
            if user_agent_keys and random.random() < self.user_agent_rotation_chance:
                new_user_agent = random.choice(USER_AGENTS)
                self.http_client.headers[user_agent_keys[0]] = new_user_agent

        if is_page_request:
            delay = random.uniform(self.page_request_delay_min, self.page_request_delay_max)
        else:
            delay = random.uniform(self.item_request_delay_min, self.item_request_delay_max)

        site_delay_modifier = self.config.get("delay_modifier", 1.0)
        delay *= site_delay_modifier

        time.sleep(delay)

    def get_html_content(self, url: str, is_page_request: bool = False) -> Optional[str]:
        """Lädt HTML-Inhalt von einer URL"""
        if not self.http_client:
            self.open_client()

        if not self.http_client:
            return None

        for attempt in range(self.max_retries):
            try:
                self._apply_anti_bot_measures(is_page_request)

                response = self.http_client.get(url)
                response.raise_for_status()

                try:
                    content = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    content = response.text

                return content

            except httpx.HTTPStatusError as e:
                if e.response.status_code in self.retry_on_status_codes:
                    backoff_time = min(
                        self.retry_delay_max,
                        self.retry_delay_base * (2 ** attempt) + random.uniform(1, 5)
                    )
                    time.sleep(backoff_time)
                elif e.response.status_code == 404:
                    return None
                else:
                    logger.error(f"HTTP Fehler {e.response.status_code}: {url}")
                    return None

            except httpx.RequestError:
                backoff_time = min(
                    self.retry_delay_max,
                    self.retry_delay_base * (attempt + 1) + random.uniform(0.5, 2)
                )
                time.sleep(backoff_time)

            except Exception:
                time.sleep(self.retry_delay_base)

        logger.error(f"Alle Versuche für URL fehlgeschlagen: {url}")
        return None

    def close_client(self) -> None:
        """Schließt den HTTP-Client"""
        if self.http_client:
            try:
                self.http_client.close()
                self.http_client = None
            except Exception:
                pass