import os
from dotenv import load_dotenv
from enum import Enum
import random

load_dotenv()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.2420.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

DEFAULT_REQUEST_DELAY_SECONDS = (2.0, 5.0)

class Site(Enum):
    STEPSTONE = "StepStone"

SITE_CONFIGS = {
    Site.STEPSTONE: {
        "base_url": "https://www.stepstone.de",
        "search_url_template": "/jobs/{jobTitle}/in-{location}?radius={radius}&di={discipline}&page={seite}",
        "headers": {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.5",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        },
        "job_url": {
            "selector": 'a[href^="/stellenangebote"]',
            "attribute": "href"
        },
        "job_content_selector": 'div[data-at="job-ad-content"]',
        "job_pages_selector": 'span[class="res-tqs0ve"]'
    }
}

def get_site_config(site_name_enum: Site) -> dict | None:
    return SITE_CONFIGS.get(site_name_enum)

def get_site_config_by_string(site_name_str: str) -> dict | None:
    try:
        site_enum_member = Site[site_name_str.upper().replace(" ", "_").replace(".","_")]
        return SITE_CONFIGS.get(site_enum_member)
    except KeyError:
        # Fallback, falls der String dem Enum.value entspricht (z.B. "StepStone")
        for site_enum, config in SITE_CONFIGS.items():
            if site_enum.value == site_name_str:
                return config
        print(f"Warnung: Keine Konfiguration für Seite '{site_name_str}' gefunden.")
        return None

