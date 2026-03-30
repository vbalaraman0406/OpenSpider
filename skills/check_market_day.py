import datetime

def is_market_working_day():
    today = datetime.date.today()
    
    # Check for weekends
    if today.weekday() >= 5:  # Saturday (5) or Sunday (6)
        return False

    # US Market Holidays for 2024 (observed dates)
    holidays_2024 = [
        datetime.date(2024, 1, 1),   # New Year's Day
        datetime.date(2024, 1, 15),  # Martin Luther King, Jr. Day
        datetime.date(2024, 2, 19),  # Washington's Birthday
        datetime.date(2024, 3, 29),  # Good Friday
        datetime.date(2024, 5, 27),  # Memorial Day
        datetime.date(2024, 6, 19),  # Juneteenth National Independence Day
        datetime.date(2024, 7, 4),   # Independence Day
        datetime.date(2024, 9, 2),   # Labor Day
        datetime.date(2024, 11, 28), # Thanksgiving Day
        datetime.date(2024, 12, 25)  # Christmas Day
    ]

    if today in holidays_2024:
        return False

    return True

if __name__ == '__main__':
    if is_market_working_day():
        print("True")
    else:
        print("False")