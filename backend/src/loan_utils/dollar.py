from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


class Dollar:
    """A class to represent dollar amounts with precise arithmetic and formatting."""

    def __init__(self, amount: int | float | str | Dollar):
        if isinstance(amount, Dollar):
            # Copy constructor
            self.amount = amount.amount
        else:
            self.amount = self._to_decimal(amount)

    def __str__(self) -> str:
        # abs() also drops the sign from a negative zero (e.g. Dollar(-0.004))
        sign = "-" if self.amount < 0 else ""
        return f"{sign}${abs(self.amount):,.2f}"

    def __repr__(self) -> str:
        return f"Dollar({str(self.amount)})"

    # --------------------
    # Arithmetic Operators
    # --------------------
    def __add__(self, other):
        self._check_is_dollar(other, "+")

        return Dollar._from_decimal(self.amount + other.amount)

    def __iadd__(self, other):
        self._check_is_dollar(other, "+=")

        return Dollar._from_decimal(self.amount + other.amount)

    def __sub__(self, other):
        self._check_is_dollar(other, "-")

        return Dollar._from_decimal(self.amount - other.amount)

    def __isub__(self, other):
        self._check_is_dollar(other, "-=")

        return Dollar._from_decimal(self.amount - other.amount)

    def __mul__(self, other):
        self._check_is_dollar(other, "*")

        return Dollar._from_decimal(self.amount * other.amount)

    def __imul__(self, other):
        self._check_is_dollar(other, "*=")

        return Dollar._from_decimal(self.amount * other.amount)

    def __truediv__(self, other):
        self._check_is_dollar(other, "/")

        return Dollar._from_decimal(self.amount / other.amount)

    def __itruediv__(self, other):
        self._check_is_dollar(other, "/=")

        return Dollar._from_decimal(self.amount / other.amount)

    # --------------------
    # Comparison Operators
    # --------------------
    def __eq__(self, other):
        self._check_is_dollar(other, "==")

        return self.amount == other.amount

    def __hash__(self):
        return hash(self.amount)

    def __lt__(self, other):
        self._check_is_dollar(other, "<")

        return self.amount < other.amount

    def __le__(self, other):
        self._check_is_dollar(other, "<=")

        return self.amount <= other.amount

    def __gt__(self, other):
        self._check_is_dollar(other, ">")

        return self.amount > other.amount

    def __ge__(self, other):
        self._check_is_dollar(other, ">=")

        return self.amount >= other.amount

    # --------------------
    # Unary Operators
    # --------------------
    def __abs__(self):
        return Dollar._from_decimal(abs(self.amount))

    def __neg__(self):
        return Dollar._from_decimal(-self.amount)

    # --------------------
    # Internal helpers
    # --------------------
    @classmethod
    def _from_decimal(cls, amount: Decimal) -> Dollar:
        """Internal constructor for trusted Decimal values"""
        obj = cls.__new__(cls)
        obj.amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return obj

    @staticmethod
    def _check_is_dollar(other, operation: str):
        if not isinstance(other, Dollar):
            raise TypeError(
                f"Unsupported operand type for {operation}: 'Dollar' and '{type(other).__name__}'"
            )

    @staticmethod
    def _to_decimal(amount: int | float | str) -> Decimal:
        """Convert input safely into a Decimal rounded to cents"""
        if isinstance(amount, Decimal):
            raise TypeError(
                "To avoid floating point issues, Decimal input is not allowed. Use float, int, str, or Dollar instead."
            )
        try:
            value = Decimal(str(amount))
            if not value.is_finite():
                raise InvalidOperation
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError, TypeError):
            raise TypeError(f"Unsupported type for Dollar conversion: {amount!r}")

    # --------------------
    # Explicit methods for multiplication and division
    # --------------------
    def divide_by(self, divisor: int | float | Decimal) -> Dollar:
        """Divide this dollar amount by a divisor."""
        return Dollar._from_decimal(self.amount / Decimal(str(divisor)))

    def multiply_by(self, multiplier: int | float | Decimal) -> Dollar:
        """Multiply this dollar amount by a multiplier."""
        return Dollar._from_decimal(self.amount * Decimal(str(multiplier)))
