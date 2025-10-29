from loan_utils.dollar import Dollar


class BalanceTracker:
    def __init__(self, term_length_months: int):
        """Initializes the tracker with a list of Dollar objects."""
        self.balances: list[Dollar] = [Dollar(0.0) for _ in range(term_length_months)]

    def extract_values(self) -> list[float]:
        """Returns a list of numerical dollar values for graphing."""
        return [d.amount for d in self.balances]

    def get_balance(self, month: int) -> Dollar:
        """Returns the balance for a specific month."""
        if 0 <= month < len(self.balances):
            return self.balances[month]
        else:
            raise IndexError("Month index out of range.")

    def update_balance(self, month: int, amount: Dollar):
        """Updates the balance for a specific month."""
        if 0 <= month < len(self.balances):
            self.balances[month] = amount
        else:
            raise IndexError("Month index out of range.")
