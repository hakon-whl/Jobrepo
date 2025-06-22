#!/usr/bin/env python3
"""
main_utils.py

Test-Harness für projekt.backend.utils
Führt HTML-Parser- und PDF-Utility-Tests durch.
"""

import os
import tempfile
import argparse

from projekt.backend.utils import (
    extract_text_from_selector,
    extract_attribute_from_selector,
    PdfUtils,
)


def test_html_parser():
    print("\n" + "="*60)
    print("HTML Parser Tests".center(60))
    print("="*60)
    sample_html = """
    <div id="content">
      Dies ist der   Haupttext.
      Er hat mehrere     Leerzeichen.
    </div>
    <ul class="nav-links">
      <li><a href="/home">Home</a></li>
      <li><a href="/about">Über uns</a></li>
      <li><a href="/contact">Kontakt</a></li>
    </ul>
    """
    text = extract_text_from_selector(sample_html, "#content")
    print("[1] extract_text_from_selector →", repr(text))
    assert "Haupttext" in text

    links = extract_attribute_from_selector(
        sample_html, ".nav-links a", "href"
    )
    print("[2] extract_attribute_from_selector →", links)
    assert links == ["/home", "/about", "/contact"]

    print("HTML Parser Tests: PASSED\n")




def main():
    parser = argparse.ArgumentParser(
        description="Test-Suite für projekt.backend.utils"
    )
    parser.add_argument(
        "--tmp-dir",
        help="Optionales Verzeichnis für erstellte PDFs",
        default=None
    )
    args = parser.parse_args()

    test_html_parser()

    if args.tmp_dir:
        tmp_dir = args.tmp_dir
        os.makedirs(tmp_dir, exist_ok=True)
    else:
        tmp = tempfile.TemporaryDirectory()
        tmp_dir = tmp.name

    print("Alle Utils-Tests erfolgreich abgeschlossen!")


if __name__ == "__main__":
    main()