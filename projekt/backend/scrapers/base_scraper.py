from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import httpx
import time
import random
from projekt.backend.core.config import get_site_config_by_string, Site, USER_AGENTS


class BaseScraper(ABC):
    def __init__(self, site_name: str, max_retries=3, retry_delay=5, timeout=30.0):
        self.site_name_str = site_name
        self.config = get_site_config_by_string(site_name)
        if not self.config:
            raise ValueError(
                f"Keine Konfiguration für Seite '{site_name}' gefunden."
            )
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Langsamere, aber stabilere Timeout-Einstellungen
        self.http_client = httpx.Client(
            headers=self.config.get("headers"),
            timeout=timeout  # Längerer Timeout
        )
        self.base_url = self.config.get("base_url", "")

    def _fetch_html(self, url: str) -> Optional[str]:
        """Holt HTML mit Retry-Mechanismus und zufälligen Verzögerungen"""
        for attempt in range(self.max_retries):
            try:
                print(f"Versuch {attempt + 1}/{self.max_retries}: HTML von {url} für {self.site_name_str} abrufen...")
                # Rotation der User-Agents für jede Anfrage
                if "headers" in self.config and "User-Agent" in self.config["headers"]:
                    self.http_client.headers["User-Agent"] = random.choice(USER_AGENTS)

                # Zufällige Verzögerung vor dem Request (simuliert menschliches Verhalten)
                delay = random.uniform(1.0, 3.0)
                print(f"Warte {delay:.2f} Sekunden vor der Anfrage...")
                time.sleep(delay)

                response = self.http_client.get(url)
                response.raise_for_status()

                # Erfolgreich - HTML zurückgeben
                try:
                    return response.content.decode("utf-8")
                except UnicodeDecodeError:
                    return response.text

            except httpx.HTTPStatusError as e:
                print(f"HTTP Fehler beim Abrufen von {url}: {e.response.status_code} - {e.response.text[:200]}")
                if e.response.status_code in [429, 403, 503]:  # Rate limiting or forbidden
                    # Bei Rate-Limiting oder Blocking länger warten
                    backoff_time = self.retry_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"Mögliches Rate Limiting. Warte {backoff_time:.2f} Sekunden...")
                    time.sleep(backoff_time)

            except httpx.RequestError as e:
                print(f"Netzwerkfehler beim Abrufen von {url}: {e}")
                # Exponentielles Backoff mit Jitter
                backoff_time = self.retry_delay * (2 ** attempt) + random.uniform(1, 3)
                print(f"Warte {backoff_time:.2f} Sekunden vor dem nächsten Versuch...")
                time.sleep(backoff_time)

            except Exception as e:
                print(f"Unerwarteter Fehler beim Abrufen von {url}: {e}")
                time.sleep(self.retry_delay)

        print(f"Alle {self.max_retries} Versuche für {url} fehlgeschlagen")
        return None

    def _construct_search_url(
            self, template_path: str, params: Dict[str, Any]
    ) -> str:
        """Ersetzt Platzhalter in einem URL-Pfad-Template."""
        path = template_path
        for key, value in params.items():
            # Stelle sicher, dass die Platzhalter-Syntax übereinstimmt
            path = path.replace(f"{{{key}}}", str(value))
        return self.base_url + path

    def close_client(self):
        """Schließt den HTTP-Client."""
        try:
            self.http_client.close()
            print("HTTP-Client erfolgreich geschlossen.")
        except Exception as e:
            print(f"Fehler beim Schließen des HTTP-Clients: {e}")
