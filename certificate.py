"""Proof-of-authorship certificate (PDF)."""
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from models import TrackRecord


def generate_certificate(rec: TrackRecord) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 110, "Certificate of Authorship")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 135, "Music AI Solutions")

    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 200, "This certifies that the work")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 235, rec.title)
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 270, f"by {rec.artist}")
    c.drawCentredString(width / 2, height - 295, f"was registered on {rec.registered_at} (UTC)")

    c.setFont("Helvetica-Bold", 10)
    y = height - 380
    for label, value in (
        ("Certificate ID", rec.id),
        ("File SHA-256", rec.sha256),
        ("Audio fingerprint", rec.fingerprint_id),
        ("Duration", f"{rec.duration_s} s"),
    ):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, label)
        c.setFont("Courier", 8)
        c.drawString(60, y - 14, value)
        y -= 44

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2, 70, "A registry record of when this audio was fingerprinted. It is not a copyright registration."
    )
    c.showPage()
    c.save()
    return buf.getvalue()
