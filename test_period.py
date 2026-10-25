import datetime
from period import parse_period

TODAY = datetime.date(2026, 10, 25)

def test_good_period():
    start, end, problem = parse_period("2026-01-01", "2026-09-30", TODAY)
    assert start == datetime.date(2026, 1, 1)
    assert end == datetime.date(2026, 9, 30)
    assert problem is None

def test_one_day_is_allowed():
    start, end, problem = parse_period("2026-10-25", "2026-10-25", TODAY)
    assert problem is None
    assert start == end

def test_missing_box_is_refused():
    for f, t in [("", "2026-10-01"), ("2026-10-01", None), ("  ", "2026-10-01")]:
        start, end, problem = parse_period(f, t, TODAY)
        assert start is None
        assert problem == "Please choose both a FROM date and a TO date."

def test_not_a_date_is_refused():
    for bad in ["hello", "31-02-2026", "2026-02-31"]:
        start, end, problem = parse_period(bad, "2026-10-01", TODAY)
        assert start is None
        assert "not a real date" in problem

def test_backwards_is_refused():
    start, end, problem = parse_period("2026-10-10", "2026-10-01", TODAY)
    assert start is None
    assert "on or before" in problem

def test_today_allowed_tomorrow_refused():
    assert parse_period("2026-10-01", "2026-10-25", TODAY)[2]is None
    assert "after today" in parse_period("2026-10-01", "2026-10-26", TODAY)[2]

def test_366_days_allowed_367_refused():
    assert parse_period("2025-10-25", "2026-10-25", TODAY)[2] is None
    assert "366 days" in parse_period("2025-10-24", "2026-10-25", TODAY)[2]
