"""
gps_history.py
Records every GPS ping a taxi sends, so a trip can be replayed later.
Records only. Never decides anything about money.
"""
import sqlite3
from datetime import datetime, timezone, timedelta

from setup_taxi_db import get_db_path

MAX_FUTURE = timedelta(minutes=2)

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