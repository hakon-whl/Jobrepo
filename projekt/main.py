import subprocess
import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
import datetime
import traceback
import re

# Verbesserte Imports mit Error Handling
try:
    from projekt.backend.ai.text_processor import TextProcessor
    from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
    from projekt.backend.scrapers.xing_scraper import XingScraper
    from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper
    from projekt.backend.utils.pdf_utils import PdfUtils
    from projekt.backend.core.models import (
        SearchCriteria, ApplicantProfile, JobMatchResult,
        ScrapingSession, JobSource, PDFGenerationConfig
    )
except ImportError as e:
    print(f"KRITISCHER FEHLER: Konnte Backend-Module nicht importieren: {e}")
    print("Stelle sicher, dass alle Dependencies installiert sind:")
    print(
        "pip install httpx selenium beautifulsoup4 lxml PyPDF2 xhtml2pdf markdown google-generativeai python-dotenv webdriver-manager")
    sys.exit(1)

# Pfade definieren
frontend_dir = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
temp_pfs_dir = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\temp_pdfs"
build_dir = os.path.join(frontend_dir, "build")

app = Flask(__name__, static_folder=build_dir)


def create_session_directory(job_title: str, location: str, job_source: JobSource) -> str:
    """
    Erstellt ein neues Verzeichnis für die Session basierend auf Job-Titel, Stadt, Jobseite und Datum

    Args:
        job_title: Der Job-Titel für die Suche
        location: Die Stadt/Ort für die Suche
        job_source: Die verwendete Jobseite

    Returns:
        str: Pfad zum neuen Session-Verzeichnis
    """
    try:
        # Datum im Format dd.mm.yyyy
        date_str = datetime.datetime.now().strftime("%d.%m.%Y")

        # Job-Titel für Dateinamen bereinigen
        clean_job_title = re.sub(r'[^a-zA-Z0-9\s]', '', job_title)
        clean_job_title = re.sub(r'\s+', '_', clean_job_title.strip())
        clean_job_title = clean_job_title[:25]  # Länge begrenzt für Platz für Stadt und Jobseite

        if not clean_job_title:
            clean_job_title = "Unbekannter_Job"

        # Stadt für Dateinamen bereinigen
        clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
        clean_location = re.sub(r'\s+', '_', clean_location.strip())
        clean_location = clean_location[:15]  # Länge begrenzen

        if not clean_location:
            clean_location = "Unbekannte_Stadt"

        # Jobseite für Dateinamen bereinigen
        clean_job_source = re.sub(r'[^a-zA-Z0-9]', '', job_source.value)
        clean_job_source = clean_job_source[:15]  # Länge begrenzen

        if not clean_job_source:
            clean_job_source = "UnbekannteSeite"

        # Session-Verzeichnisname erstellen: JobTitel_Stadt_Jobseite_dd.mm.yyyy
        session_dir_name = f"{clean_job_title}_{clean_location}_{clean_job_source}_{date_str}"
        session_dir_path = os.path.join(temp_pfs_dir, session_dir_name)

        # Verzeichnis erstellen falls es nicht existiert
        os.makedirs(session_dir_path, exist_ok=True)

        print(f"Session-Verzeichnis erstellt: {session_dir_path}")
        return session_dir_path

    except Exception as e:
        print(f"Fehler beim Erstellen des Session-Verzeichnisses: {e}")
        # Fallback auf temp_pdfs Hauptverzeichnis
        return temp_pfs_dir


def setup_frontend_and_server():
    """Build das Frontend falls nötig und startet einen Server für beides"""
    try:
        if not os.path.exists(build_dir) or not os.listdir(build_dir):
            print("Build-Verzeichnis nicht gefunden oder leer. Erstelle neuen Build...")
            try:
                subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
                print("Frontend erfolgreich gebaut.")
            except subprocess.CalledProcessError as e:
                print(f"Fehler beim Bauen des Frontends: {e}")
                return False
            except FileNotFoundError:
                print("npm nicht gefunden. Stelle sicher, dass Node.js installiert ist.")
                return False
        else:
            print(f"Verwende existierenden Frontend-Build in {build_dir}")
        return True
    except Exception as e:
        print(f"Fehler in setup_frontend_and_server: {e}")
        return False


def get_scraper_for_source(job_source: JobSource):
    """Factory-Funktion für Scraper basierend auf JobSource"""
    try:
        scraper_map = {
            JobSource.STEPSTONE: StepstoneScraper,
            JobSource.XING: XingScraper,
            JobSource.STELLENANZEIGEN: StellenanzeigenScraper
        }
        return scraper_map.get(job_source)()
    except Exception as e:
        print(f"Fehler beim Erstellen des Scrapers für {job_source}: {e}")
        return None


