"""
test_segment_attribution.py -- proves the money rules of segment attribution.
Pure functions: no database needed, so no fixture -- just the simulated trip.
"""

import pytest

from gate_crossing import find_gate_crossing, find_gate_times
from segment_attribution import SegmentAttributionError, attribute_boardings
from trip_simulation import FULL_FARE, at, build_trip

def run(pings, gates, events):
    """Helper: the full pipeline in one call."""
    return attribute_boardings(events, find_gate_times(pings, gates), gates, FULL_FARE)

def test_full_trip_matches_the_hand_worked_answer():
    report = run(*build_trip())
    assert report["expected_revenue"] == 444
    assert report["needs_review"] == 1

def test_path_beside_a_gate_is_not_a_crossing():
    pings, gates, _ = build_trip()
    moved = [dict(p, lon=27.832) for p in pings]
    assert find_gate_crossing(moved[1], moved[2], gates[0]) is None

def test_alightings_never_change_the_money():
    pings, gates, events = build_trip()
    only_boardings = [e for e in events if e["direction"] == "IN"]
    assert run(pings, gates, only_boardings)["expected_revenue"] == run(pings, gates, events)["expected_revenue"]

def test_missing_gate_sends_uncertain_boardings_to_review():
    pings, gates, events = build_trip()
    gates[1] = dict(gates[1], center_lon=27.835)
    report = run(pings, gates, events)
    assert report["expected_revenue"] == 15 * 24
    reasons = [b["reason"] for b in report["boardings"] if b["status"] == "needs_review"]
    assert any("gate 2 was not detected" in r for r in reasons)

def test_missing_gate_is_inferred_when_a_later_gate_was_passed():
    pings, gates, _ = build_trip()
    gates[1] = dict(gates[1], center_lon=27.835)
    late_boarding = [{"time": at(2.9), "direction": "IN"}]
    report = run(pings, gates, late_boarding)
    assert report["boardings"][0]["segment"] == 3
    assert report["boardings"][0]["status"] == "needs_review"

@pytest.mark.parametrize("bad_fare", [0, -24, True, float("inf")])
def test_rejects_invalid_full_fare(bad_fare):
    pings, gates, events = build_trip()
    with pytest.raises(SegmentAttributionError, match="full_fare"):
        attribute_boardings(events, find_gate_times(pings, gates), gates, bad_fare)