import subprocess
import os
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response

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


@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    stepstone = StepstoneScraper()
    xing = XingScraper()
    stellenanzeigen = StellenanzeigenScraper()
    text_processor = TextProcessor()
    pdf_utils = PdfUtils()
    scraper = None

    # Eindeutigen Dateinamen für diese Session erstellen
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_pdf_path = os.path.join(temp_pfs_dir, f"job_summary_{timestamp}.pdf")

    try:
        data = request.json
        print(f"Empfangene Daten: {list(data.keys())}")

        # PDF-Inhalte aus Frontend verarbeiten (bereits als Text empfangen)
        pdf_contents = data.get("pdfContents", {})
        if pdf_contents:
            print(f"PDF-Inhalte empfangen: {list(pdf_contents.keys())}")
            # Hier kannst du die PDF-Texte weiterverarbeiten
            for filename, text in pdf_contents.items():
                print(f"PDF '{filename}': {len(text)} Zeichen")

        job_sites_selected = data.get("jobSites", [])

        # Scraper-Auswahl und Suchkriterien
        if "StepStone" in job_sites_selected:
            scraper = StepstoneScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("location", ""),  # Geändert von selectedPlz zu location
                "radius": data.get("radius", ""),
                "discipline": data.get("discipline", "")
            }
            print("Scraper: StepStone ausgewählt.")

        elif "Xing" in job_sites_selected:
            scraper = XingScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("location", ""),  # Geändert von selectedPlz zu location
                "radius": data.get("radius", ""),
            }
            print("Scraper: XING ausgewählt.")

        elif "Stellenanzeigen" in job_sites_selected:
            scraper = StellenanzeigenScraper()
            search_criteria = {
                "jobTitle": data.get("jobTitle", ""),
                "location": data.get("location", ""),  # Geändert von selectedPlz zu location
                "radius": data.get("radius", ""),
            }
            print("Scraper: Stellenanzeigen ausgewählt.")

        else:
            return jsonify({
                "success": False,
                "message": "Keine unterstützte Jobseite ausgewählt."
            }), 400

        job_urls = []
        processed_jobs = 0

        if scraper:
            if isinstance(scraper, StepstoneScraper):
                job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls = list(set(job_urls))
                print(f"StepStone: {len(job_urls)} einzigartige Job-URLs gesammelt.")

            elif isinstance(scraper, XingScraper):
                page_job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls.extend(page_job_urls)
                job_urls = list(set(job_urls))

            elif isinstance(scraper, StellenanzeigenScraper):
                page_job_urls = scraper.get_search_result_urls(search_criteria)
                job_urls.extend(page_job_urls)
                job_urls = list(set(job_urls))

            # Job-Verarbeitung (limitiert auf 4 Jobs für Tests)
            for job_url in job_urls[:4]:
                if job_url:
                    try:
                        if "StepStone" in job_sites_selected:
                            job_details = stepstone.extract_job_details(job_url)
                        elif "Xing" in job_sites_selected:
                            job_details = xing.extract_job_details(job_url)
                        elif "Stellenanzeigen" in job_sites_selected:
                            job_details = stellenanzeigen.extract_job_details(job_url)

                        if job_details:
                            job_title = job_details.get('title_clean', '')
                            include_keywords = ["Praktikant", "Praktikum", "Trainee", "Internship", "INTERN", "Intern"]

                            if any(keyword.lower() in str(job_title).lower() for keyword in include_keywords):
                                applicant_information = {
                                    "studyInfo": data.get("studyInfo", ""),
                                    "interests": data.get("interests", ""),
                                    "skills": data.get("skills", ""),
                                }

                                # Verwende PDF-Inhalte als previous_cover_letter
                                previous_cover_letter = ""
                                if pdf_contents:
                                    # Kombiniere alle PDF-Inhalte oder verwende spezifische
                                    previous_cover_letter = "\n\n".join(pdf_contents.values())

                                job_description = text_processor.format_job_description(job_details.get('raw_text'))
                                rating_str = text_processor.rate_job_match(job_description, applicant_information)

                                try:
                                    rating_int = int(rating_str.strip())
                                except (ValueError, TypeError):
                                    rating_int = 0

                                safe_job_title_clean = job_details.get('title_clean', 'unbekannter_titel').replace(
                                    os.sep, '_').replace('/', '_').replace('\\', '_')
                                pdf_filename = f"{rating_int}_{safe_job_title_clean}.pdf"
                                full_pdf_path = os.path.join(temp_pfs_dir, pdf_filename)

                                if rating_int >= 2:
                                    print(f"Verarbeite Job mit Rating {rating_int}: {job_title}")
                                    if rating_int >= 8:
                                        model = 'gemini-2.5-pro-preview-05-06'
                                    else:
                                        model = 'gemini-2.5-flash-preview-05-20'

                                    anschreiben = text_processor.generate_anschreiben(
                                        job_description,
                                        applicant_information,
                                        previous_cover_letter,
                                        model
                                    )

                                    pdf_utils.markdown_to_pdf(
                                        job_description, full_pdf_path,
                                        job_details.get('title'),
                                        job_details.get('url'),
                                        rating_int, anschreiben
                                    )
                                    processed_jobs += 1
                                else:
                                    print(f'Rating {rating_int} zu gering für: {job_title}')
                            else:
                                print(f"Überspringe Job '{job_title}' - keine relevanten Keywords")
                    except Exception as job_error:
                        print(f"Fehler bei Job-Verarbeitung {job_url}: {job_error}")
                        continue

        print(f"Verarbeitung abgeschlossen. {processed_jobs} Jobs verarbeitet.")

        # PDF zusammenfassen und als Response senden
        if processed_jobs > 0:
            print("Erstelle zusammengefasste PDF...")
            pdf_utils.merge_pdfs_by_rating(temp_pfs_dir, summary_pdf_path)

            if os.path.exists(summary_pdf_path):
                print(f"PDF erstellt: {summary_pdf_path}")

                # PDF als Response senden
                response = make_response(send_file(
                    summary_pdf_path,
                    as_attachment=True,
                    download_name=f"job_bewerbungen_{timestamp}.pdf",
                    mimetype='application/pdf'
                ))

                # Cleanup nach dem Senden (optional)
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(summary_pdf_path):
                            os.remove(summary_pdf_path)
                            print(f"Temporäre PDF gelöscht: {summary_pdf_path}")
                    except Exception as e:
                        print(f"Fehler beim Löschen der temporären PDF: {e}")

                return response
            else:
                return jsonify({
                    "success": False,
                    "message": "Fehler beim Erstellen der zusammengefassten PDF."
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Keine passenden Jobs gefunden oder verarbeitet."
            }), 404

    except Exception as e:
        print(f"Fehler in create_job_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        if scraper:
            scraper.close_client()


# Serve des Frontend-Builds
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    return send_from_directory(build_dir, 'index.html')


def main():
    # Stelle sicher, dass temp_pdfs Ordner existiert
    os.makedirs(temp_pfs_dir, exist_ok=True)

    if setup_frontend_and_server():
        print("Starte Server mit Frontend...")
        print("Öffne http://localhost:5000 im Browser")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Server konnte nicht gestartet werden.")


if __name__ == "__main__":
    main()