@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    """Erstellt Job-Zusammenfassung mit strukturierten Datenklassen"""
    scraper = None
    session_dir = None

    try:
        # Eindeutigen Dateinamen für diese Session erstellen
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Request-Daten validieren
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type muss application/json sein"
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Keine JSON-Daten empfangen"
            }), 400

        print(f"Empfangene Daten: {list(data.keys())}")

        # Temp-Verzeichnis sicherstellen
        os.makedirs(temp_pfs_dir, exist_ok=True)

        # === SCHRITT 1: STRUKTURIERTE DATENERFASSUNG ===
        try:
            search_criteria = SearchCriteria(
                job_title=data.get("jobTitle", ""),
                location=data.get("location", ""),
                radius=str(data.get("radius", "20")),
                discipline=data.get("discipline", "")
            )

            applicant_profile = ApplicantProfile(
                study_info=data.get("studyInfo", ""),
                interests=data.get("interests", ""),
                skills=data.get("skills", []),
                pdf_contents=data.get("pdfContents", {})
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler beim Verarbeiten der Eingabedaten: {str(e)}"
            }), 400

        # Validierung der Pflichtfelder
        if not search_criteria.job_title:
            return jsonify({
                "success": False,
                "error": "Jobtitel ist erforderlich"
            }), 400

        if not search_criteria.location:
            return jsonify({
                "success": False,
                "error": "Ort ist erforderlich"
            }), 400

        # Job-Sites zu JobSource Enum konvertieren
        job_sites_input = data.get("jobSites", "")
        if not job_sites_input:
            return jsonify({
                "success": False,
                "error": "Keine Jobseite ausgewählt."
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
                return jsonify({
                    "success": False,
                    "error": f"Unbekannte Job-Site: {job_sites_input}"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler bei JobSource-Bestimmung: {str(e)}"
            }), 400

        # Session-Verzeichnis basierend auf Job-Titel, Stadt UND Jobseite erstellen
        session_dir = create_session_directory(
            search_criteria.job_title,
            search_criteria.location,
            selected_source
        )
        print(f"Verwende Session-Verzeichnis: {session_dir}")

        # PDF-Inhalte loggen
        if applicant_profile.pdf_contents:
            print(f"PDF-Inhalte empfangen: {list(applicant_profile.pdf_contents.keys())}")
            for filename, text in applicant_profile.pdf_contents.items():
                print(f"PDF '{filename}': {len(text)} Zeichen")

        # === SCHRITT 2: SCRAPING SESSION INITIALISIEREN ===
        try:
            scraping_session = ScrapingSession(
                search_criteria=search_criteria,
                applicant_profile=applicant_profile,
                selected_sources=[selected_source]
            )

            pdf_config = PDFGenerationConfig(
                output_directory=session_dir,  # Verwende das Session-Verzeichnis
                merge_pdfs=True,
                include_cover_letters=True,
                sort_by_rating=True
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler beim Initialisieren der Session: {str(e)}"
            }), 500

        # === SCHRITT 3: SCRAPER AUSWÄHLEN UND URLS SAMMELN ===
        try:
            scraper = get_scraper_for_source(selected_source)
            if not scraper:
                return jsonify({
                    "success": False,
                    "error": f"Scraper für {selected_source.value} konnte nicht erstellt werden"
                }), 500

            print(f"Scraper: {selected_source.value} ausgewählt.")

            # Job-URLs sammeln mit strukturierten SearchCriteria
            job_urls = scraper.get_search_result_urls(search_criteria)
            if not job_urls:
                return jsonify({
                    "success": False,
                    "message": "Keine Job-URLs gefunden.",
                    "stats": {
                        "total_found": 0,
                        "selected_source": selected_source.value
                    }
                }), 404

            job_urls = list(set(job_urls))  # Duplikate entfernen
            scraping_session.total_jobs_found = len(job_urls)

            print(f"{selected_source.value}: {len(job_urls)} einzigartige Job-URLs gesammelt.")
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler beim Sammeln der Job-URLs: {str(e)}"
            }), 500

        # === SCHRITT 4: JOB-VERARBEITUNG ===
        try:
            text_processor = TextProcessor()
            pdf_utils = PdfUtils()

            for job_url in job_urls[:4]:  # Limitiert auf 4 Jobs für Tests
                if job_url:
                    try:
                        # Job-Details extrahieren
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

                                # Anschreiben generieren
                                cover_letter = text_processor.generate_anschreiben(
                                    job_details, applicant_profile, ai_model
                                )
                                match_result.cover_letter = cover_letter

                                # PDF erstellen - im Session-Verzeichnis speichern
                                pdf_filename = match_result.get_pdf_filename()
                                full_pdf_path = os.path.join(session_dir, pdf_filename)

                                pdf_success = pdf_utils.markdown_to_pdf(
                                    formatted_description,
                                    full_pdf_path,
                                    job_details.title,
                                    job_details.url,
                                    rating,
                                    cover_letter
                                )

                                if pdf_success:
                                    scraping_session.add_result(match_result)
                                else:
                                    print(f"PDF-Erstellung fehlgeschlagen für: {job_details.title}")
                            else:
                                print(f'Rating {rating} zu gering für: {job_details.title}')
                        else:
                            if job_details:
                                print(f"Überspringe Job '{job_details.title}' - keine relevanten Keywords")

                    except Exception as job_error:
                        print(f"Fehler bei Job-Verarbeitung {job_url}: {job_error}")
                        continue
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Fehler bei der Job-Verarbeitung: {str(e)}"
            }), 500

        # === SCHRITT 5: ERGEBNISSE ZUSAMMENFASSEN ===
        print(f"Verarbeitung abgeschlossen. {scraping_session.total_jobs_processed} Jobs verarbeitet.")
        print(f"Erfolgreiche Matches: {len(scraping_session.successful_matches)}")

        if scraping_session.successful_matches:
            print(f"Durchschnittliches Rating: {scraping_session.average_rating:.2f}")

            # PDF zusammenfassen und als Response senden
            try:
                print("Erstelle zusammengefasste PDF...")
                summary_pdf_filename = pdf_config.get_summary_filename(timestamp)
                summary_pdf_path = os.path.join(session_dir, summary_pdf_filename)

                merge_success = pdf_utils.merge_pdfs_by_rating(session_dir, summary_pdf_path)

                if merge_success and os.path.exists(summary_pdf_path):
                    print(f"PDF erstellt: {summary_pdf_path}")

                    # PDF als Response senden
                    response = make_response(send_file(
                        summary_pdf_path,
                        as_attachment=True,
                        download_name=summary_pdf_filename,
                        mimetype='application/pdf'
                    ))

                    # Cleanup nach dem Senden - OPTIONAL: entferne das komplette Session-Verzeichnis
                    @response.call_on_close
                    def cleanup():
                        try:
                            # Optional: Session-Verzeichnis nach dem Download löschen
                            # Kommentiere die nächsten Zeilen aus, wenn du die PDFs behalten möchtest
                            import shutil
                            if os.path.exists(session_dir):
                                shutil.rmtree(session_dir)
                                print(f"Session-Verzeichnis gelöscht: {session_dir}")
                        except Exception as e:
                            print(f"Fehler beim Cleanup: {e}")

                    return response
                else:
                    return jsonify({
                        "success": False,
                        "error": "Fehler beim Erstellen der zusammengefassten PDF."
                    }), 500
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Fehler bei PDF-Erstellung: {str(e)}"
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
        print(f"KRITISCHER FEHLER in create_job_summary: {str(e)}")
        traceback.print_exc()

        # Detaillierte Fehlermeldung zurückgeben
        error_message = str(e)
        error_type = type(e).__name__

        return jsonify({
            "success": False,
            "error": error_message,
            "error_type": error_type,
            "message": "Ein unerwarteter Fehler ist aufgetreten. Überprüfe die Server-Logs für Details."
        }), 500

    finally:
        if scraper:
            try:
                scraper.close_client()
            except Exception as e:
                print(f"Fehler beim Schließen des Scrapers: {e}")


