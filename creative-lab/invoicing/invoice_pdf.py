"""invoice_pdf.py - draws a Separaka invoice. All money comes from invoice_maths (cents)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from invoice_maths import rand, split_deposit, invoice_total

COMPANY = ["Separaka Holdings (Pty) Ltd", "Sechaba Mofokeng",
           "073 223 9762  |  info@separaka.co.za  | separakaholdings.co.za"]


def load_bank(path="bank.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def draw_invoice(out_path, inv, bank):
    c = canvas.Canvas(out_path, pagesize=A4)
    left, right = 20 * mm, 190 * mm
    y = 277 * mm

    c.setFont("Helvetica-Bold", 18); c.drawString(left, y, "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawRightString(right, y, inv["number"])
    for line in COMPANY:
        y -= 6 * mm; c.drawString(left, y, line)
    y -= 6 * mm; c.drawRightString(right, y, f"Date: {inv['date']}")

    y -= 12 * mm; c.setFont("Helvetica-Bold", 11); c.drawString(left, y, "Bill to:")
    c.setFont("Helvetica", 10)
    for line in inv["bill_to"]:
        y -= 6 * mm; c.drawString(left, y, line)

    y -= 12 * mm; c.setFont("Helvetica-Bold", 10)
    c.drawString(left, y, "Description"); c.drawRightString(right, y, "Amount")
    c.setFont("Helvetica", 10)
    for description, qty, unit_cents in inv["items"]:
        y -= 7 * mm
        c.drawString(left, y, f"{description} (x{qty})")
        c.drawRightString(right, y, rand(qty * unit_cents))

    total = invoice_total(inv["items"])
    deposit, balance = split_deposit(total, inv["deposit_percent"])
    y -= 10 * mm; c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y, "Total"); c.drawRightString(right, y, rand(total))
    y -= 7 * mm
    c.drawString(left, y, f"Deposit due now ({inv['deposit_percent']}%)"); c.drawRightString(right, y, rand(deposit))
    c.setFont("Helvetica", 10)
    y -= 7 * mm
    c.drawString(left, y, "Balance due when the website goes live"); c.drawRightString(right, y, rand(balance))

    y -= 14 * mm; c.setFont("Helvetica-Bold", 11); c.drawString(left, y, "Banking details")
    c.setFont("Helvetica", 10)
    for label, key in [("Bank", "bank"), ("Account name", "account_name"), ("Account number", "account_number"),
                       ("Branch code", "branch_code"), ("Account type", "account_type")]:
        y -= 6 * mm; c.drawString(left, y, f"{label}: {bank[key]}")
    y -= 6 * mm; c.drawString(left, y, f"Reference: {inv['number']}")

    c.save()
    