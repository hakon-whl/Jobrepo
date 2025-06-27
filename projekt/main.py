import datetime
import logging
import math
import os
import re
import subprocess

from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory,send_file

from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.scrapers.stepstone_scraper import StepStoneScraper
from projekt.backend.scrapers.xing_scraper import XingScraper
from projekt.backend.core.models import SearchCriteria,ApplicantProfile,JobSource,JobDetailsAi,JobDetailsScraped
from projekt.backend.core.config import app_config
from projekt.backend.utils.pdf_utils import markdown_to_pdf, merge_pdfs_by_rating

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
app = Flask(__name__, static_folder=app_config.paths.build_dir)
app.logger.setLevel(logging.INFO)

def create_session_directory(job_title: str, location: str,job_source: JobSource) -> str:
    try:
        now = datetime.datetime.now()
        ds = now.strftime("%d.%m.%Y")
        ts = now.strftime("%H-%M")
        def clean(s: str, mx: int) -> str:
            c = re.sub(r'[^0-9A-Za-z\s]', '', s).strip()
            c = re.sub(r'\s+', '_', c)[:mx]
            return c or "Unbekannt"
        dname = (
            f"{clean(job_title,25)}_"
            f"{clean(location,15)}_"
            f"{clean(job_source.value,15)}_"
            f"{ds}_{ts}"
        )
        path = os.path.join(app_config.paths.temp_pdfs_dir, dname)
        os.makedirs(path, exist_ok=True)
        return path

    except Exception as e:
        app.logger.error("Session-Verz err: %s", e)
        return str(app_config.paths.temp_pdfs_dir)

def setup_frontend_and_server() -> bool:
    try:
        bd = app_config.paths.build_dir
        if not os.path.exists(bd) or not os.listdir(bd):
            app.logger.info("Baue Frontend …")
            subprocess.run(
                ["npm", "run", "build"],
                cwd=app_config.paths.frontend_dir,
                check=True
            )
            app.logger.info("Frontend gebaut")
        return True

    except Exception as e:
        app.logger.error("Frontend-Setup fehlgeschlagen: %s", e)
        return False

def process_stepstone_jobs(search_criteria: SearchCriteria,applicant_profile: ApplicantProfile) -> list[JobDetailsAi]:
    scraper = StepStoneScraper()
    tp = TextProcessor()
    ai_jobs: list[JobDetailsAi] = []

    try:
        scraper.open_client()
        start_url = scraper.build_search_url(search_criteria, page=1)
        max_page = scraper.get_max_pages(start_url)
        app.logger.info("StepStone: %d Seiten gefunden", max_page)

        all_urls = []
        for p in range(1, max_page + 1):
            page_url = scraper.build_search_url(search_criteria, page=p)
            urls = scraper.extract_job_urls(page_url)
            app.logger.info(" Seite %d: %d Jobs", p, len(urls))
            all_urls.extend(urls)

        all_urls = list(dict.fromkeys(all_urls))

        for url in all_urls:
            if scraper.legit_job_counter >= app_config.scraping.max_jobs_to_prozess_session:
                break
            jd = scraper.extract_job_details_scraped(url)
            if not jd or not jd.is_internship:
                continue
            rating = tp.rate_job_match(jd, applicant_profile)
            app.logger.info("StepStone Rating: %d", rating)
            if rating >= app_config.ai.cover_letter_min_rating_premium:
                model_enum = app_config.ai.cover_letter_model_premium
                threshold = app_config.ai.cover_letter_min_rating_premium
            else:
                model_enum = app_config.ai.cover_letter_model
                threshold = app_config.ai.cover_letter_min_rating
            if rating >= threshold:
                scraper.legit_job_counter += 1
                formatted = tp.format_job_description(jd.raw_text)
                cover = tp.generate_anschreiben(jd, applicant_profile, model_enum.value)
                ai_jobs.append(JobDetailsAi(
                    scraped=jd,
                    rating=rating,
                    formatted_text=formatted,
                    cover_letters=cover,
                    ai_model_used=model_enum
                ))

    finally:
        scraper.close_client()

    return ai_jobs

