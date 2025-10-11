from decimal import Decimal

import pandas as pd

from loan_utils.dollar import Dollar
from loan_utils.rate import Rate


class Loan:
    """A class to represent a generic loan."""

    def __init__(
        self,
        annual_interest_percent: float,
        down_payment_percent: float,
        purchase_price: float,
        term_years: int,
    ):
        if down_payment_percent < 0.0 or down_payment_percent > 100.0:
            raise ValueError("Down payment percentage must be between 0 and 100.")
        if purchase_price <= 0:
            raise ValueError("Purchase price must be greater than 0.")
        if term_years <= 0:
            raise ValueError("Term years must be greater than 0.")

        self.down_payment: Dollar = Dollar(purchase_price).multiply_by(
            down_payment_percent / 100.0
        )
        self.loan_amount: Dollar = Dollar(purchase_price) - self.down_payment
        self.monthly_interest_rate: float = Rate(annual_interest_percent).per_period(12)
        self.term_months: int = term_years * 12
        self.monthly_payment: Dollar = self.calculate_monthly_payment()

    def amortization_schedule(self) -> None:
        schedule = pd.DataFrame(
            columns=[
                "Payment #",
                "Payment Date",
                "Payment Amount",
                "Principal Portion",
                "Interest Portion",
                "Total Interest",
                "Ending Balance",
                "Resulting LTV%",
            ]
        )

        balance: Dollar = self.loan_amount
        total_interest: Dollar = Dollar(0)

        for month in range(1, self.term_months + 1):
            interest: Dollar = balance.multiply_by(self.monthly_interest_rate)
            principal: Dollar = self.monthly_payment - interest
            balance -= principal
            total_interest += interest

            if balance.amount < 0:
                principal += balance
                self.monthly_payment = principal + interest
                balance = Dollar(0)

            schedule = pd.concat(
                [
                    schedule,
                    pd.DataFrame(
                        {
                            "Payment #": [month],
                            "Payment Date": [month],
                            "Payment Amount": [str(self.monthly_payment)],
                            "Principal Portion": [str(principal)],
                            "Interest Portion": [str(interest)],
                            "Total Interest": [str(total_interest)],
                            "Ending Balance": [str(balance)],
                            "Resulting LTV%": [
                                f"{(balance.amount / self.home_value.amount) * 100:.3f}%"
                            ],
                        }
                    ),
                ],
                ignore_index=True,
            )

            if balance.amount <= 0:
                break

        print(schedule)

    def calculate_monthly_payment(self) -> Dollar:
        if self.monthly_interest_rate == 0.0:
            return self.loan_amount.divide_by(self.term_months)

        interest_rate: Decimal = Decimal(str(self.monthly_interest_rate))

        return self.loan_amount.multiply_by(
            interest_rate
            / (Decimal(1) - (Decimal(1) + interest_rate) ** -self.term_months)
        )
