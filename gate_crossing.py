"""
gate_crossing.py -- works out WHEN a taxi passed each checkpoint gate,
even if no GPS ping landed inside the gate.

Distance here are only ever a few kilometres around one gate, so we use
a flat (equirectangular) approximation: accurate to well under a metre at
that scale, and it lets us use simple straight-line geometry.
"""

import math
from datetime import datetime

EARTH_RADIUS_M = 6_371_000

class GateCrossingError(ValueError):
    """Raised when the GPS input is invalid."""

def _check_coordinate(lat, lon, label):
    """Rejects anything that isn't a real, in-range GPS coordinate."""
    for name, value in (("lat", lat), ("lon", lon)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise GateCrossingError(f"{label} {name} must be a number, got {value!r}")
        if not math.isfinite(value):
            raise GateCrossingError(f"{label} {name} must be finite, got {value!r}")
        if not -90 <= lat <= 90:
            raise GateCrossingError(f"{label} latitude out of range: {lat}")
        if not -180 <= lon <= 180:
            raise GateCrossingError(f"{label} longitude out of range: {lon}")

def to_local_metres(lat, lon, origin_lat, origin_lon):
    """
    Converts a GPS point into flat (x, y) metres measured from an origin.
    x = metres east of the origin, y = metres north of the origin.
    """
    _check_coordinate(lat, lon, "point")
    _check_coordinate(origin_lat, origin_lon, "origin")

    x = math.radians(lon - origin_lon) * EARTH_RADIUS_M * math.cos(math.radians(origin_lat))
    y = math.radians(lat - origin_lat) * EARTH_RADIUS_M 
    return x, y

def _check_gate(gate):
    """A gate needs a valid centre and a real, positive radius."""
    if not isinstance(gate, dict):
        raise GateCrossingError("gate must be a dict")
    for key in ("center_lat", "center_lon", "radius_meters"):
        if key not in gate:
            raise GateCrossingError(f"gate is missing '{key}'")
        _check_coordinate(gate["center_lat"], gate["center_lon"], "gate centre")
        radius = gate["radius_meters"]
        if isinstance(radius, bool) or not isinstance(radius, (int, float)) \
                or not math.isfinite(radius) or radius <= 0:
            raise GateCrossingError(f"radius_meters must be a number above 0, got {radius!r}")

def _check_ping(ping, label):
    """A ping needs a valid position and a real datetime."""
    if not isinstance(ping, dict):
        raise GateCrossingError(f"{label} must be a dict")
    for key in ("lat", "lon", "time"):
        if key not in ping:
            raise GateCrossingError(f"{label} is missing '{key}'")
    _check_coordinate(ping["lat"], ping["lon"], label)
    if not isinstance(ping["time"], datetime):
        raise GateCrossingError(f"{label} time must be a datetime, got {ping['time']!r}")

def find_gate_crossing(ping_a, ping_b, gate):
    """
    Did the taxi pass through the gate while driving from ping_a to ping_b?

    ping_a, ping_b: {"lat", "lon", "time"} -- consecutive pings, a before b.
    gate:           {"center_lat", "center_lon", "radius_meters"}

    Returns None if the straight path between the pings misses the gate.
    Otherwise returns evidence, not just a time:
        {"time": <estimated crossing datetime>,
         "closest_m": <closest distance to the gate centre, metres>,
         "fraction": <0..1, how far from a to b the closest point was>}
    """
    _check_ping(ping_a, "ping_a")
    _check_ping(ping_b, "ping_b")
    _check_gate(gate)
    if ping_b["time"] < ping_a["time"]:
        raise GateCrossingError("ping_b must not be earlier than ping_a")

    ax, ay = to_local_metres(ping_a["lat"], ping_a["lon"], gate["center_lat"], gate["center_lon"])
    bx, by = to_local_metres(ping_b["lat"], ping_b["lon"], gate["center_lat"], gate["center_lon"])

    dx, dy = bx - ax, by -ay
    length_sq = dx * dx + dy * dy

    if length_sq == 0:
        t = 0.0
    else:
        t = -(ax * dx + ay * dy) / length_sq
        t = max(0.0, min(1.0, t))

    closest_x, closest_y = ax + t * dx, ay + t * dy
    closest_m = math.hypot(closest_x, closest_y)

    if closest_m > gate["radius_meters"]:
        return None

    crossing_time = ping_a["time"] + (ping_b["time"] - ping_a["time"]) * t
    return {"time": crossing_time, "closest_m": round(closest_m, 1), "fraction": round(t, 3)}

def find_gate_times(pings, gates):
    """
    Finds when the taxi passed each gate on its route, in route order.

    pings: list of {"lat", "lon", "time"} for ONE trip (any order -- sorted here).
    gates: the route's gates IN ORDER -- the "gates" list from get_checkpoint_chain().

    Returns one result per gate, in route order:
        {"sequence": ..., "zone_id": ..., "crossing": <evidence dict> or None}
    None means the gate was not found -- never a guessed time.
    """
    if not isinstance(pings, (list, tuple)) or len(pings) < 2:
        raise GateCrossingError("A trip needs at least 2 pings to find gate crossings")
    if not isinstance(gates, (list, tuple)) or len(gates) == 0:
        raise GateCrossingError("gates must be a non-empty list, in route order")

    for index, ping in enumerate(pings):
        _check_ping(ping, f"ping {index}")

    ordered = sorted(pings, key=lambda ping: ping["time"])

    results = []
    search_from = 0
    last_time = None

    for gate in gates:
        found = None
        for i in range(search_from, len(ordered) - 1):
            crossing = find_gate_crossing(ordered[i], ordered[i + 1], gate)
            if crossing is None:
                continue
            if last_time is not None and crossing["time"] < last_time:
                continue
            found = crossing
            search_from = i
            last_time = crossing["time"]
            break

        results.append({
            "sequence": gate.get("sequence"),
            "zone_id": gate.get("zone_id"),
            "crossing": found,
        })

    return results





