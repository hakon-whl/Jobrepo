import subprocess
import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
import datetime
import traceback
import re
import logging

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
    from projekt.backend.core.config import app_config, setup_logging
except ImportError as e:
    print(f"KRITISCHER FEHLER: Konnte Backend-Module nicht importieren: {e}")
    print("Stelle sicher, dass alle Dependencies installiert sind:")
    print(
        "pip install httpx selenium beautifulsoup4 lxml PyPDF2 xhtml2pdf markdown google-generativeai python-dotenv webdriver-manager")
    sys.exit(1)

# Logging konfigurieren
setup_logging(app_config.logging_config, app_config.paths.logs_dir)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=app_config.paths.build_dir)


def create_session_directory(job_title: str, location: str, job_source: JobSource) -> str:
    """
    Erstellt ein neues Verzeichnis für die Session basierend auf Job-Titel, Stadt, Jobseite und Datum
    """
    try:
        # Datum im Format dd.mm.yyyy
        date_str = datetime.datetime.now().strftime("%d.%m.%Y")

        # Job-Titel für Dateinamen bereinigen
        clean_job_title = re.sub(r'[^a-zA-Z0-9\s]', '', job_title)
        clean_job_title = re.sub(r'\s+', '_', clean_job_title.strip())
        clean_job_title = clean_job_title[:25]

        if not clean_job_title:
            clean_job_title = "Unbekannter_Job"

        # Stadt für Dateinamen bereinigen
        clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
        clean_location = re.sub(r'\s+', '_', clean_location.strip())
        clean_location = clean_location[:15]

        if not clean_location:
            clean_location = "Unbekannte_Stadt"

        # Jobseite für Dateinamen bereinigen
        clean_job_source = re.sub(r'[^a-zA-Z0-9]', '', job_source.value)
        clean_job_source = clean_job_source[:15]

        if not clean_job_source:
            clean_job_source = "UnbekannteSeite"

        # Session-Verzeichnisname erstellen
        session_dir_name = f"{clean_job_title}_{clean_location}_{clean_job_source}_{date_str}"
        session_dir_path = os.path.join(app_config.paths.temp_pdfs_dir, session_dir_name)

        # Verzeichnis erstellen falls es nicht existiert
        os.makedirs(session_dir_path, exist_ok=True)

        logger.info(f"Session-Verzeichnis erstellt: {session_dir_path}")
        return session_dir_path

    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Session-Verzeichnisses: {e}")
        # Fallback auf temp_pdfs Hauptverzeichnis
        return app_config.paths.temp_pdfs_dir


def setup_frontend_and_server():
    """Build das Frontend falls nötig und startet einen Server für beides"""
    try:
        if not os.path.exists(app_config.paths.build_dir) or not os.listdir(app_config.paths.build_dir):
            logger.info("Build-Verzeichnis nicht gefunden oder leer. Erstelle neuen Build...")
            try:
                subprocess.run(["npm", "run", "build"], cwd=app_config.paths.frontend_dir, check=True)
                logger.info("Frontend erfolgreich gebaut.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Fehler beim Bauen des Frontends: {e}")
                return False
            except FileNotFoundError:
                logger.error("npm nicht gefunden. Stelle sicher, dass Node.js installiert ist.")
                return False
        else:
            logger.info(f"Verwende existierenden Frontend-Build in {app_config.paths.build_dir}")
        return True
    except Exception as e:
        logger.error(f"Fehler in setup_frontend_and_server: {e}")
        return False


def get_scraper_for_source(job_source: JobSource):
    """Factory-Funktion für Scraper basierend auf JobSource"""
    try:
        scraper_map = {
            JobSource.STEPSTONE: StepstoneScraper,
            JobSource.XING: XingScraper,
            JobSource.STELLENANZEIGEN: StellenanzeigenScraper
        }
        scraper = scraper_map.get(job_source)()
        logger.info(f"Scraper erstellt für {job_source.value}")
        return scraper
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Scrapers für {job_source}: {e}")
        return None


