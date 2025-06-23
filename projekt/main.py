import subprocess
import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
import datetime
import traceback
import re
import logging

try:
    from projekt.backend.ai.text_processor import TextProcessor
    from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
    from projekt.backend.scrapers.xing_scraper import XingScraper
    from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper
    from projekt.backend.utils.pdf_utils import PdfUtils
    from projekt.backend.core.models import (
        SearchCriteria, ApplicantProfile, JobMatchResult,
        ScrapingSession, JobSource
    )
    from projekt.backend.core.config import app_config, setup_logging

except ImportError as e:
    print(f"KRITISCHER FEHLER: {e}")
    sys.exit(1)

setup_logging(app_config.logging_config, app_config.paths.logs_dir)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=app_config.paths.build_dir)


def create_session_directory(job_title: str, location: str, job_source: JobSource) -> str:
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%M-%H")

        clean_job_title = re.sub(r'[^a-zA-Z0-9\s]', '', job_title)
        clean_job_title = re.sub(r'\s+', '_', clean_job_title.strip())
        clean_job_title = clean_job_title[:25]

        if not clean_job_title:
            clean_job_title = "Unbekannter_Job"

        clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
        clean_location = re.sub(r'\s+', '_', clean_location.strip())
        clean_location = clean_location[:15]

        if not clean_location:
            clean_location = "Unbekannte_Stadt"

        clean_job_source = re.sub(r'[^a-zA-Z0-9]', '', job_source.value)
        clean_job_source = clean_job_source[:15]

        if not clean_job_source:
            clean_job_source = "UnbekannteSeite"

        session_dir_name = f"{clean_job_title}_{clean_location}_{clean_job_source}_{date_str}_{time_str}"
        session_dir_path = os.path.join(app_config.paths.temp_pdfs_dir, session_dir_name)

        os.makedirs(session_dir_path, exist_ok=True)

        logger.info(f"📁 Session-Verzeichnis erstellt: {session_dir_name}")
        return session_dir_path

    except Exception as e:
        logger.error(f"Session-Verzeichnis Fehler: {e}")
        # Fallback auf temp_pdfs Hauptverzeichnis
        return app_config.paths.temp_pdfs_dir


def setup_frontend_and_server():
    try:
        if not os.path.exists(app_config.paths.build_dir) or not os.listdir(app_config.paths.build_dir):
            logger.info("Frontend wird gebaut...")
            subprocess.run(["npm", "run", "build"], cwd=app_config.paths.frontend_dir, check=True)
        return True
    except Exception as e:
        logger.error(f"Frontend Setup Fehler: {e}")
        return False


def get_scraper_for_source(job_source: JobSource):
    scraper_map = {
        JobSource.STEPSTONE: StepstoneScraper,
        JobSource.XING: XingScraper,
        JobSource.STELLENANZEIGEN: StellenanzeigenScraper
    }
    return scraper_map.get(job_source)()


