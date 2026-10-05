"""
segment_attribution.py -- places each camera boarding into the segment of
the route where it happened, and prices it with the owner's fares.

Only boardings (IN) affect revenue: once aboard, a passenger owes the fare
for where they BOARDED, wherever they get off.
Anything the system cannot be sure of is marked needs_review -- never guessed.
"""

import math
from datetime import datetime

class SegmentAttributionError(ValueError):
    """Raised when the input is invalid."""

def _gates_passed(event_time, gate_results):
    """
    How many gates had the taxi passed at event_time?
    Returns (count, uncertain_reason). uncertain_reason is None when sure.
    """
    passed = 0
    for k, result in enumerate(gate_results):
        crossing = result["crossing"]

        if crossing is None:
            later_passed = any(
                r["crossing"] is not None and r["crossing"]["time"] <= event_time
                for r in gate_results[k + 1:]
            )
            if later_passed:
                passed = k + 1
                continue
            return passed, f"gate {result['sequence']} was not detected -- can't tell which side of it this boarding was"

        if crossing["time"] <= event_time:
            passed = k + 1
        else:
            break

    return passed, None

def attribute_boardings(events, gate_results, gates, full_fare):
    """
    events:       camera door events [{"time": datetime, "direction": "IN" or "OUT"}, ...]
    gate_results: output of find_gate_times() -- one per gate, in route order
    gates:        the route's gates in order (get_checkpoint_chain()["gates])
    full_fare:    the route's full fare (get_checkpoint_chain()["full_fare"])

    Returns {"boardings": [...], "expected_revenue": ..., "needs_review": ...}
    """
    if isinstance(full_fare, bool) or not isinstance(full_fare, (int, float)) \
            or not math.isfinite(full_fare) or full_fare <= 0:
        raise SegmentAttributionError(f"full_fare must be a number above 0, got {full_fare!r}")
    if len(gate_results) != len(gates):
        raise SegmentAttributionError("gate_results and gates must describe the same gates")
    for result, gate in zip(gate_results, gates):
        if result.get("sequence") != gate.get("sequence"):
            raise SegmentAttributionError("gate_results and gates are not in the same order")

    boardings = []
    for index, event in enumerate(events):
        if not isinstance(event, dict) or not isinstance(event.get("time"), datetime):
            raise SegmentAttributionError(f"event {index} needs a datetime 'time'")
        if event.get("direction") not in ("IN", "OUT"):
            raise SegmentAttributionError(f"event {index} direction must be 'IN' or 'OUT'")
        if event["direction"] == "OUT":
            continue

        passed, uncertain = _gates_passed(event["time"], gate_results)

        if uncertain:
            boardings.append({"time": event["time"], "segment": None, "fare": None,
                              "status": "needs_review", "reason": uncertain})
            continue

        fare = full_fare if passed == 0 else gates[passed - 1]["boarding_fare"]
        if fare is None:
            boardings.append({"time": event["time"], "segment": passed, "fare": None,
                              "status": "needs_review",
                              "reason": f"boarding after gate {passed}, where no boarding is expected"})
            continue

        boardings.append({"time": event["time"], "segment": passed, "fare": fare,
                          "status": "priced", "reason": None})

    priced = [b["fare"] for b in boardings if b["status"] == "priced"]
    return {
        "boardings": boardings,
        "expected_revenue": sum(priced),
        "needs_review": sum(1 for b in boardings if b["status"] == "needs_review"),
    }