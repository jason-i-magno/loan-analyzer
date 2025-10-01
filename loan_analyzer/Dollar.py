from decimal import ROUND_HALF_UP, Decimal


class Dollar:
    def __init__(self, amount: float):
        self.amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"${self.amount:,.2f}"

    def __repr__(self):
        return f"Dollar({self.amount})"

    def __add__(self, other):
        if isinstance(other, Dollar):
            return Dollar(self.amount + other.amount)
        return Dollar(self.amount + Decimal(other))

    def __sub__(self, other):
        if isinstance(other, Dollar):
            return Dollar(self.amount - other.amount)
        return Dollar(self.amount - Decimal(other))

    def __mul__(self, other):
        return Dollar(self.amount * Decimal(other))

    def __truediv__(self, other):
        return Dollar(self.amount / Decimal(other))

    def __eq__(self, other):
        self.check_is_dollar(other, "==")

        return self.amount == other.amount

    def __lt__(self, other):
        self.check_is_dollar(other, "<")

        return self.amount < other.amount

    def __le__(self, other):
        self.check_is_dollar(other, "<=")

        return self.amount <= other.amount

    def __gt__(self, other):
        self.check_is_dollar(other, ">")

        return self.amount > other.amount

    def __ge__(self, other):
        self.check_is_dollar(other, ">=")

        return self.amount >= other.amount

    def check_is_dollar(self, other, operation: str):
        if not isinstance(other, Dollar):
            raise TypeError(
                f"Unsupported operand type for {operation}: 'Dollar' and '{type(other).__name__}'"
            )
