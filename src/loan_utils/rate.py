class Rate:
    def __init__(self, value: float, is_percent: bool = True):
        self._fraction = value / 100 if is_percent else value

    @property
    def as_fraction(self) -> float:
        return self._fraction

    @property
    def as_percent(self) -> float:
        return self._fraction * 100

    def per_period(self, periods_per_year: int) -> float:
        """Return per-period rate (e.g. monthly interest, quarterly tax)."""
        return self._fraction / periods_per_year