def process_xing_jobs(search_criteria: SearchCriteria,applicant_profile: ApplicantProfile) -> list[JobDetailsAi]:
    scraper = XingScraper()
    tp = TextProcessor()
    ai_jobs: list[JobDetailsAi] = []

    try:
        scraper.open_client()
        start_url = scraper.build_search_url(search_criteria)
        if not scraper.load_url(start_url):
            return []

        html = scraper.get_html_content() or ""
        soup = BeautifulSoup(html, "html.parser")
        cfg = scraper.config

        class_str = cfg.get("max_job_amount", "")
        selector = "." + ".".join(class_str.split())
        el = soup.select_one(selector)
        if el and el.get_text(strip=True):
            digits = re.sub(r"[^\d]", "", el.get_text(strip=True))
            total_jobs = int(digits) if digits else 0
        else:
            total_jobs = 0

        per_load = cfg.get("jobs_per_lazyload", 20)
        iterations = max(1, math.ceil(total_jobs / per_load))
        app.logger.info("Xing: %d Jobs → %d Lazy-Loads", total_jobs, iterations)
        scraper.get_to_bottom(iterations)

        urls = scraper.extract_job_urls()
        urls = list(dict.fromkeys(urls))

        for url in urls:
            if scraper.legit_job_counter >= app_config.scraping.max_jobs_to_prozess_session:
                break
            jd = scraper.extract_job_details_scraped(url)
            if not jd or not jd.is_internship:
                continue
            rating = tp.rate_job_match(jd, applicant_profile)
            app.logger.info("Xing Rating: %d", rating)
            if rating >= app_config.ai.cover_letter_min_rating_premium:
                model_enum = app_config.ai.cover_letter_model_premium
                threshold = app_config.ai.cover_letter_min_rating_premium
            else:
                model_enum = app_config.ai.cover_letter_model
                threshold = app_config.ai.cover_letter_min_rating
            if rating >= threshold:
                scraper.legit_job_counter += 1
                formatted = tp.format_job_description(jd.raw_text)
                cover = tp.generate_anschreiben(jd, applicant_profile, model_enum.value)
                ai_jobs.append(JobDetailsAi(
                    scraped=jd,
                    rating=rating,
                    formatted_text=formatted,
                    cover_letters=cover,
                    ai_model_used=model_enum
                ))

    finally:
        scraper.close_client()

    return ai_jobs

@app.route('/api/create_job', methods=['POST'])
def create_job_summary():
    try:
        data = request.get_json() or {}
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

        src = data.get("jobSites", "")
        source_map = {
            "StepStone": JobSource.STEPSTONE,
            "Xing":      JobSource.XING
        }
        selected = source_map.get(src)
        if not selected:
            return jsonify(success=False,error=f"Unbekannte Quelle '{src}'"), 400

        session_dir = create_session_directory(
            search_criteria.job_title,
            search_criteria.location,
            selected
        )

        if selected == JobSource.STEPSTONE:
            ai_jobs = process_stepstone_jobs(search_criteria, applicant_profile)
        else:
            ai_jobs = process_xing_jobs(search_criteria, applicant_profile)

        for job in ai_jobs:
            markdown_to_pdf(
                jobdetailsai=job,
                session_dir=session_dir,
                rating=job.rating
            )

        merged_filename = "summary.pdf"
        merged_path = os.path.join(session_dir, merged_filename)
        if not merge_pdfs_by_rating(session_dir, merged_path):
            app.logger.error("Fehler beim Zusammenführen der PDFs")
            return jsonify(
                success=False,
                error="Fehler beim Erstellen der PDF-Zusammenfassung"
            ), 500

        return send_file(
            merged_path,
            as_attachment=True,
            download_name=merged_filename,
            mimetype='application/pdf'
        ), 200

    except Exception:
        app.logger.exception("Unerwarteter Fehler in create_job_summary")
        return jsonify(success=False,
                       error="Ein unerwarteter Fehler ist aufgetreten"), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    try:
        bd = app_config.paths.build_dir
        fp = os.path.join(bd, path)
        if path and os.path.exists(fp):
            return send_from_directory(bd, path)
        return send_from_directory(bd, 'index.html')

    except Exception as e:
        app.logger.error("Frontend-Fehler: %s", e)
        return f"Frontend nicht verfügbar: {e}", 500


def main():
    app.logger.info("Starte Server auf http://0.0.0.0:5000")
    if setup_frontend_and_server():
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        app.logger.error("Server-Start abgebrochen")


if __name__ == "__main__":
    main()