from __future__ import annotations

import io
from random import Random

import fitz
from PIL import Image, ImageFilter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape

from unicont_poc.corpus.contract import DocumentDraft

SYNTHETIC_NOTICE = "DOCUMENTO SINTÉTICO – SEM VALOR LEGAL – PoC CPSI 001/2026"
_BODY = ParagraphStyle("corpo", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=8)
_TITLE = ParagraphStyle(
    "titulo", fontName="Helvetica-Bold", fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=14
)
_SCAN_DOTS_PER_INCH = 150


def _draw_footer(canvas, document) -> None:
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, SYNTHETIC_NOTICE)


def render_text_pdf(draft: DocumentDraft, sei_number: str) -> bytes:
    buffer = io.BytesIO()
    story = []
    if draft.title:
        story.append(Paragraph(escape(draft.title), _TITLE))
    for paragraph in draft.paragraphs:
        story.append(Paragraph(escape(paragraph), _BODY))
    story.extend((Spacer(1, 12), Paragraph(f"SEI nº {sei_number}", _BODY)))
    SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2 * cm, bottomMargin=2 * cm
    ).build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()


def _degrade_as_scan(page_image: Image.Image, random_source: Random) -> Image.Image:
    grayscale = page_image.convert("L")
    rotated = grayscale.rotate(random_source.uniform(-1.1, 1.1), resample=Image.Resampling.BILINEAR, fillcolor=255)
    softened = rotated.filter(ImageFilter.GaussianBlur(radius=random_source.uniform(0.3, 0.7)))
    speckle = Image.effect_noise(softened.size, random_source.uniform(10, 26))
    return Image.blend(softened, speckle, random_source.uniform(0.03, 0.09))


def convert_to_scanned_pdf(text_pdf: bytes, random_source: Random) -> bytes:
    source = fitz.open(stream=text_pdf, filetype="pdf")
    scanned = fitz.open()
    for page in source:
        pixmap = page.get_pixmap(dpi=_SCAN_DOTS_PER_INCH)
        page_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        encoded = io.BytesIO()
        _degrade_as_scan(page_image, random_source).save(encoded, format="JPEG", quality=random_source.randint(45, 70))
        new_page = scanned.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=encoded.getvalue())
    return scanned.tobytes(deflate=True)
