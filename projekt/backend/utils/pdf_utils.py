import os
import re
import io
import markdown
from xhtml2pdf import pisa
from PyPDF2 import PdfMerger

def _clean(text: str) -> str:
    return re.sub(r'```(?:markdown)?\n?|```', '', text or '').strip()

def markdown_to_pdf(cover_letter: str, dest: str, title: str, link: str, rating: int = None) -> bool:
    parts = []
    if rating is not None:
        parts.append(f"## {rating} von 10")
    if title:
        parts.append(f"## {title}")

    if cover_letter:
        parts.append("## Anschreiben")
        parts.append(_clean(cover_letter))

    parts.append(f"[Original Job Posting]({link})")

    html = markdown.markdown("\n\n".join(parts))
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    with open(dest, "wb") as f:
        err = pisa.CreatePDF(io.StringIO(html), dest=f).err
    return not err

def merge_pdfs_by_rating(src_dir: str, dest: str) -> bool:
    """Führt alle PDFs in src_dir nach Rating (aus Dateinamen) zusammen."""
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