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
        monthly_extra_payment: float = 0.0,
        one_time_extras: dict[int, float] | None = None,
    ):
        """
        Args:
            annual_interest_percent: Annual interest rate as a percentage (e.g. 6.5)
            down_payment_percent: Down payment percentage (0-100)
            purchase_price: Total property price
            term_years: Term in years
            monthly_extra_payment: Extra amount added to every monthly payment (default 0)
            one_time_extras: Dict of {month_number: extra_payment_amount}
        """
        if down_payment_percent < 0.0 or down_payment_percent > 100.0:
            raise ValueError("Down payment percentage must be between 0 and 100.")
        if purchase_price <= 0:
            raise ValueError("Purchase price must be greater than 0.")
        if term_years <= 0:
            raise ValueError("Term years must be greater than 0.")

        self.purchase_price: Dollar = Dollar(purchase_price)
        self.down_payment: Dollar = self.purchase_price.multiply_by(
            down_payment_percent / 100.0
        )
        self.loan_amount: Dollar = self.purchase_price - self.down_payment
        self.monthly_interest_rate: float = Rate(annual_interest_percent).per_period(12)
        self.term_months: int = term_years * 12
        self.monthly_payment: Dollar = self.calculate_monthly_payment()
        self.total_amount_payed: Dollar = self.monthly_payment.multiply_by(
            self.term_months
        )
        self.total_interest: Dollar = self.total_amount_payed - self.loan_amount

        self.monthly_extra_payment: Dollar = Dollar(monthly_extra_payment)
        self.one_time_extras: dict[int, float] = one_time_extras or {}

    def amortization_schedule(self) -> pd.DataFrame:
        schedule = pd.DataFrame(
            columns=[
                "payment_id",
                "payment_date",
                "payment_amount",
                "principal_portion",
                "interest_portion",
                "extra_payment",
                "total_interest",
                "ending_balance",
                "resulting_ltv",
            ]
        )

        balance: Dollar = self.loan_amount
        total_interest: Dollar = Dollar(0)
        month: int = 1

        while balance.amount > 0 and month <= self.term_months:
            interest: Dollar = balance.multiply_by(self.monthly_interest_rate)
            principal: Dollar = self.monthly_payment - interest
            extra_payment: Dollar = self.monthly_extra_payment

            # Apply one-time extra if defined
            if month in self.one_time_extras:
                extra_payment += Dollar(self.one_time_extras[month])

            # Prevent overpaying beyond remaining balance
            if principal + extra_payment > balance:
                extra_payment = (
                    balance - principal if principal > balance else Dollar(0)
                )

            balance -= principal + extra_payment
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
                            "payment_id": [month],
                            "payment_date": [month],
                            "payment_amount": [str(self.monthly_payment)],
                            "principal_portion": [str(principal)],
                            "interest_portion": [str(interest)],
                            "extra_payment": [str(extra_payment)],
                            "total_interest": [str(total_interest)],
                            "ending_balance": [str(balance)],
                            "resulting_ltv": [
                                f"{(balance.amount / self.purchase_price.amount) * 100:.3f}%"
                            ],
                        }
                    ),
                ],
                ignore_index=True,
            )

            if balance.amount <= 0:
                break
            month += 1

        return schedule

    def calculate_monthly_payment(self) -> Dollar:
        if self.monthly_interest_rate == 0.0:
            return self.loan_amount.divide_by(self.term_months)

        interest_rate: Decimal = Decimal(str(self.monthly_interest_rate))

        return self.loan_amount.multiply_by(
            interest_rate
            / (Decimal(1) - (Decimal(1) + interest_rate) ** -self.term_months)
        )
