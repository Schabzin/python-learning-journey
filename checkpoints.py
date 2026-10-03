"""
checkpoints.py -- route chechpointchains (runtime logic).

A chain is an ordered list of gates along one route. Each gate stores
the fare for passengers who board AFTER passing it. The route's own
fare-per_passenger is the full fare for boardings before the first gate.
"""

import math
import sqlite3

from utils import get_db_path

MIN_GATES = 2

class CheckpointChainError(ValueError):
    """Raised when a chain request is invalid. Nothing is saved."""

def _is_real_int(value):
    """True for real integers. Rejects bool, because True == 1 in Python."""
    return isinstance(value, int) and not isinstance(value, bool)

def _is_valid_fare(value):
    """None (no boarding expected) or a real, finite number above 0."""
    if value is None:
        return True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value) and value > 0

def _connect(db_path):
    """Open a connection with foreign keys switched ON (SQLite defaults to OFF)."""
    conn = sqlite3.connect(db_path if db_path is not None else get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def set_checkpoint_chain(route_id, gates, db_path=None):
    """
    Saves a route's gates in order, replacing any existing chain.

    gates: list of dicts IN ROUTE ORDER, e.g.
        [{"zone_id": 240, "boarding_fare": 18},
         {"zone_id": 241, "boarding_fare": 15},
         {"zone_id": 242, "boarding_fare": None}]

    Every check runs before anything is written.
    """
    if not _is_real_int(route_id):
        raise CheckpointChainError(f"route_id must be an integer, got {route_id!r}")
    if not isinstance(gates, (list, tuple)):
        raise CheckpointChainError("gates must be a list, in route order")
    if len(gates) < MIN_GATES:
        raise CheckpointChainError(
            f"A chain needs at least {MIN_GATES} gates, got {len(gates)}"
        )

    zone_ids = []
    for position, gate in enumerate(gates, start=1):
        if not isinstance(gate, dict) or "zone_id" not in gate or "boarding_fare" not in gate:
            raise CheckpointChainError(
                f"Gate {position} must be a dict with 'zone_id' and 'boarding_fare'"
            )
        if not _is_real_int(gate["zone_id"]):
            raise CheckpointChainError(f"Gate {position}: zone_id must be an integer")
        if not _is_valid_fare(gate["boarding_fare"]):
            raise CheckpointChainError(
                f"Gate {position}: boarding_fare must be None or a number above 0"
            )
        zone_ids.append(gate["zone_id"])

    duplicates = sorted({z for z in zone_ids if zone_ids.count(z) > 1})
    if duplicates:
        raise CheckpointChainError(f"A zone can only appear once in a chain: {duplicates}")

    conn = _connect(db_path)
    try:
        route = conn.execute(
            "SELECT fare_per_passenger FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if route is None:
            raise CheckpointChainError(f"Route {route_id} does not exist")
        if not route[0] or route[0] <= 0:
            raise CheckpointChainError(
                f"Route {route_id} has no full fare set -- set fare_per_passenger first"
            )
        placeholders = ", ".join("?" for _ in zone_ids)
        rows = conn.execute(
            f"SELECT id, active, zone_type FROM geofence_zones WHERE id IN ({placeholders})",
            tuple(zone_ids),
        ).fetchall()
        found = {zone_id: (active, zone_type) for zone_id, active, zone_type in rows}

        missing = [z for z in zone_ids if z not in found]
        if missing:
            raise CheckpointChainError(f"These zones do not exist: {missing}")

        inactive = [z for z in zone_ids if found[z][0] != 1]
        if inactive:
            raise CheckpointChainError(f"These zones are deactivated: {inactive}")

        not_checkpoints = [z for z in zone_ids if found[z][1] != "checkpoint"]
        if not_checkpoints:
            raise CheckpointChainError(
                f"Gates must be 'checkpoint' zones, these are not: {not_checkpoints}"
            )

        with conn:
            conn.execute("DELETE FROM route_checkpoints WHERE route_id = ?", (route_id,))
            conn.executemany(
                "INSERT INTO route_checkpoints (route_id, zone_id, sequence, boarding_fare) "
                "VALUES (?, ?, ?, ?)",
                [
                    (route_id, gate["zone_id"], position, gate["boarding_fare"])
                    for position, gate in enumerate(gates, start=1)
                ],

            )
    finally:
        conn.close()

    return get_checkpoint_chain(route_id, db_path=db_path)

def get_checkpoint_chain(route_id, db_path=None):
    """
    Returns a route's full fare and its gates in order.

    {"route_id": 20, "full_fare": 24.0, "gates": [ {...}, {...} ]}

    An EMPTY gates list means this route has no chain -- callers must
    fall back to cross-taxi corroboration (corroboration.py).
    """
    if not _is_real_int(route_id):
        raise CheckpointChainError(f"route_id must be an integer, got {route_id!r}")

    conn = _connect(db_path)
    try:
        route = conn.execute(
            "SELECT fare_per_passenger FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if route is None:
            raise CheckpointChainError(f"Route {route_id} does not exist")

        rows = conn.execute(
            """
            SELECT rc.sequence, rc.zone_id, rc.boarding_fare,
                   gz.name, gz.center_lat, gz.center_lon, gz.radius_meters, gz.active
            FROM route_checkpoints AS rc
            JOIN geofence_zones AS gz ON gz.id = rc.zone_id
            WHERE rc.route_id = ?
            ORDER BY rc.sequence ASC
            """,
            (route_id,),
        ).fetchall()
    finally:
        conn.close()

    return {
        "route_id": route_id,
        "full_fare": route[0],
        "gates": [
            {
                "sequence": r[0],
                "zone_id": r[1],
                "boarding_fare": r[2],
                "name": r[3],
                "center_lat": r[4],
                "center_lon": r[5],
                "radius_meters": r[6],
                "active": r[7],
            }
            for r in rows
        ],
    }

         