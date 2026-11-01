from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

import fitz

from unicont_poc.domain import PageText

MINIMUM_TEXT_LAYER_CHARACTERS = 25
OCR_DOTS_PER_INCH = 200


def _recognize_page(page: fitz.Page) -> str:
    pixmap = page.get_pixmap(dpi=OCR_DOTS_PER_INCH, colorspace=fitz.csGRAY)
    with tempfile.TemporaryDirectory() as directory:
        image_path = Path(directory) / "pagina.png"
        pixmap.save(image_path)
        completed = subprocess.run(
            ["tesseract", str(image_path), "stdout", "-l", "por", "--psm", "6"],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "OMP_THREAD_LIMIT": "1"},
        )
    return completed.stdout


def read_pdf_pages(pdf_path: Path) -> tuple[tuple[PageText, ...], bool, str]:
    pdf_bytes = pdf_path.read_bytes()
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    pages: list[PageText] = []
    was_scanned = False
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for number, page in enumerate(document, start=1):
            text = page.get_text()
            if len(text.strip()) < MINIMUM_TEXT_LAYER_CHARACTERS:
                text = _recognize_page(page)
                was_scanned = True
            pages.append(PageText(number, text))
    return tuple(pages), was_scanned, digest
