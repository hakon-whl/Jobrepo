from stepstone_scraper import StepstoneScraper
import time


def main():
    stepstone_scraper = StepstoneScraper()

    search_criteria_stepstone = {
        "jobTitle": "Softwareentwickler",
        "location": "Muenchen",
        "radius": "50",
        "discipline": "IT",
    }

    print(f"Suche Job-URLs auf StepStone für: {search_criteria_stepstone}")
    start_time = time.time()
    job_urls = stepstone_scraper.get_search_result_urls(search_criteria_stepstone)
    end_time = time.time()

    print(f"\nSuche abgeschlossen in {end_time - start_time:.2f} Sekunden")
    print(f"{len(job_urls)} Job-URLs gefunden:")

    for i, url in enumerate(job_urls):
        if i < 4:
            print(url)
        elif i == 3:
            print(f"... und {len(job_urls) - 3} weitere.")
            break

    if job_urls:
        print(f"\nExtrahiere Details für die erste gefundene URL: {job_urls[0]}")
        start_detail_time = time.time()
        details = stepstone_scraper.extract_job_details(job_urls[0])
        end_detail_time = time.time()

        print(f"Details extrahiert in {end_detail_time - start_detail_time:.2f} Sekunden")

        if details:
            print(f"\nTitel: {details.get('title')}")
            print(f"URL: {details.get('url')}")
            raw_text = details.get('raw_text', '')
            print(f"Text (erste 300 Zeichen): {raw_text[:300]}...")
            print(f"Gesamtlänge des Textes: {len(raw_text)} Zeichen")
        else:
            print("Keine Details extrahiert.")

    # Schließe den Client ordnungsgemäß
    stepstone_scraper.close_client()
    print("Scraping abgeschlossen.")


if __name__ == "__main__":
    # Erstelle die Verzeichnisstruktur, falls sie nicht existiert
    import os

    os.makedirs("app/core", exist_ok=True)
    os.makedirs("app/utils", exist_ok=True)
    os.makedirs("app/scrapers", exist_ok=True)

    # Schreibe die (leeren) __init__.py Dateien, damit Python die Ordner als Pakete erkennt
    open("app/__init__.py", 'a').close()
    open("app/core/__init__.py", 'a').close()
    open("app/utils/__init__.py", 'a').close()
    open("app/scrapers/__init__.py", 'a').close()

    # Führe das Beispiel aus
    main()
