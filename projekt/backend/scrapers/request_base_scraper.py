from abc import ABC
from typing import Dict, Optional, Any
import httpx
import time
import random
import logging
from projekt.backend.core.config import get_site_config_by_string, USER_AGENTS, app_config

logger = logging.getLogger(__name__)


class RequestBaseScraper(ABC):
    def __init__(self, site_name: str):
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)

        # Globale Scraping-Konfiguration
        self.max_retries = app_config.scraping.max_retries
        self.retry_delay = app_config.scraping.retry_delay
        self.timeout = app_config.scraping.timeout

        # Neue Delay-Konfigurationen
        self.page_delay_min = getattr(app_config.scraping, 'page_delay_min', 2.0)
        self.page_delay_max = getattr(app_config.scraping, 'page_delay_max', 5.0)
        self.request_delay_min = getattr(app_config.scraping, 'request_delay_min', 1.0)
        self.request_delay_max = getattr(app_config.scraping, 'request_delay_max', 3.0)

        # Site-spezifische Konfiguration
        self.base_url = self.config.get("base_url", "")
        self.http_client = None

        logger.info(f"RequestBaseScraper initialisiert für {site_name}")
        self.open_client()

    def _construct_search_url(self, template_path: str, params: Dict[str, Any]) -> str:
        """Konstruiert URL aus Template und Parametern"""
        path = template_path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", str(value))

        full_url = self.base_url + path
        logger.debug(f"Such-URL konstruiert: {full_url}")
        return full_url

    def open_client(self) -> None:
        """Öffnet HTTP-Client falls noch nicht aktiv"""
        if self.http_client:
            return
        self._setup_client()

    def _setup_client(self) -> None:
        """Konfiguriert und startet den HTTP-Client"""
        try:
            # Basis-Headers mit zufälligem User-Agent
            headers = self.config.get("headers", {}).copy()
            if not any(k.lower() == 'user-agent' for k in headers.keys()):
                headers['User-Agent'] = random.choice(USER_AGENTS)

            self.http_client = httpx.Client(
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True
            )
            logger.info(f"HTTP-Client erfolgreich gestartet für {self.site_name_str}")
        except Exception as e:
            logger.error(f"Fehler beim Starten des HTTP-Clients: {e}")
            self.http_client = None

    def _apply_anti_bot_measures(self, is_page_request: bool = False) -> None:
        """Wendet Anti-Bot-Maßnahmen an (User-Agent, Delays)"""
        if not self.http_client:
            return

        # User-Agent rotieren
        if "headers" in self.config:
            user_agent_keys = [k for k in self.http_client.headers.keys()
                               if k.lower() == 'user-agent']
            if user_agent_keys and random.random() < 0.3:  # 30% Chance auf Rotation
                new_user_agent = random.choice(USER_AGENTS)
                self.http_client.headers[user_agent_keys[0]] = new_user_agent
                logger.debug(f"User-Agent gewechselt zu: {new_user_agent[:50]}...")

        # Intelligente Delays
        if is_page_request:
            delay = random.uniform(self.page_delay_min, self.page_delay_max)
        else:
            delay = random.uniform(self.request_delay_min, self.request_delay_max)

        # Site-spezifische Delay-Modifikation
        site_delay_modifier = self.config.get("delay_modifier", 1.0)
        delay *= site_delay_modifier

        logger.debug(f"Anti-Bot-Delay: {delay:.2f} Sekunden")
        time.sleep(delay)

    def get_html_content(self, url: str, is_page_request: bool = False) -> Optional[str]:
        """Lädt HTML-Inhalt von einer URL"""
        if not self.http_client:
            self.open_client()

        if not self.http_client:
            logger.error(f"Kein aktiver Client zum Laden von {url}")
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Versuch {attempt + 1}/{self.max_retries}: HTML von {url} für {self.site_name_str} abrufen...")

                self._apply_anti_bot_measures(is_page_request)

                response = self.http_client.get(url)
                response.raise_for_status()

                # Encoding-Behandlung
                try:
                    content = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    content = response.text

                logger.info(f"HTML erfolgreich abgerufen: {len(content)} Zeichen")
                return content

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP Fehler beim Abrufen von {url}: {e.response.status_code}")
                if e.response.status_code in [429, 403, 503]:
                    backoff_time = self.retry_delay * (2 ** attempt) + random.uniform(1, 5)
                    logger.warning(f"Rate Limiting erkannt. Warte {backoff_time:.2f} Sekunden...")
                    time.sleep(backoff_time)
                elif e.response.status_code == 404:
                    logger.error(f"Seite nicht gefunden (404): {url}")
                    return None

            except httpx.RequestError as e:
                logger.warning(f"Netzwerkfehler beim Abrufen von {url}: {e}")
                backoff_time = self.retry_delay * (attempt + 1)
                logger.info(f"Warte {backoff_time:.2f} Sekunden vor dem nächsten Versuch...")
                time.sleep(backoff_time)

            except Exception as e:
                logger.error(f"Unerwarteter Fehler beim Abrufen von {url}: {e}")
                time.sleep(self.retry_delay)

        logger.error(f"Alle {self.max_retries} Versuche für {url} fehlgeschlagen")
        return None

    def close_client(self) -> None:
        """Schließt den HTTP-Client"""
        if self.http_client:
            try:
                self.http_client.close()
                self.http_client = None
                logger.info(f"HTTP-Client erfolgreich geschlossen für {self.site_name_str}")
            except Exception as e:
                logger.error(f"Fehler beim Schließen des HTTP-Clients: {e}")
        else:
            logger.debug("Kein aktiver Client zum Schließen vorhanden")