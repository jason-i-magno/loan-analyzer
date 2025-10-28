class Calendar:
    def __init__(self, year: int):
        self.year: int = year
        self.months: dict[str, int] = {
            "January": 31,
            "February": 28 if year % 4 != 0 else 29,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31,
        }
