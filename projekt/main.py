import subprocess
import os
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
import datetime

from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
from projekt.backend.scrapers.xing_scraper import XingScraper
from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper
from projekt.backend.utils.pdf_utils import PdfUtils
from projekt.backend.core.models import (
    SearchCriteria, ApplicantProfile, JobMatchResult,
    ScrapingSession, JobSource, PDFGenerationConfig
)

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


def get_scraper_for_source(job_source: JobSource):
    """Factory-Funktion für Scraper basierend auf JobSource"""
    scraper_map = {
        JobSource.STEPSTONE: StepstoneScraper,
        JobSource.XING: XingScraper,
        JobSource.STELLENANZEIGEN: StellenanzeigenScraper
    }
    return scraper_map.get(job_source)()


@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    """Erstellt Job-Zusammenfassung mit strukturierten Datenklassen"""
    scraper = None

    # Eindeutigen Dateinamen für diese Session erstellen
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        data = request.json
        print(f"Empfangene Daten: {list(data.keys())}")

        # === SCHRITT 1: STRUKTURIERTE DATENERFASSUNG ===
        search_criteria = SearchCriteria(
            job_title=data.get("jobTitle", ""),
            location=data.get("location", ""),
            radius=str(data.get("radius", "20")),
            discipline=data.get("discipline", "")
        )

        applicant_profile = ApplicantProfile(
            study_info=data.get("studyInfo", ""),
            interests=data.get("interests", ""),
            skills=data.get("skills", []),  # Liste von Skills
            pdf_contents=data.get("pdfContents", {})
        )

        # PDF-Inhalte loggen
        if applicant_profile.pdf_contents:
            print(f"PDF-Inhalte empfangen: {list(applicant_profile.pdf_contents.keys())}")
            for filename, text in applicant_profile.pdf_contents.items():
                print(f"PDF '{filename}': {len(text)} Zeichen")

        # Job-Sites zu JobSource Enum konvertieren
        job_sites_input = data.get("jobSites", "")
        if not job_sites_input:
            return jsonify({
                "success": False,
                "message": "Keine Jobseite ausgewählt."
            }), 400

        # JobSource bestimmen
        try:
            if job_sites_input == "StepStone":
                selected_source = JobSource.STEPSTONE
            elif job_sites_input == "Xing":
                selected_source = JobSource.XING
            elif job_sites_input == "Stellenanzeigen.de":
                selected_source = JobSource.STELLENANZEIGEN
            else:
                raise ValueError(f"Unbekannte Job-Site: {job_sites_input}")
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        # === SCHRITT 2: SCRAPING SESSION INITIALISIEREN ===
        scraping_session = ScrapingSession(
            search_criteria=search_criteria,
            applicant_profile=applicant_profile,
            selected_sources=[selected_source]
        )

        # PDF-Konfiguration
        pdf_config = PDFGenerationConfig(
            output_directory=temp_pfs_dir,
            merge_pdfs=True,
            include_cover_letters=True,
            sort_by_rating=True
        )

        # === SCHRITT 3: SCRAPER AUSWÄHLEN UND URLS SAMMELN ===
        scraper = get_scraper_for_source(selected_source)
        print(f"Scraper: {selected_source.value} ausgewählt.")

        # Job-URLs sammeln mit strukturierten SearchCriteria
        job_urls = scraper.get_search_result_urls(search_criteria)
        job_urls = list(set(job_urls))  # Duplikate entfernen
        scraping_session.total_jobs_found = len(job_urls)

        print(f"{selected_source.value}: {len(job_urls)} einzigartige Job-URLs gesammelt.")

        # === SCHRITT 4: JOB-VERARBEITUNG ===
        text_processor = TextProcessor()
        pdf_utils = PdfUtils()

        for job_url in job_urls[:4]:  # Limitiert auf 4 Jobs für Tests
            if job_url:
                try:
                    # Job-Details extrahieren (gibt JobDetails-Objekt zurück)
                    job_details = scraper.extract_job_details(job_url)

                    if job_details and job_details.contains_internship_keywords():
                        print(f"Verarbeite relevanten Job: {job_details.title}")

                        # Job-Beschreibung formatieren
                        formatted_description = text_processor.format_job_description(job_details.raw_text)
                        job_details.formatted_description = formatted_description

                        # Job-Match bewerten
                        rating = text_processor.rate_job_match(job_details, applicant_profile)

                        # JobMatchResult erstellen
                        match_result = JobMatchResult(
                            job_details=job_details,
                            rating=rating,
                            formatted_description=formatted_description
                        )

                        if match_result.is_worth_processing:
                            print(f"Job mit Rating {rating} wird verarbeitet: {job_details.title}")

                            # AI-Model basierend auf Rating auswählen
                            ai_model = match_result.recommended_ai_model
                            match_result.ai_model_used = ai_model

                            # Anschreiben generieren mit strukturierten Daten
                            cover_letter = text_processor.generate_anschreiben(
                                job_details, applicant_profile, ai_model
                            )
                            match_result.cover_letter = cover_letter

                            # PDF erstellen
                            pdf_filename = match_result.get_pdf_filename()
                            full_pdf_path = os.path.join(temp_pfs_dir, pdf_filename)

                            pdf_utils.markdown_to_pdf(
                                formatted_description,
                                full_pdf_path,
                                job_details.title,
                                job_details.url,
                                rating,
                                cover_letter
                            )

                            # Zu Session hinzufügen
                            scraping_session.add_result(match_result)
                        else:
                            print(f'Rating {rating} zu gering für: {job_details.title}')
                    else:
                        if job_details:
                            print(f"Überspringe Job '{job_details.title}' - keine relevanten Keywords")

                except Exception as job_error:
                    print(f"Fehler bei Job-Verarbeitung {job_url}: {job_error}")
                    continue

        # === SCHRITT 5: ERGEBNISSE ZUSAMMENFASSEN ===
        print(f"Verarbeitung abgeschlossen. {scraping_session.total_jobs_processed} Jobs verarbeitet.")
        print(f"Erfolgreiche Matches: {len(scraping_session.successful_matches)}")
        print(f"Durchschnittliches Rating: {scraping_session.average_rating:.2f}")

        # PDF zusammenfassen und als Response senden
        if scraping_session.successful_matches:
            print("Erstelle zusammengefasste PDF...")
            summary_pdf_path = os.path.join(temp_pfs_dir, pdf_config.get_summary_filename(timestamp))

            pdf_utils.merge_pdfs_by_rating(temp_pfs_dir, summary_pdf_path)

            if os.path.exists(summary_pdf_path):
                print(f"PDF erstellt: {summary_pdf_path}")

                # PDF als Response senden
                response = make_response(send_file(
                    summary_pdf_path,
                    as_attachment=True,
                    download_name=pdf_config.get_summary_filename(timestamp),
                    mimetype='application/pdf'
                ))

                # Cleanup nach dem Senden
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(summary_pdf_path):
                            os.remove(summary_pdf_path)
                            print(f"Temporäre PDF gelöscht: {summary_pdf_path}")
                        # Cleanup einzelner PDFs
                        for match_result in scraping_session.successful_matches:
                            individual_pdf = os.path.join(temp_pfs_dir, match_result.get_pdf_filename())
                            if os.path.exists(individual_pdf):
                                os.remove(individual_pdf)
                    except Exception as e:
                        print(f"Fehler beim Cleanup: {e}")

                return response
            else:
                return jsonify({
                    "success": False,
                    "message": "Fehler beim Erstellen der zusammengefassten PDF."
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Keine passenden Jobs gefunden oder verarbeitet.",
                "stats": {
                    "total_found": scraping_session.total_jobs_found,
                    "total_processed": scraping_session.total_jobs_processed,
                    "average_rating": scraping_session.average_rating,
                    "selected_source": selected_source.value
                }
            }), 404

    except Exception as e:
        print(f"Fehler in create_job_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

    finally:
        if scraper:
            scraper.close_client()


# === HEALTH CHECK ENDPOINT ===
@app.route('/api/health', methods=['GET'])
def health_check():
    """Einfacher Health Check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "temp_dir_exists": os.path.exists(temp_pfs_dir)
    })

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
        print(f"Health Check: http://localhost:5000/api/health")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Server konnte nicht gestartet werden.")


if __name__ == "__main__":
    main()