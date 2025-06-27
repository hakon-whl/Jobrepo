import os
import re
import io
import markdown
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger
from projekt.backend.core.models import JobDetailsAi

def markdown_to_pdf(jobdetailsai: JobDetailsAi, session_dir: str, rating: int) -> bool:
    filename = jobdetailsai.get_output_filename()
    os.makedirs(session_dir, exist_ok=True)
    target_path = os.path.join(session_dir, filename)

    clean_md = lambda txt: re.sub(r"```(?:markdown)?\n?|```", "", txt or "").strip()
    parts = []
    if rating is not None:
        parts.append(f"## {rating} von 10")
    if jobdetailsai.scraped.title:
        parts.append(f"## {jobdetailsai.scraped.title}")
    if jobdetailsai.formatted_text:
        parts.append(clean_md(jobdetailsai.formatted_text))
    if jobdetailsai.cover_letters:
        parts.append("## Anschreiben")
        parts.append(clean_md(jobdetailsai.cover_letters))
    parts.append(f"[Original Job Posting]({jobdetailsai.scraped.url})")

    html = markdown.markdown("\n\n".join(parts))
    with open(target_path, "wb") as f:
        err = pisa.CreatePDF(io.StringIO(html), dest=f).err

    return not err

def merge_pdfs_by_rating(src_dir: str, dest: str) -> bool:
    def rate(fn):
        m = re.match(r'(\d+)_', fn)
        return int(m.group(1)) if m else -1

    pdfs = sorted(
        [f for f in os.listdir(src_dir) if f.lower().endswith('.pdf')],
        key=rate,
        reverse=True
    )

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(os.path.join(src_dir, pdf))
    merger.write(dest)
    merger.close()

    return True