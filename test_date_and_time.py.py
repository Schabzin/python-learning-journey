from datetime import datetime, date, timedelta

today = date.today()

print(today.strftime('%A, %d %B %Y'))
youth_day = datetime.strptime("16 June 2026", "%d %B %Y").date()
days_until = (youth_day - today).days
print(f"Youth Day is in {days_until} days")