@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    """Erstellt Job-Zusammenfassung mit strukturierten Datenklassen"""
    scraper = None
    session_dir = None

    try:
        # Eindeutigen Dateinamen für diese Session erstellen
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Starte neue Job-Zusammenfassung Session: {timestamp}")

        # Request-Daten validieren
        if not request.is_json:
            logger.warning("Request ohne JSON Content-Type erhalten")
            return jsonify({
                "success": False,
                "error": "Content-Type muss application/json sein"
            }), 400

        data = request.get_json()
        if not data:
            logger.warning("Leere JSON-Daten empfangen")
            return jsonify({
                "success": False,
                "error": "Keine JSON-Daten empfangen"
            }), 400

        logger.info(f"Empfangene Daten: {list(data.keys())}")

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

            logger.info(f"Suchkriterien: {search_criteria.job_title} in {search_criteria.location}")
            logger.info(
                f"Bewerber-Profil: {len(applicant_profile.skills)} Skills, {len(applicant_profile.pdf_contents)} PDFs")

        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten der Eingabedaten: {e}")
            return jsonify({
                "success": False,
                "error": f"Fehler beim Verarbeiten der Eingabedaten: {str(e)}"
            }), 400

        # Validierung der Pflichtfelder
        if not search_criteria.job_title:
            logger.warning("Jobtitel fehlt in der Anfrage")
            return jsonify({
                "success": False,
                "error": "Jobtitel ist erforderlich"
            }), 400

        if not search_criteria.location:
            logger.warning("Ort fehlt in der Anfrage")
            return jsonify({
                "success": False,
                "error": "Ort ist erforderlich"
            }), 400

        # Job-Sites zu JobSource Enum konvertieren
        job_sites_input = data.get("jobSites", "")
        if not job_sites_input:
            logger.warning("Keine Jobseite ausgewählt")
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
                logger.warning(f"Unbekannte Job-Site: {job_sites_input}")
                return jsonify({
                    "success": False,
                    "error": f"Unbekannte Job-Site: {job_sites_input}"
                }), 400
        except Exception as e:
            logger.error(f"Fehler bei JobSource-Bestimmung: {e}")
            return jsonify({
                "success": False,
                "error": f"Fehler bei JobSource-Bestimmung: {str(e)}"
            }), 400

        # Session-Verzeichnis erstellen
        session_dir = create_session_directory(
            search_criteria.job_title,
            search_criteria.location,
            selected_source
        )
        logger.info(f"Verwende Session-Verzeichnis: {session_dir}")

        # === SCHRITT 2: SCRAPING SESSION INITIALISIEREN ===
        try:
            scraping_session = ScrapingSession(
                search_criteria=search_criteria,
                applicant_profile=applicant_profile,
                selected_sources=[selected_source]
            )

            pdf_config = PDFGenerationConfig(
                output_directory=session_dir,
                merge_pdfs=True,
                include_cover_letters=True,
                sort_by_rating=True
            )

            logger.info("Scraping-Session erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Session: {e}")
            return jsonify({
                "success": False,
                "error": f"Fehler beim Initialisieren der Session: {str(e)}"
            }), 500

        # === SCHRITT 3: SCRAPER AUSWÄHLEN UND URLS SAMMELN ===
        try:
            scraper = get_scraper_for_source(selected_source)
            if not scraper:
                logger.error(f"Scraper für {selected_source.value} konnte nicht erstellt werden")
                return jsonify({
                    "success": False,
                    "error": f"Scraper für {selected_source.value} konnte nicht erstellt werden"
                }), 500

            # Job-URLs sammeln
            job_urls = scraper.get_search_result_urls(search_criteria)
            if not job_urls:
                logger.warning("Keine Job-URLs gefunden")
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

            logger.info(f"{selected_source.value}: {len(job_urls)} einzigartige Job-URLs gesammelt")
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Job-URLs: {e}")
            return jsonify({
                "success": False,
                "error": f"Fehler beim Sammeln der Job-URLs: {str(e)}"
            }), 500

        # === SCHRITT 4: JOB-VERARBEITUNG ===
        try:
            text_processor = TextProcessor()
            pdf_utils = PdfUtils()

            max_jobs = min(len(job_urls), app_config.scraping.max_jobs_per_session)
            logger.info(f"Verarbeite {max_jobs} von {len(job_urls)} Jobs")

            for i, job_url in enumerate(job_urls[:max_jobs]):
                if job_url:
                    try:
                        logger.info(f"Verarbeite Job {i + 1}/{max_jobs}: {job_url}")

                        # Job-Details extrahieren
                        job_details = scraper.extract_job_details(job_url)

                        if job_details and job_details.contains_internship_keywords():
                            logger.info(f"Verarbeite relevanten Job: {job_details.title}")

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
                                logger.info(f"Job mit Rating {rating} wird verarbeitet: {job_details.title}")

                                # AI-Model basierend auf Rating auswählen
                                ai_model = match_result.recommended_ai_model
                                match_result.ai_model_used = ai_model

                                # Anschreiben generieren
                                cover_letter = text_processor.generate_anschreiben(
                                    job_details, applicant_profile, ai_model
                                )
                                match_result.cover_letter = cover_letter

                                # PDF erstellen
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
                                    logger.error(f"PDF-Erstellung fehlgeschlagen für: {job_details.title}")
                            else:
                                logger.info(f'Rating {rating} zu gering für: {job_details.title}')
                        else:
                            if job_details:
                                logger.debug(f"Überspringe Job '{job_details.title}' - keine relevanten Keywords")

                    except Exception as job_error:
                        logger.error(f"Fehler bei Job-Verarbeitung {job_url}: {job_error}")
                        continue
        except Exception as e:
            logger.error(f"Fehler bei der Job-Verarbeitung: {e}")
            return jsonify({
                "success": False,
                "error": f"Fehler bei der Job-Verarbeitung: {str(e)}"
            }), 500

        # === SCHRITT 5: ERGEBNISSE ZUSAMMENFASSEN ===
        logger.info(f"Verarbeitung abgeschlossen. {scraping_session.total_jobs_processed} Jobs verarbeitet.")
        logger.info(f"Erfolgreiche Matches: {len(scraping_session.successful_matches)}")

        if scraping_session.successful_matches:
            logger.info(f"Durchschnittliches Rating: {scraping_session.average_rating:.2f}")

            # PDF zusammenfassen und als Response senden
            try:
                logger.info("Erstelle zusammengefasste PDF...")
                summary_pdf_filename = pdf_config.get_summary_filename(timestamp)
                summary_pdf_path = os.path.join(session_dir, summary_pdf_filename)

                merge_success = pdf_utils.merge_pdfs_by_rating(session_dir, summary_pdf_path)

                if merge_success and os.path.exists(summary_pdf_path):
                    logger.info(f"PDF erstellt: {summary_pdf_path}")

                    # PDF als Response senden
                    response = make_response(send_file(
                        summary_pdf_path,
                        as_attachment=True,
                        download_name=summary_pdf_filename,
                        mimetype='application/pdf'
                    ))

                    # Cleanup nach dem Senden - OPTIONAL
                    @response.call_on_close
                    def cleanup():
                        try:
                            import shutil
                            if os.path.exists(session_dir):
                                shutil.rmtree(session_dir)
                                logger.info(f"Session-Verzeichnis gelöscht: {session_dir}")
                        except Exception as e:
                            logger.error(f"Fehler beim Cleanup: {e}")

                    return response
                else:
                    logger.error("Fehler beim Erstellen der zusammengefassten PDF")
                    return jsonify({
                        "success": False,
                        "error": "Fehler beim Erstellen der zusammengefassten PDF."
                    }), 500
            except Exception as e:
                logger.error(f"Fehler bei PDF-Erstellung: {e}")
                return jsonify({
                    "success": False,
                    "error": f"Fehler bei PDF-Erstellung: {str(e)}"
                }), 500
        else:
            logger.warning("Keine passenden Jobs gefunden oder verarbeitet")
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
        logger.error(f"KRITISCHER FEHLER in create_job_summary: {str(e)}")
        logger.error(traceback.format_exc())

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
                logger.info("Scraper erfolgreich geschlossen")
            except Exception as e:
                logger.error(f"Fehler beim Schließen des Scrapers: {e}")