# === HEALTH CHECK ENDPOINT ===
@app.route('/api/health', methods=['GET'])
def health_check():
    """Erweiterte Health Check"""
    try:
        health_info = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "temp_dir_exists": os.path.exists(temp_pfs_dir),
            "temp_dir_writable": os.access(temp_pfs_dir, os.W_OK) if os.path.exists(temp_pfs_dir) else False,
            "build_dir_exists": os.path.exists(build_dir),
            "python_version": sys.version,
        }

        # Test Dependencies
        try:
            import httpx, selenium, bs4, PyPDF2, xhtml2pdf, markdown
            health_info["dependencies"] = "OK"
        except ImportError as e:
            health_info["dependencies"] = f"FEHLER: {e}"
            health_info["status"] = "unhealthy"

        return jsonify(health_info)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# Serve des Frontend-Builds
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    try:
        if path and os.path.exists(os.path.join(build_dir, path)):
            return send_from_directory(build_dir, path)
        return send_from_directory(build_dir, 'index.html')
    except Exception as e:
        return f"Fehler beim Laden der Frontend-Datei: {e}", 500


def main():
    try:
        # Stelle sicher, dass temp_pdfs Ordner existiert
        os.makedirs(temp_pfs_dir, exist_ok=True)

        if setup_frontend_and_server():
            print("Starte Server mit Frontend...")
            print("Öffne http://localhost:5000 im Browser")
            print(f"Health Check: http://localhost:5000/api/health")

            # Teste Dependencies
            try:
                import httpx, selenium, bs4, PyPDF2, xhtml2pdf, markdown
                print("✅ Alle Dependencies verfügbar")
            except ImportError as e:
                print(f"❌ Fehlende Dependencies: {e}")
                print(
                    "Installiere: pip install httpx selenium beautifulsoup4 lxml PyPDF2 xhtml2pdf markdown google-generativeai python-dotenv webdriver-manager")

            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            print("❌ Server konnte nicht gestartet werden.")
    except Exception as e:
        print(f"Fehler beim Starten des Servers: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()