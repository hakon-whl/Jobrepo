import random
import time
import subprocess
import os

from flask import Flask, request, jsonify, send_from_directory

from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
from projekt.backend.scrapers.xing_scraper import XingScraper
from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper
from projekt.backend.utils.pdf_utils import PdfUtils

# Pfade definieren
frontend_dir = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
temp_pfs_dir = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\temp_pdfs"
build_dir = os.path.join(frontend_dir, "build")

app = Flask(__name__, static_folder=build_dir)


def setup_frontend_and_server():
    """Build das Frontend falls nötig und startet einen Server für beides"""

    # Prüfen, ob build-Verzeichnis existiert, falls nicht: neu bauen
    if not os.path.exists(build_dir) or not os.listdir(build_dir):
        print("Build-Verzeichnis nicht gefunden oder leer. Erstelle neuen Build...")
        try:
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
            print("Frontend erfolgreich gebaut.")
        except Exception as e:
            print(f"Fehler beim Bauen des Frontends: {e}")
            return False
    else:
        print(f"Verwende existierenden Frontend-Build in {build_dir}")

    return True


# API-Endpunkt mit korrektem Funktionsnamen
@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    stepstone = StepstoneScraper()
    xing = XingScraper()
    stellenanzeigen = StellenanzeigenScraper()
    text_processor = TextProcessor()
    pdf_utils = PdfUtils()
    scraper = None

    try:
        data = request.json
        job_sites_selected = data.get("jobSites", [])

        if "StepStone" in job_sites_selected:
            scraper = StepstoneScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("selectedPlz", ""),
                "radius": data.get("radius", ""),
                "discipline": data.get("discipline", "")
            }
            print("Scraper: StepStone ausgewählt.")

        elif "Xing" in job_sites_selected:
            scraper = XingScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("selectedPlz", ""),
                "radius": data.get("radius", ""),
            }
            print("Scraper: XING ausgewählt.")

        elif "Stellenanzeigen" in job_sites_selected:
            scraper = StellenanzeigenScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("selectedPlz", ""),
                "radius": data.get("radius", ""),
            }
            print("Scraper: Stellenanzeigen ausgewählt.")

        else:
            return jsonify({
                "success": False,
                "message": "Keine unterstützte Jobseite ausgewählt. Bitte wählen Sie StepStone oder XING."
            }), 400

        job_urls = []
        if scraper:
            if isinstance(scraper, StepstoneScraper):
                # ✅ VEREINFACHT: Neue Methode sammelt automatisch alle Seiten
                job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls = list(set(job_urls))  # Duplikate entfernen
                print(f"StepStone: Insgesamt {len(job_urls)} einzigartige Job-URLs gesammelt.")

            elif isinstance(scraper, XingScraper):
                page_job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls.extend(page_job_urls)
                job_urls = list(set(job_urls))

            elif isinstance(scraper, StellenanzeigenScraper):
                page_job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls.extend(page_job_urls)
                job_urls = list(set(job_urls))

            for job_url in job_urls:
                if job_url:
                    print(job_sites_selected)
                    if "StepStone" in job_sites_selected:
                        job_details = stepstone.extract_job_details(job_url)
                    if "Xing" in job_sites_selected:
                        job_details = xing.extract_job_details(job_url)
                    if "Stellenanzeigen" in job_sites_selected:
                        job_details = xing.extract_job_details(job_url)

                    if job_details:
                        job_title = job_details.get('title_clean') if job_details else None
                        print(job_title)
                        include_keywords = ["Praktikant", "Praktikum", "Trainee", "Internship", "INTERN", "Intern"]

                        if any(keyword.lower() in str(job_title).lower() for keyword in include_keywords):
                            applicant_information = {
                                "studyInfo": data.get("studyInfo", ""),
                                "interests": data.get("interests", ""),
                                "skills": data.get("skills", ""),
                            }

                            previous_cover_letter = data.get("pdfContents", "")
                            job_description = text_processor.format_job_description(job_details.get('raw_text'))
                            rating_str = text_processor.rate_job_match(job_description, applicant_information)

                            try:
                                rating_int = int(rating_str.strip())
                            except (ValueError, TypeError):
                                rating_int = 0
                                print(
                                    f"Warnung: Konnte Rating '{rating_str}' nicht in Integer konvertieren. Setze auf 0.")

                            safe_job_title_clean = job_details.get('title_clean', 'unbekannter_titel').replace(os.sep,
                                                                                                               '_').replace(
                                '/', '_').replace('\\', '_')
                            pdf_filename = f"{rating_int}_{safe_job_title_clean}.pdf"
                            full_pdf_path = os.path.join(temp_pfs_dir, pdf_filename)
                            print('Rating:' + rating_str)

                            if rating_int >= 2:
                                print(f"  Rating {rating_int} >= 6: Generiere Anschreiben mit gemini-2.0-flash-001...")
                                anschreiben = text_processor.generate_anschreiben(job_description,
                                                                                  applicant_information,
                                                                                  previous_cover_letter,
                                                                                  'gemini-2.5-flash-preview-05-20')
                                pdf_utils.markdown_to_pdf(job_description, full_pdf_path, job_details.get('title'),
                                                          job_details.get('url'), rating_int, anschreiben)
                            if rating_int >= 8:
                                print(
                                    f"  Rating {rating_int} >= 7: Generiere Anschreiben mit gemini-2.5-flash-preview-05-20...")
                                anschreiben = text_processor.generate_anschreiben(job_description,
                                                                                  applicant_information,
                                                                                  previous_cover_letter,
                                                                                  'gemini-2.5-pro-preview-05-06')
                                pdf_utils.markdown_to_pdf(job_description, full_pdf_path, job_details.get('title'),
                                                          job_details.get('url'), rating_int, anschreiben)
                            else:
                                print('Rating zu gering')
                        else:
                            print(
                                f"Überspringe Job '{job_title}' aufgrund ausgeschlossener Keywords (z.B. Praktikant, Trainee).")
                    else:
                        print(f"Konnte Job-Details für URL {job_url} nicht abrufen oder verarbeiten. Überspringe.")

    except Exception as e:
        print(f"Fehler: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if scraper:
            scraper.close_client()
        pdf_utils.merge_pdfs_by_rating(temp_pfs_dir, f"{temp_pfs_dir}\summary.pdf")

# Serve des Frontend-Builds
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    return send_from_directory(build_dir, 'index.html')


def main():
    # Frontend aufsetzen
    if setup_frontend_and_server():
        print("Starte Server mit Frontend...")
        print("Öffne http://localhost:5000 im Browser")
        print("Der Inhalt des Formulars und die Such-Kriterien werden nach dem Abschicken in der Konsole ausgegeben.")
        app.run(host='0.0.0.0', port=5000)
    else:
        print("Server konnte nicht gestartet werden.")


if __name__ == "__main__":
    main()