# === HEALTH CHECK ENDPOINT ===
@app.route('/api/health', methods=['GET'])
def health_check():
    """Erweiterte Health Check"""
    try:
        health_info = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "temp_dir_exists": os.path.exists(app_config.paths.temp_pdfs_dir),
            "temp_dir_writable": os.access(app_config.paths.temp_pdfs_dir, os.W_OK) if os.path.exists(
                app_config.paths.temp_pdfs_dir) else False,
            "build_dir_exists": os.path.exists(app_config.paths.build_dir),
            "python_version": sys.version,
            "config": {
                "debug": app_config.debug,
                "ai_model": app_config.ai.default_model.value,
                "max_jobs": app_config.scraping.max_jobs_per_session
            }
        }

        # Test Dependencies
        try:
            import httpx, selenium, bs4, PyPDF2, xhtml2pdf, markdown
            health_info["dependencies"] = "OK"
        except ImportError as e:
            health_info["dependencies"] = f"FEHLER: {e}"
            health_info["status"] = "unhealthy"

        logger.info("Health check ausgeführt")
        return jsonify(health_info)
    except Exception as e:
        logger.error(f"Health check Fehler: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# Serve des Frontend-Builds
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    try:
        if path and os.path.exists(os.path.join(app_config.paths.build_dir, path)):
            return send_from_directory(app_config.paths.build_dir, path)
        return send_from_directory(app_config.paths.build_dir, 'index.html')
    except Exception as e:
        logger.error(f"Fehler beim Laden der Frontend-Datei: {e}")
        return f"Fehler beim Laden der Frontend-Datei: {e}", 500


def main():
    try:
        logger.info("=== ANWENDUNG STARTET ===")
        logger.info(f"Debug-Modus: {app_config.debug}")
        logger.info(f"Temp-PDFs Verzeichnis: {app_config.paths.temp_pdfs_dir}")
        logger.info(f"Prompts Verzeichnis: {app_config.paths.prompts_dir}")

        if setup_frontend_and_server():
            logger.info("Starte Server mit Frontend...")
            logger.info("Öffne http://localhost:5000 im Browser")
            logger.info("Health Check: http://localhost:5000/api/health")

            # Teste Dependencies
            try:
                import httpx, selenium, bs4, PyPDF2, xhtml2pdf, markdown
                logger.info("✅ Alle Dependencies verfügbar")
            except ImportError as e:
                logger.error(f"❌ Fehlende Dependencies: {e}")
                logger.error(
                    "Installiere: pip install httpx selenium beautifulsoup4 lxml PyPDF2 xhtml2pdf markdown google-generativeai python-dotenv webdriver-manager")

            app.run(host='0.0.0.0', port=5000, debug=app_config.debug)
        else:
            logger.error("❌ Server konnte nicht gestartet werden.")
    except Exception as e:
        logger.error(f"Fehler beim Starten des Servers: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()