@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    scraper = None

    try:
        logger.info("🔍 Starte Job-Suche...")
        logger.info(f"🤖 AI-Config: Anschreiben={app_config.ai.cover_letter_model.value}, "
                    f"Rating={app_config.ai.rating_model.value}, "
                    f"Formatierung={app_config.ai.formatting_model.value}")

        # Request validieren
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Keine Daten empfangen"}), 400

        # Datenstrukturen erstellen
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

        if not search_criteria.job_title or not search_criteria.location:
            return jsonify({"success": False, "error": "Jobtitel und Ort sind erforderlich"}), 400

        job_sites_input = data.get("jobSites", "")
        source_map = {
            "StepStone": JobSource.STEPSTONE,
            "Xing": JobSource.XING,
            "Stellenanzeigen.de": JobSource.STELLENANZEIGEN
        }
        selected_source = source_map.get(job_sites_input)
        if not selected_source:
            return jsonify({"success": False, "error": f"Unbekannte Job-Site: {job_sites_input}"}), 400

        # Session initialisieren
        session_dir = create_session_directory(search_criteria.job_title, search_criteria.location, selected_source)
        scraping_session = ScrapingSession(search_criteria, applicant_profile, selected_source)

        logger.info(f"📋 Suche: {search_criteria.job_title} in {search_criteria.location}")

        # Scraper starten
        scraper = get_scraper_for_source(selected_source)
        job_urls = scraper.get_search_result_urls(search_criteria)

        if not job_urls:
            return jsonify({
                "success": False,
                "message": "Keine Jobs gefunden",
                "stats": {"total_found": 0, "selected_source": selected_source.value}
            }), 404

        job_urls = list(set(job_urls))
        scraping_session.total_jobs_found = len(job_urls)

        logger.info(f"📊 {len(job_urls)} Jobs gefunden auf {selected_source.value}")

        # Jobs verarbeiten
        text_processor = TextProcessor()
        pdf_utils = PdfUtils()
        max_jobs = min(len(job_urls), app_config.scraping.max_jobs_per_session)

        logger.info(f"🔧 Verarbeite {max_jobs} Jobs...")

        processed_count = 0
        for i, job_url in enumerate(job_urls[:max_jobs]):
            if job_url:
                try:
                    if i % 5 == 0 or i == max_jobs - 1:
                        logger.info(f"   {i + 1}/{max_jobs} Jobs verarbeitet")

                    job_details = scraper.extract_job_details(job_url)

                    if job_details and job_details.is_internship:
                        processed_count += 1

                        # Job formatieren und bewerten (verwendet automatisch Config-Parameter)
                        logger.debug(f"Formatiere Job: {job_details.title}")
                        formatted_description = text_processor.format_job_description(job_details.raw_text)

                        logger.debug(f"Bewerte Job-Match für: {job_details.title}")
                        rating = text_processor.rate_job_match(job_details, applicant_profile)

                        job_details.formatted_description = formatted_description

                        # AI-Model Info für Tracking
                        ai_model_used = app_config.ai.cover_letter_model.value
                        match_result = JobMatchResult(
                            job_details=job_details,
                            rating=rating,
                            formatted_description=formatted_description,
                            ai_model_used=ai_model_used
                        )

                        # NUR Jobs mit Rating >= 5 verarbeiten
                        if match_result.is_worth_processing:
                            logger.info(f"🎯 Verarbeite hochwertigen Job (Rating: {rating}/10): {job_details.title}")

                            # Anschreiben generieren (verwendet automatisch Config-Parameter)
                            cover_letter = text_processor.generate_anschreiben(
                                job_details, applicant_profile
                            )
                            match_result.cover_letter = cover_letter

                            # PDF erstellen
                            pdf_filename = match_result.get_pdf_filename()
                            full_pdf_path = os.path.join(session_dir, pdf_filename)

                            if pdf_utils.markdown_to_pdf(
                                    formatted_description,
                                    full_pdf_path,
                                    job_details.title,
                                    job_details.url,
                                    rating,
                                    cover_letter
                            ):
                                scraping_session.add_result(match_result)
                                logger.debug(f"✅ PDF erstellt: {pdf_filename}")
                        else:
                            logger.debug(f"⏭️  Job übersprungen (Rating: {rating}/10): {job_details.title}")
                    else:
                        logger.debug(f"⏭️  Kein Praktikums-Job übersprungen: {job_details.title if job_details else 'Unbekannt'}")

                except Exception as job_error:
                    logger.error(f"Job-Verarbeitung Fehler für {job_url}: {job_error}")
                    continue

        logger.info(f"✅ {processed_count} relevante Jobs verarbeitet")
        logger.info(f"⭐ {len(scraping_session.successful_matches)} erfolgreiche Matches")

        if scraping_session.successful_matches:
            avg_rating = scraping_session.average_rating
            logger.info(f"📈 ⌀ Rating: {avg_rating:.1f}/10")

            # Log AI-Model Usage
            used_models = {}
            for match in scraping_session.successful_matches:
                model = match.ai_model_used or "unknown"
                used_models[model] = used_models.get(model, 0) + 1

            logger.info(f"🤖 AI-Models verwendet: {used_models}")

            # PDF zusammenstellen
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_pdf_filename = f"Jobs_{search_criteria.job_title}_{search_criteria.location}_{timestamp}.pdf"
            summary_pdf_path = os.path.join(session_dir, summary_pdf_filename)

            if pdf_utils.merge_pdfs_by_rating(session_dir, summary_pdf_path):
                logger.info("📄 PDF-Zusammenfassung erstellt")

                response = make_response(send_file(
                    summary_pdf_path,
                    as_attachment=True,
                    download_name=summary_pdf_filename,
                    mimetype='application/pdf'
                ))

                @response.call_on_close
                def cleanup():
                    try:
                        import shutil
                        if os.path.exists(session_dir):
                            shutil.rmtree(session_dir)
                            logger.debug(f"🗑️  Session-Verzeichnis aufgeräumt: {session_dir}")
                    except Exception as cleanup_error:
                        logger.warning(f"Cleanup Fehler: {cleanup_error}")

                return response
            else:
                return jsonify({"success": False, "error": "PDF-Erstellung fehlgeschlagen"}), 500
        else:
            return jsonify({
                "success": False,
                "message": "Keine passenden Jobs gefunden",
                "stats": {
                    "total_found": scraping_session.total_jobs_found,
                    "total_processed": scraping_session.total_jobs_processed,
                    "selected_source": selected_source.value,
                    "average_rating": scraping_session.average_rating if scraping_session.job_results else 0
                }
            }), 404

    except Exception as e:
        logger.error(f"KRITISCHER FEHLER: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Unerwarteter Fehler aufgetreten"
        }), 500

    finally:
        if scraper:
            try:
                scraper.close_client()
                logger.debug("🔒 Scraper geschlossen")
            except Exception as close_error:
                logger.warning(f"Scraper-Close Fehler: {close_error}")


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "config": {
                "ai_models": {
                    "cover_letter": app_config.ai.cover_letter_model.value,
                    "rating": app_config.ai.rating_model.value,
                    "formatting": app_config.ai.formatting_model.value
                },
                "temperatures": {
                    "cover_letter": app_config.ai.cover_letter_temperature,
                    "rating": app_config.ai.rating_temperature,
                    "formatting": app_config.ai.formatting_temperature
                }
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Gibt aktuelle AI-Konfiguration zurück"""
    try:
        return jsonify({
            "ai_config": {
                "cover_letter_model": app_config.ai.cover_letter_model.value,
                "cover_letter_temperature": app_config.ai.cover_letter_temperature,
                "rating_model": app_config.ai.rating_model.value,
                "rating_temperature": app_config.ai.rating_temperature,
                "formatting_model": app_config.ai.formatting_model.value,
                "formatting_temperature": app_config.ai.formatting_temperature,
                "premium_threshold": app_config.ai.premium_rating_threshold
            },
            "scraping_config": {
                "max_jobs_per_session": app_config.scraping.max_jobs_per_session,
                "max_pages_per_site": app_config.scraping.max_pages_per_site
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    try:
        if path and os.path.exists(os.path.join(app_config.paths.build_dir, path)):
            return send_from_directory(app_config.paths.build_dir, path)
        return send_from_directory(app_config.paths.build_dir, 'index.html')
    except Exception as e:
        return f"Frontend Fehler: {e}", 500


def main():
    try:
        logger.info("🚀 Starte Server...")
        logger.info("🤖 AI-Konfiguration:")
        logger.info(
            f"   Anschreiben: {app_config.ai.cover_letter_model.value} (temp: {app_config.ai.cover_letter_temperature})")
        logger.info(f"   Rating: {app_config.ai.rating_model.value} (temp: {app_config.ai.rating_temperature})")
        logger.info(
            f"   Formatierung: {app_config.ai.formatting_model.value} (temp: {app_config.ai.formatting_temperature})")

        if setup_frontend_and_server():
            logger.info("✅ Server bereit auf http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=app_config.debug)
        else:
            logger.error("❌ Server-Start fehlgeschlagen")
    except Exception as e:
        logger.error(f"Server-Start Fehler: {e}")


if __name__ == "__main__":
    main()