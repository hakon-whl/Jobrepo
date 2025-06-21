import markdown
from xhtml2pdf import pisa
import io
import os
import re
import PyPDF2
import logging

logger = logging.getLogger(__name__)


class PdfUtils:
    @staticmethod
    def markdown_to_pdf(markdown_string, path, job_titel, link, rating, anschreiben=None):
        try:
            logger.info(f"Erstelle PDF für Job: {job_titel}")

            cleaned_job_description = re.sub(r'```markdown|```', '', markdown_string).strip()
            cleaned_job_anschreiben = re.sub(r'```markdown|```', '', anschreiben).strip() if anschreiben else ""

            all_content_blocks = []

            if rating is not None:
                all_content_blocks.append(f"## {str(rating).strip()} von 10")

            if job_titel:
                all_content_blocks.append(f"## {job_titel.strip()}")

            if cleaned_job_description:
                all_content_blocks.append(cleaned_job_description)

            if cleaned_job_anschreiben and cleaned_job_anschreiben.strip():
                all_content_blocks.append("## Anschreiben\n\n" + cleaned_job_anschreiben.strip())

            link_text = "Original Job Posting"
            link_markdown = f"[{link_text}]({link})"
            all_content_blocks.append(link_markdown)

            final_markdown_input = "\n\n".join(filter(None, all_content_blocks))

            html_string = markdown.markdown(final_markdown_input)
            source_html = io.BytesIO(html_string.encode('UTF-8'))

            with open(path, "w+b") as output_file:
                pisa_status = pisa.pisaDocument(
                    source_html,
                    dest=output_file,
                    encoding='UTF-8'
                )

            if pisa_status.err:
                logger.error(f"Fehler bei der PDF-Erstellung: {pisa_status.err}")
                return False
            else:
                logger.info(f"PDF erfolgreich erstellt: {job_titel}")
                return True

        except Exception as e:
            logger.error(f"Ein Fehler ist in markdown_to_pdf aufgetreten: {e}")
            return False

    @staticmethod
    def get_rating_from_filename(filename):
        match = re.search(r'^(\d+)_', filename)
        if match:
            try:
                rating = int(match.group(1))
                logger.debug(f"Rating aus Dateiname extrahiert: {rating} ({filename})")
                return rating
            except ValueError:
                logger.warning(f"Konnte den Rating-Wert aus '{filename}' nicht interpretieren.")
                return None
        return None

    @staticmethod
    def merge_pdfs_by_rating(source_dir, output_filepath):
        logger.info(f"Beginne Zusammenführung von PDFs aus '{source_dir}' nach '{output_filepath}'...")

        if not os.path.isdir(source_dir):
            logger.error(f"Der Quellordner '{source_dir}' existiert nicht.")
            return False

        pdf_files_info = []

        for entry_name in os.listdir(source_dir):
            full_path = os.path.join(source_dir, entry_name)
            if os.path.isfile(full_path) and entry_name.lower().endswith('.pdf'):
                rating = PdfUtils.get_rating_from_filename(entry_name)
                pdf_files_info.append((rating if rating is not None else -1, full_path))

        if not pdf_files_info:
            logger.warning(f"Keine PDF-Dateien im Ordner '{source_dir}' gefunden.")
            return False

        sorted_pdf_files = sorted(pdf_files_info, key=lambda item: item[0], reverse=True)

        logger.info(f"Gefundene und sortierte Dateien zur Zusammenführung:")
        for rating, path in sorted_pdf_files:
            logger.info(f"  Rating {rating}: {os.path.basename(path)}")

        merger = PyPDF2.PdfMerger()
        success = False

        try:
            for rating, pdf_path in sorted_pdf_files:
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        merger.append(pdf_file)
                        logger.debug(f"PDF hinzugefügt: {os.path.basename(pdf_path)}")
                except Exception as e:
                    logger.error(f"Fehler bei der Datei '{os.path.basename(pdf_path)}': {e}. Überspringe.")
                    continue

            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    logger.info(f"Zielverzeichnis erstellt: {output_dir}")
                except OSError as e:
                    logger.error(f"Konnte Zielverzeichnis '{output_dir}' nicht erstellen: {e}")
                    raise

            with open(output_filepath, 'wb') as output_pdf_file:
                merger.write(output_pdf_file)

            logger.info(f"PDF-Dateien erfolgreich zusammengeführt als '{output_filepath}'")
            success = True

        except Exception as e:
            logger.error(f"Ein schwerwiegender Fehler ist aufgetreten: {e}")
            success = False

        finally:
            return success