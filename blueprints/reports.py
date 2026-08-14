from flask import Blueprint, session
from flask import send_file
import io
import datetime
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from utils import get_db, login_required

logger = logging.getLogger(__name__)

reports_bp = Blueprint("reports", __name__)


def build_taxi_rows(taxis):
    yield ["Plate", "Driver", "Trips", "Collected", "Target"]
    for taxi in taxis:
        yield [taxi["plate"], taxi["driver_name"] or "No driver",
               taxi["trips_today"], f"R{taxi['collected']}", f"R{taxi['target']}"]


def build_summary_rows(taxis):
    yield ["Plate", "Driver", "Trips", "Collected"]
    for taxi in taxis:
        yield [taxi["plate"], taxi["driver_name"] or "No driver",
               taxi["trips"], f"R{taxi['collected']}"]


def build_pdf_report(taxis, title, filename, row_builder):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 16)]

    rows = list(row_builder(taxis))
    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")


@reports_bp.route("/reports/daily")
@login_required
def download_daily_report():
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date = ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (today, today, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    logger.info("event=report_generated user=%s type=daily taxi_count=%d", session["user"], len(taxis))
    return build_pdf_report(taxis, f"Daily Report - {today}", f"separaka_daily_{today}.pdf", build_taxi_rows)


@reports_bp.route("/reports/weekly")
@login_required
def download_weekly_report():
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.plate, t.driver_name,
                COUNT(tr.id) as trips,
                COALESCE(SUM(dt.collected_amount), 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) >= ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date >= ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (week_ago, week_ago, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return build_pdf_report(taxis, f"Weekly Report ({week_ago} to {today})", f"separaka_weekly_{today}.pdf", build_summary_rows)


@reports_bp.route("/reports/monthly")
@login_required
def download_monthly_report():
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.plate, t.driver_name,
                COUNT(tr.id) as trips,
                COALESCE(SUM(dt.collected_amount), 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) >= ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date >= ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (month_ago, month_ago, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return build_pdf_report(taxis, f"Monthly Report ({month_ago} to {today})", f"separaka_monthly_{today}.pdf", build_summary_rows)