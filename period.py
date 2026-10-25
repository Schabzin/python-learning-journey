import datetime

MAX_DAYS = 366

def _read_date(text):
    """Turn 'YYYY-MM-DD' text into a real date, or None if it isn't one."""
    try:
        return datetime.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_period(from_text, to_text, today):
    """Check the FROM/TO boxes. Returns (start, end, problem).
    Pass: problem is None. Refuse: start and end are None, problem = owner's message."""
    from_text = (from_text or "").strip()
    to_text = (to_text or "").strip()
    if from_text == "" or to_text == "":
        return None, None, "Please choose both a FROM date and a TO date."

    start = _read_date(from_text)
    end = _read_date(to_text)
    if start is None or end is None:
        return None, None, "That is not a real date. Use the calendar to pick one."

    if start > end:
        return None, None, "The FROM date must be on or before the TO date."

    if end > today:
        return None, None, "The TO date can't be after today."

    days = (end - start).days + 1
    if days > MAX_DAYS:
        return None, None, f"A statement can cover at most {MAX_DAYS} days. Choose a shorter period."

    return start, end, None
                       