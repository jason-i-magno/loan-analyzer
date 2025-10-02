from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


class Dollar:
    def __init__(self, amount: int | float | str | Dollar):
        if isinstance(amount, Dollar):
            # Copy constructor
            self.amount = amount.amount
        else:
            self.amount = self._to_decimal(amount)

    def __str__(self) -> str:
        return f"${self.amount:,.2f}" if self.amount >= 0 else f"-${-self.amount:,.2f}"

    def __repr__(self) -> str:
        return f"Dollar({str(self.amount)})"

    # --------------------
    # Arithmetic Operators
    # --------------------
    def __add__(self, other):
        return Dollar._from_decimal(self.amount + self._to_decimal(other))

    def __iadd__(self, other):
        self.amount = (self.amount + self._to_decimal(other)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return self

    def __radd__(self, other):
        return Dollar._from_decimal(self._to_decimal(other) + self.amount)

    def __sub__(self, other):
        return Dollar._from_decimal(self.amount - self._to_decimal(other))

    def __isub__(self, other):
        self.amount = (self.amount - self._to_decimal(other)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return self

    def __rsub__(self, other):
        return Dollar._from_decimal(self._to_decimal(other) - self.amount)

    def __mul__(self, other):
        return Dollar._from_decimal(self.amount * self._to_decimal(other))

    def __imul__(self, other):
        self.amount = (self.amount * self._to_decimal(other)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return self

    def __rmul__(self, other):
        return Dollar._from_decimal(self._to_decimal(other) * self.amount)

    def __truediv__(self, other):
        return Dollar._from_decimal(self.amount / self._to_decimal(other))

    def __itruediv__(self, other):
        self.amount = (self.amount / self._to_decimal(other)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return self

    def __rtruediv__(self, other):
        return Dollar._from_decimal(self._to_decimal(other) / self.amount)

    # --------------------
    # Comparison Operators
    # --------------------
    def __eq__(self, other):
        return self.amount == self._to_decimal(other)

    def __lt__(self, other):
        return self.amount < self._to_decimal(other)

    def __le__(self, other):
        return self.amount <= self._to_decimal(other)

    def __gt__(self, other):
        return self.amount > self._to_decimal(other)

    def __ge__(self, other):
        return self.amount >= self._to_decimal(other)

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
    def _to_decimal(amount: int | float | str | Dollar) -> Decimal:
        """Convert input safely into a Decimal rounded to cents"""
        if isinstance(amount, Dollar):
            return amount.amount
        if isinstance(amount, Decimal):
            raise TypeError(
                "To avoid floating point issues, Decimal input is not allowed. Use float, int, str, or Dollar instead."
            )
        try:
            return Decimal(str(amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError, TypeError):
            raise TypeError(f"Unsupported type for Dollar conversion: {amount!r}")
