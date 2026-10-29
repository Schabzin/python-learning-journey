from urllib.parse import quote
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from qr import make_qr, read_qr
from sheets import SHEETS

NAVY = (0.08, 0.13, 0.24)
AMBER = (0.99, 0.64, 0.07)
MARGIN = 20 * mm
CONTACT = ["Sechaba Mofokeng", "Separaka Holdings (Pty) Ltd",
           "073 223 9762 (call / WhatsApp)", "info@separaka.co.za", "separaka.co.za"]


def chat_link(code):
    return "https://wa.me/27732239762?text=" + quote(f"Hi Sechaba, I saw your sheet ({code}).")


def draw_wrapped(c, text, x, y, width, font, size):
    c.setFont(font, size)
    for line in simpleSplit(text, font, size, width):
        c.drawString(x, y, line)
        y -= size * 1.3
    return y


def make_sheet(code, path):
    sheet = SHEETS[code]
    w, h = A4
    c = canvas.Canvas(path, pagesize=A4)

    c.setFillColorRGB(*NAVY)
    c.rect(0, h - 45 * mm, w, 45 * mm, fill=1, stroke=0)
    c.setFillColorRGB(*AMBER)
    c.rect(0, h - 47 * mm, w, 2 * mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, h - 20 * mm, "SEPARAKA HOLDINGS")

    c.setFillColorRGB(*NAVY)
    y = draw_wrapped(c, sheet["headline"], MARGIN, h - 70 * mm, w - 2 * MARGIN, "Helvetica-Bold", 30)
    y = draw_wrapped(c, sheet["intro"], MARGIN, y - 6 * mm, w - 2 * MARGIN, "Helvetica", 13)

    y -= 8 * mm
    
    for point in sheet["points"]:
        c.setFillColorRGB(*AMBER)
        c.rect(MARGIN, y - 1 * mm, 4 * mm, 4 * mm, fill=1, stroke=0)
        c.setFillColorRGB(*NAVY)
        y = draw_wrapped(c, point, MARGIN + 8 * mm, y, w - 2 * MARGIN - 8 * mm, "Helvetica", 13) - 4 * mm

    proof = sheet.get("proof")
    if proof:
        draw_wrapped(c, proof, MARGIN, y -4 * mm, w - 2 * MARGIN, "Helvetica-Oblique", 13)

    link = chat_link(code)
    qr_path = f"{path}.qr.png"
    make_qr(link, qr_path)
    if read_qr(qr_path) != link:
        raise ValueError("QR does not read back - sheet not made.")
    qr_size = 45 * mm
    c.drawImage(qr_path, MARGIN, 40 * mm, width=qr_size, height=qr_size)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, 34 * mm, f"Scan to chat on WhatsApp  ({code})")

    x = MARGIN + qr_size + 15 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, 75 * mm, CONTACT[0])
    c.setFont("Helvetica", 11)
    for i, line in enumerate(CONTACT[1:]):
        c.drawString(x, 68 * mm - i * 6 * mm, line)

    c.save()


if __name__ == "__main__":
    for code in SHEETS:
        make_sheet(code, f"sheet_{code}.pdf")
        print(f"Made sheet_{code}.pdf")