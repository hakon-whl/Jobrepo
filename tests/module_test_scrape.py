from projekt.backend.core.models import SearchCriteria
from projekt.backend.scrapers.stepstone_scraper import StepStoneScraper
from projekt.backend.scrapers.xing_scraper import XingScraper
from bs4 import BeautifulSoup
import re

def main():
    criteria = SearchCriteria(
        job_title="Data Scientist",
        location="München",
        radius="10",
    )

    print("StepStone Scraper")
    stepstone = StepStoneScraper()
    stepstone.open_client()

    url_ss = stepstone.build_search_url(criteria)
    print("Suche StepStone mit URL:", url_ss)

    max_pages = stepstone.get_max_pages(url_ss)
    print("StepStone Max Seiten:", max_pages)

    urls_ss = stepstone.extract_job_urls(url_ss)
    print(f"StepStone gefundene Job-Links (Seite 1): {len(urls_ss)}")
    for link in urls_ss[:5]:
        print(" -", link)

    print("StepStone: extrahiere Job-Details (max. 3):")
    for idx, link in enumerate(urls_ss[:3], start=1):
        details = stepstone.extract_job_details_scraped(link)
        if details is None:
            print(f"MaxJobs erreicht bei Job #{idx}, breche ab.")
            break
        print(f"Job #{idx}")
        print(" Titel:", details.title)
        snippet = details.raw_text[:100].replace("\n", " ")
        print(" Snippet:", snippet, "...")

    stepstone.close_client()

    print("Xing Scraper")
    xing = XingScraper()
    xing.open_client()

    url_x = xing.build_search_url(criteria)
    print("Suche Xing mit URL:", url_x)
    if not xing.load_url(url_x):
        print("Suchseite konnte nicht geladen werden, breche ab.")
        xing.close_client()
        return

    html = xing.get_html_content()
    soup = BeautifulSoup(html, "html.parser")
    class_string = xing.config["max_job_amount"]
    selector = "." + ".".join(class_string.split())
    el = soup.select_one(selector)
    if el and el.get_text(strip=True):
        text = el.get_text(strip=True)
        digits = re.sub(r"[^\d]", "", text)
        total_jobs = int(digits) if digits else 0
    else:
        total_jobs = 0
    print("Xing TotalJobs:", total_jobs)

    jobs_per_load = xing.config.get("jobs_per_lazyload", 20)
    iterations = int(total_jobs / jobs_per_load)
    xing.get_to_bottom(iterations)
    urls_x = xing.extract_job_urls()
    print(f"\nXing gefundene Job-Links: {len(urls_x)}")
    for link in urls_x[:5]:
        print(" -", link)

    print("Xing: extrahiere Job-Details (max. 3):")
    for idx, link in enumerate(urls_x[:3], start=1):
        details = xing.extract_job_details_scraped(link)
        if details is None:
            print(f"MaxJobs erreicht bei Job #{idx}, breche ab.")
            break
        print(f"Job #{idx}")
        print(" Titel:", details.title)
        snippet = details.raw_text[:100].replace("\n", " ")
        print(" Snippet:", snippet, "...")

    xing.close_client()

if __name__ == "__main__":
    main()