import os

from projekt.backend.utils.html_parser import (
    extract_text_from_selector,
    extract_attribute_from_selector,
)
from projekt.backend.utils.pdf_utils import markdown_to_pdf, merge_pdfs_by_rating
from projekt.backend.core.models import JobDetailsScraped, JobDetailsAi
from projekt.backend.core.config import JobSource, AIModel

SAMPLE_HTML = """
<div id="content">
Dies ist der   Haupttext.
Er hat mehrere     Leerzeichen.
</div>
<ul class="nav-links">
  <li><a href="/home">Home</a></li>
  <li><a href="/about">Über uns</a></li>
  <li><a href="/contact">Kontakt</a></li>
</ul>
"""

COVER_LETTERS = {
    "Alice": (
        """
**Alice Mustermann**
Musterstraße 12  
80331 München  
alice.mustermann@email.de  
0170 1234567

**Hochschule München**  
Personalabteilung  
Herrn/Frau [Name des Ansprechpartners]  
Lothstraße 13c  
80335 München

München, 26. Juni 2025

**Bewerbung als Werkstudentin im Bereich Informationstechnologie**

Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Stellenausschreibung auf Ihrer Karriereseite gelesen.
Ich bringe …

Mit freundlichen Grüßen

**Alice Mustermann**
        """,
        6
    ),
    "Bob": (
        """
**Bob Beispielmann**  
Beispielweg 5  
81675 München  
bob.beispielmann@email.de  
0171 7654321

**Hochschule München**  
Personalabteilung  
Herrn/Frau [Name des Ansprechpartners]  
Blumenstraße 7  
80331 München

München, 26. Juni 2025

**Bewerbung als Werkstudent im Bereich IT-Support und Systemadministration**

Sehr geehrte Damen und Herren,

als engagierter Student der Wirtschaftsinformatik bringe ich …

Mit freundlichen Grüßen

**Bob Beispielmann**
        """,
        9
    )
}

def main():
    print("=== Extrahierter Text aus #content ===")
    text = extract_text_from_selector(SAMPLE_HTML, "#content")
    print(text or "<kein Text gefunden>")
    print()

    print("=== Extrahierte Links aus .nav-links a (href) ===")
    links = extract_attribute_from_selector(SAMPLE_HTML, ".nav-links a", "href")
    for url in links or []:
        print("-", url)
    print()

    base_dir = os.getcwd()
    out_dir = os.path.join(base_dir, "pdf_output")
    os.makedirs(out_dir, exist_ok=True)

    scraped = JobDetailsScraped(
        title="Werkstudent Backend-Entwicklung",
        raw_text="Irrelevant für diesen Test.",
        url="https://example.com/job/42",
        source=JobSource.STEPSTONE,
    )

    print("=== Erzeuge PDFs für Anschreiben ===")
    for name, (letter_md, rating) in COVER_LETTERS.items():
        ai_job = JobDetailsAi(
            scraped=scraped,
            rating=rating,
            formatted_text=scraped.raw_text,
            cover_letters=letter_md,
            ai_model_used=AIModel.GEMINI_FLASH,
        )
        success = markdown_to_pdf(ai_job, out_dir, rating)
        fname = ai_job.get_output_filename()
        status = "OK" if success else "FEHLER"
        print(f"{name}: {status} → {os.path.join('pdf_output', fname)}")
    print()

    merged_path = os.path.join(out_dir, "merged_coverletters.pdf")
    ok = merge_pdfs_by_rating(out_dir, merged_path)
    print("=== Merge aller PDFs nach Rating ===")
    if ok:
        print("Gemeinsame PDF gespeichert in:", os.path.join("pdf_output", "merged_coverletters.pdf"))
    else:
        print("FEHLER beim Mergen der PDFs")

if __name__ == "__main__":
    main()