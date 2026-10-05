"""
trip_simulation.py -- runs one simulated trip through the whole pipeline:
GPS pings -> gate times -> boardings priced by segment.
Test-only coordinates; the expected answer is worked out by hand first.
"""

from datetime import datetime, timedelta

from gate_crossing import find_gate_times
from segment_attribution import attribute_boardings

START = datetime(2026, 10, 5, 7, 0, 0)
FULL_FARE = 24

def at(minutes):
    """A time `minutes` after the trip start."""
    return START + timedelta(minutes=minutes)

def build_trip():
    pings = [{"lat": -26.70 + i * 0.0045, "lon": 27.83, "time": START + timedelta(seconds=30 * i)}
             for i in range(10)]

    gates = [
        {"sequence": 1, "zone_id": 11, "name": "After R54",       "center_lat": -26.70 + 0.0068, "center_lon": 27.83, "radius_meters": 80, "boarding_fare": 18},
        {"sequence": 2, "zone_id": 12, "name": "After Boipatong", "center_lat": -26.70 + 0.0158, "center_lon": 27.83, "radius_meters": 80, "boarding_fare": 15},
        {"sequence": 3, "zone_id": 13, "name": "After Licence",   "center_lat": -26.70 + 0.0248, "center_lon": 27.83, "radius_meters": 80, "boarding_fare": None},
    ]

    events = []
    events += [{"time": at(0.1), "direction": "IN"}] * 15
    events += [{"time": at(1.2), "direction": "OUT"}] * 3
    events += [{"time": at(1.25), "direction": "IN"}] * 3
    events += [{"time": at(2.2), "direction": "OUT"}] * 2
    events += [{"time": at(2.25), "direction": "IN"}] * 2
    events += [{"time": at(3.5), "direction": "IN"}] * 1
    return pings, gates, events

if __name__ == "__main__":
    pings, gates, events = build_trip()

    gate_results = find_gate_times(pings, gates)
    print("Gates times:")
    for gate, result in zip(gates, gate_results):
        when = result["crossing"]["time"].strftime("%H:%M:%S") if result["crossing"] else "NOT DETECTED"
        print(f"  {result['sequence']}. {gate['name']:<16} {when}")

    report = attribute_boardings(events, gate_results, gates, FULL_FARE)

    print("\nBoardings:")
    counts = {}
    for b in report["boardings"]:
        if b["status"] == "priced":
            label = f"segment {b['segment']} at R{b['fare']}"
        else:
            label = "needs review"
        counts[label] = counts.get(label, 0) + 1
    for label, count in counts.items():
        print(f"  {count:>2} x {label}")

    print(f"\nExpected revenue: R{report['expected_revenue']}")
    print(f"Needs review:     {report['needs_review']}")
    for b in report["boardings"]:
        if b["status"] == "needs_review":
            print(f"  - {b['time'].strftime('%H:%M:%S')}: {b['reason']}")