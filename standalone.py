import datetime

ANCHOR_DATE = datetime.date(2026, 7, 25)
ANCHOR_LETTER ="B"

def get_weekend_letter(check_date):
    days_since_anchor = (check_date - ANCHOR_DATE).days
    weeks_since_anchor = days_since_anchor // 7
    if weeks_since_anchor % 2 == 0:
        return ANCHOR_LETTER
    return "A" if ANCHOR_LETTER == "B" else "B"

print(get_weekend_letter(datetime.date(2026, 7, 25)))
print(get_weekend_letter(datetime.date(2026, 8, 1)))
print(get_weekend_letter(datetime.date(2026, 8, 8)))
print(get_weekend_letter(datetime.date(2026, 7, 18)))