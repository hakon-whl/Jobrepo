from abc import ABC
from typing import Dict, Optional, Any
import httpx
import time
import random
from projekt.backend.core.config import get_site_config_by_string, USER_AGENTS

class RequestBaseScraper(ABC):
    def __init__(self, site_name: str):
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)
        self.max_retries = self.config.get("max_retries")
        self.retry_delay = self.config.get("retry_delay")
        self.timeout = self.config.get("timeout")
        self.base_url = self.config.get("base_url", "")
        self.http_client = None

        self.open_client()

    def _construct_search_url(self, template_path: str, params: Dict[str, Any]) -> str:
        path = template_path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", str(value))
        return self.base_url + path

    def open_client(self) -> None:
        if self.http_client:
            return
        self._setup_client()

    def _setup_client(self) -> None:
        """Konfiguriert und startet den HTTP-Client"""
        try:
            self.http_client = httpx.Client(
                headers=self.config.get("headers", {}),
                timeout=self.timeout
            )
            print(f"HTTP-Client erfolgreich gestartet für {self.site_name_str}")
        except Exception as e:
            print(f"Fehler beim Starten des HTTP-Clients: {e}")
            self.http_client = None

    def _apply_anti_bot_measures(self) -> None:
        """Wendet Anti-Bot-Maßnahmen an (User-Agent, Delays)"""
        if "headers" in self.config:
            user_agent_keys = [k for k in self.http_client.headers.keys()
                               if k.lower() == 'user-agent']
            if user_agent_keys:
                self.http_client.headers[user_agent_keys[0]] = random.choice(USER_AGENTS)

        delay = random.uniform(1.0, self.config.get("randome_max"))
        time.sleep(delay)

    def get_html_content(self, url: str) -> Optional[str]:
        if not self.http_client:
            self.open_client()

        if not self.http_client:
            print(f"Kein aktiver Client zum Laden von {url}")
            return None

        for attempt in range(self.max_retries):
            try:
                print(f"Versuch {attempt + 1}/{self.max_retries}: HTML von {url} für {self.site_name_str} abrufen...")

                self._apply_anti_bot_measures()

                response = self.http_client.get(url)
                response.raise_for_status()

                try:
                    return response.content.decode("utf-8")
                except UnicodeDecodeError:
                    return response.text

            except httpx.HTTPStatusError as e:
                print(f"HTTP Fehler beim Abrufen von {url}: {e.response.status_code}")
                if e.response.status_code in [429, 403, 503]:
                    backoff_time = self.retry_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"Mögliches Rate Limiting. Warte {backoff_time:.2f} Sekunden...")
                    time.sleep(backoff_time)

            except httpx.RequestError as e:
                print(f"Netzwerkfehler beim Abrufen von {url}: {e}")
                backoff_time = self.retry_delay
                print(f"Warte {backoff_time:.2f} Sekunden vor dem nächsten Versuch...")
                time.sleep(backoff_time)

            except Exception as e:
                print(f"Unerwarteter Fehler beim Abrufen von {url}: {e}")
                time.sleep(self.retry_delay)

        print(f"Alle {self.max_retries} Versuche für {url} fehlgeschlagen")
        return None

    def close_client(self) -> None:
        if self.http_client:
            try:
                self.http_client.close()
                self.http_client = None
                print(f"HTTP-Client erfolgreich geschlossen für {self.site_name_str}")
            except Exception as e:
                print(f"Fehler beim Schließen des HTTP-Clients: {e}")
        else:
            print("Kein aktiver Client zum Schließen vorhanden")