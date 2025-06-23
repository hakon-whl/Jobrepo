#!/usr/bin/env python3
import argparse
from typing import Dict, Any

from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
from projekt.backend.scrapers.xing_scraper import XingScraper
from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper
from projekt.backend.core.models import SearchCriteria


def get_test_search_criteria() -> SearchCriteria:
    """Realistische Test-Kriterien für alle Scraper."""
    return SearchCriteria(
        job_title="Praktikant",
        location="München",
        radius="20",
        discipline=""
    )


def test_scraper(name: str,
                 scraper: Any,
                 criteria: SearchCriteria,
                 max_urls: int = 3) -> Dict[str, Any]:
    """
    1) URLs sammeln
    2) Details der ersten URL extrahieren
    Gibt ein Dict mit Anzahl gefundener URLs und Detail-Erfolgsflag zurück.
    """
    disp_name = name.title()
    print(f"\n=== Testing {disp_name} ===")

    try:
        urls = scraper.get_search_result_urls(criteria)
        found = len(urls or [])
        print(f"{found} URLs gefunden, zeige bis zu {max_urls}:")
        for u in (urls or [])[:max_urls]:
            print("  ▶", u)

        detail_success = False
        if urls:
            print("\nExtrahiere Details der ersten URL...")
            detail = scraper.extract_job_details(urls[0])
            detail_success = detail is not None
            status = "Erfolgreich" if detail_success else "Fehlgeschlagen"
            print(f"Detail-Extraktion: {status}")
        else:
            print("Keine URLs → Detail-Extraktion übersprungen")

        return {"urls_found": found, "detail_success": detail_success}

    except Exception as e:
        print(f"Fehler beim Testen von {disp_name}: {e}")
        return {"urls_found": 0, "detail_success": False}


def print_summary(results: Dict[str, Dict[str, Any]]) -> None:
    """Gibt eine minimalistische Test-Zusammenfassung aus."""
    print("\n=== Zusammenfassung ===")
    for name, res in results.items():
        status = "OK" if res["detail_success"] else "FAIL"
        print(f" {name.title():15} URLs={res['urls_found']:2}  Detail={status}")


def main():
    parser = argparse.ArgumentParser(
        description="Minimaler Tester für Job-Scraper"
    )
    parser.add_argument(
        "-s", "--scraper",
        choices=["stepstone", "xing", "stellenanzeigen"],
        help="Einzelnen Scraper testen"
    )
    args = parser.parse_args()

    criteria = get_test_search_criteria()
    runners = {
        "stepstone": StepstoneScraper,
        "xing": XingScraper,
        "stellenanzeigen": StellenanzeigenScraper,
    }

    to_run = [args.scraper] if args.scraper else runners.keys()
    results: Dict[str, Dict[str, Any]] = {}

    for key in to_run:
        cls = runners[key]
        scraper = cls()
        results[key] = test_scraper(key, scraper, criteria, max_urls=3)
        scraper.close_client()

    print_summary(results)


if __name__ == "__main__":
    main()