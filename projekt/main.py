# Korrigierter Import mit korrektem Pfad
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import json

from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
from projekt.backend.utils.pdf_utils import PdfUtils

# Pfade definieren
frontend_dir = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
build_dir = os.path.join(frontend_dir, "build")

# Flask-App initialisieren
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
    text_processor = TextProcessor()
    pdf_utils = PdfUtils()

    try:
        data = request.json

        search_criteria = {
            "jobTitle": data.get("jobTitle", ""),
            "location": data.get("location", ""),
            "radius": data.get("radius", ""),
            "discipline": data.get("discipline", "")
        }

        if data.get("jobSites", ""):
            job_urls = stepstone.get_search_result_urls(search_criteria)
            print(f"Gefundene Job-URLs: {len(job_urls)}")

            if job_urls:
                job_details = stepstone.extract_job_details(job_urls[0])
                print(f"Job-Titel: {job_details.get('title')}")
                print(f"URL: {job_details.get('url')}")

            applicant_information = {
                "studyInfo": data.get("studyInfo", ""),
                "interests": data.get("interests", ""),
                "skills": data.get("skills", ""),
            }

            previous_cover_letter = job_details.get("pdfContents", "")

            if job_details:
                job_description = text_processor.format_job_description(job_details.get('raw_text'))
                rating = text_processor.rate_job_match(job_description,applicant_information)
                pdf_utils.markdown_to_pdf(job_description, job_details.get('title') + ".pdf", job_details.get('url'), rating)

            # Client richtig schließen
            stepstone.close_client()

        # HIER: Auch search_criteria ausgeben
        print("\n=== ERSTELLTE SUCH-KRITERIEN ===")
        print(json.dumps(search_criteria, indent=2))
        print(json.dumps(data, indent=2))
        print("===============================\n")

        return jsonify({
            "success": True,
            "message": "Formular erfolgreich empfangen!",
            "received_data": search_criteria
        })

    except Exception as e:
        print(f"Fehler: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
