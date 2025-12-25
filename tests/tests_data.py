from datetime import date, timedelta
# Four weeks worth of Test data for habit completions
BASE_DATE = date(2025, 1, 1)

DAILY_4_WEEKS = [
    BASE_DATE + timedelta(days=i) for i in range(28)
]

WEEKLY_4_WEEKS = [
    BASE_DATE + timedelta(days=7*i) for i in range(4)
]

MONTHLY_4_PERIODS = [
    date(2025, 1, 1),
    date(2025, 2, 1),
    date(2025, 3, 1),
    date(2025, 4, 1),
]
