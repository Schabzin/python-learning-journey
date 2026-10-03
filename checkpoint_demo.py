"""
checkpoint_demo.py

Why a headcount at each gate is NOT proof of who boarded.
Pure Python, no database: two different days on the same route that
produce IDENTICAL gate headcounts but DIFFERENT numbers of boardings.
"""

# The gates in route order. Each event below is labelled with the gate the
# taxi passes NEXT after that event -- i.e. the segment the event belongs to.
#   "TK Global (origin)"  -> boarded at the origin, before gate 1
#   "After Deboniar Park" -> happened at Deboniar Park, before gate 2
#   "M61"                 -> happened at Scelo, before gate 3
GATES = ["TK Global (origin)", "After Deboniar Park", "M61"]


def build_events(boardings_at_origin, swaps_per_stop):
    """
    Builds the list of door events for one trip.

    boardings_at_origin: how many people board before the first gate.
    swaps_per_stop: {gate_name: n} -- at the informal stop before that gate,
                    n people get OFF and n DIFFERENT people get ON.

    Returns a list of (gate_name, direction) tuples, in the order they happened.
    """
    if boardings_at_origin < 0:
        raise ValueError("boardings_at_origin cannot be negative")

    events = [(GATES[0], "IN")] * boardings_at_origin

    for gate in GATES[1:]:
        n = swaps_per_stop.get(gate, 0)
        if n < 0:
            raise ValueError(f"Swap count for {gate!r} cannot be negative")
        events += [(gate, "OUT")] * n      # people getting off at this stop
        events += [(gate, "IN")] * n       # different people getting on

    return events


def headcount_at_each_gate(events):
    """
    What a 'count at the gate' system sees: how many people are on board
    at the moment the taxi passes each gate.
    """
    on_board = 0
    headcounts = {}

    for gate in GATES:
        for event_gate, direction in events:
            if event_gate != gate:
                continue
            if direction == "IN":
                on_board += 1
            elif direction == "OUT":
                on_board -= 1
            else:
                raise ValueError(f"Unknown direction {direction!r}")
        headcounts[gate] = on_board

    return headcounts


def events_per_segment(events):
    """
    What an event ledger sees: every IN and every OUT, grouped by the
    segment it happened in.
    """
    ledger = {gate: {"IN": 0, "OUT": 0} for gate in GATES}

    for event_gate, direction in events:
        if event_gate not in ledger:
            raise ValueError(f"Event belongs to unknown gate {event_gate!r}")
        if direction not in ("IN", "OUT"):
            raise ValueError(f"Unknown direction {direction!r}")
        ledger[event_gate][direction] += 1

    return ledger


if __name__ == "__main__":
    day_a = build_events(15, {})
    day_b = build_events(15, {"After Deboniar Park": 3, "M61": 2})

    for label, events in (
        ("Day A -- nobody gets off or on mid-route", day_a),
        ("Day B -- swaps at Deboniar Park and Scelo", day_b),
    ):
        ledger = events_per_segment(events)
        total_boardings = sum(segment["IN"] for segment in ledger.values())

        print(f"\n{label}")
        print("  Headcount at gates :", headcount_at_each_gate(events))
        print("  Ledger per segment :", ledger)
        print("  Total boardings    :", total_boardings)