"""
gps_history.py
Records every GPS ping a taxi sends, so a trip can be replayed later.
Records only. Never decides anything about money.
"""
import sqlite3
from datetime import datetime, timezone, timedelta

from utils import get_db_path

MAX_FUTURE = timedelta(minutes=2)
RETENTION_DAYS = 90

DB_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class PingError(ValueError):
    """A ping we refuse to store."""

def parse_recorded_at(raw, now=None):
    """Turn the phone's time into UTC text in DB_TIME_FORMAT."""
    if now is None:
        now = datetime.now(timezone.utc)

    if raw is None:
        return now.strftime(DB_TIME_FORMAT)

    if not isinstance(raw, str):
        raise PingError("recorded_at must be text")

    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        raise PingError("recorded_at is not a valid ISO time")

    if moment.tzinfo is None:
        raise PingError("recorded_at must include a time zone")

    moment = moment.astimezone(timezone.utc)

    if moment > now + MAX_FUTURE:
        raise PingError("recorded_at is in the future")

    return moment.strftime(DB_TIME_FORMAT)

def parse_accuracy(raw):
    """Accuracy in metres is optional. If sent, it must be a number >= 0."""
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise PingError("accuracy_m must be a number")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise PingError("accuracy_m must be a number")
    if value < 0:
        raise PingError("accuracy_m cannot be negative")
    return value

def save_ping(taxi_id, lat, lon, recorded_at, accuracy_m=None, db_path=None):
    """Write one ping. Returns the new row id."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            cursor = conn.execute(
                """INSERT INTO gps_pings (taxi_id, lat, lon, recorded_at, accuracy_m)
                   VALUES (?, ?, ?, ?, ?)""",
                (taxi_id, lat, lon, recorded_at, accuracy_m),
            )
        return cursor.lastrowid
    finally:
        conn.close()

def _to_db_time(moment, name):
    """A time-zone-aware datetime -> UTC text in DB_TIME_FORMAT."""
    if not isinstance(moment, datetime):
        raise PingError(f"{name} must be a datetime")
    if moment.tzinfo is None:
        raise PingError(f"{name} must include a time zone")
    return moment.astimezone(timezone.utc).strftime(DB_TIME_FORMAT)

def get_pings(taxi_id, start, end, db_path=None):
    """
    Every ping for one taxi between start and end (both included),
    oldest first, shape for gate_crossing.find_gate_times().
    """
    start_text = _to_db_time(start, "start")
    end_text = _to_db_time(end, "end")
    if end_text < start_text:
        raise PingError("end must not be before start")

    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """SELECT lat, lon, recorded_at, accuracy_m
                FROM gps_pings
                WHERE taxi_id = ?
                AND recorded_at BETWEEN ? AND ?
                ORDER BY recorded_at, id""",
            (taxi_id, start_text, end_text),
        ).fetchall()
    finally:
        conn.close()

    pings = []
    for lat, lon, recorded_at, accuracy_m in rows:
        moment = datetime.strptime(recorded_at, DB_TIME_FORMAT)
        pings.append({
            "lat": lat,
            "lon": lon,
            "time": moment.replace(tzinfo=timezone.utc),
            "accuracy_m": accuracy_m,
        })
    return pings

def delete_old_pings(days=RETENTION_DAYS, now=None, db_path=None):
    """Delete pings older than `days`. Returns how many were deleted."""
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise PingError("days must be a whole number of at least 1")

    if now is None:
        now = datetime.now(timezone.utc)
    cutoff = _to_db_time(now - timedelta(days=days), "now")

    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM gps_pings WHERE recorded_at < ?",
                (cutoff,),
            )
        return cursor.rowcount
    finally:
        conn.close()