from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def build_taxi_rows():
    """Generator -- yields one formatted row at a time"""
    yield ["Plate", "Driver", "Trips", "Collected", "Target"]
    taxis = [
        {"plate": "MG85DS GP", "driver": "Lebo", "trips": 2, "collected": "720", "target": "850"},
        {"plate": "PL74QA GP", "driver": "Mpho", "trips": 3, "collected": "600", "target": "850"},
        {"plate": "LO67TG GP", "driver": "Shane", "trips": 5, "collected": "900", "target": "850"}
    ]

    for taxi in taxis:
        yield [taxi["plate"], taxi["driver"], taxi["trips"],
               f"R{taxi['collected']}", f"R{taxi['target']}"]

def generate_report():
    doc = SimpleDocTemplate("report.pdf", pagesize=letter)
    story = []
    rows = list(build_taxi_rows())
    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    doc.build(story)

def generate_simple_report():
    doc = SimpleDocTemplate("test_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Separaka Daily Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Owner: Chahane", styles["Normal"]))
    story.append(Paragraph("Date: 2026-07-28", styles["Normal"]))

    doc.build(story)

generate_report()
generate_simple_report()