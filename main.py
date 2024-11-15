from datetime import date, datetime, timedelta

def calculate_easter(year: int) -> date:
    """Calculate the date of Easter Sunday for a given year."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_holidays(year: int) -> dict:
    """Get the holidays for a specific year, including dynamic Easter dates."""
    easter_sunday = calculate_easter(year)
    easter_monday = easter_sunday + timedelta(days=1)
    corpus_christi = easter_sunday + timedelta(days=60)

    return {
        "Nowy Rok": f"{year}-01-01",  # New Year's Day
        "Święto Trzech Króli": f"{year}-01-06",  # Epiphany
        "Wielkanoc": [easter_sunday.isoformat(), easter_monday.isoformat()],  # Easter Sunday and Monday
        "Święto Pracy": f"{year}-05-01",  # Labor Day
        "Święto Konstytucji 3 Maja": f"{year}-05-03",  # Constitution Day
        "Boże Ciało": corpus_christi.isoformat(),  # Corpus Christi
        "Wniebowzięcie Najświętszej Maryi Panny": f"{year}-08-15",  # Assumption of Mary
        "Wszystkich Świętych": f"{year}-11-01",  # All Saints' Day
        "Święto Niepodległości": f"{year}-11-11",  # Independence Day
        "Boże Narodzenie": [f"{year}-12-25", f"{year}-12-26"],  # Christmas Day and Second Day
    }


# Example usage:
if __name__ == "__main__":
    year = 2025
    holidays = get_holidays(year)

    print(f"Holidays for {year}:")
    for holiday, dates in holidays.items():
        if isinstance(dates, list):
            print(f"{holiday}: {', '.join(dates)}")
        else:
            print(f"{holiday}: {dates}")
