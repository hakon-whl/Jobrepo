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

            link_markdown = f"[Original Job Posting]({link})"
            all_content_blocks.append(link_markdown)

            final_markdown_input = "\n\n".join(filter(None, all_content_blocks))
            html_string = markdown.markdown(final_markdown_input)
            source_html = io.BytesIO(html_string.encode('UTF-8'))

            with open(path, "w+b") as output_file:
                pisa_status = pisa.pisaDocument(source_html, dest=output_file, encoding='UTF-8')

            return not pisa_status.err
        except Exception as e:
            logger.error(f"PDF-Erstellung Fehler: {e}")
            return False

    @staticmethod
    def get_rating_from_filename(filename):
        match = re.search(r'^(\d+)_', filename)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    @staticmethod
    def merge_pdfs_by_rating(source_dir, output_filepath):
        if not os.path.isdir(source_dir):
            return False

        pdf_files_info = []
        for entry_name in os.listdir(source_dir):
            full_path = os.path.join(source_dir, entry_name)
            if os.path.isfile(full_path) and entry_name.lower().endswith('.pdf'):
                rating = PdfUtils.get_rating_from_filename(entry_name)
                pdf_files_info.append((rating if rating is not None else -1, full_path))

        if not pdf_files_info:
            return False

        sorted_pdf_files = sorted(pdf_files_info, key=lambda item: item[0], reverse=True)
        merger = PyPDF2.PdfMerger()

        try:
            for rating, pdf_path in sorted_pdf_files:
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        merger.append(pdf_file)
                except Exception:
                    continue

            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_filepath, 'wb') as output_pdf_file:
                merger.write(output_pdf_file)

            return True
        except Exception as e:
            logger.error(f"PDF-Merge Fehler: {e}")
            return False