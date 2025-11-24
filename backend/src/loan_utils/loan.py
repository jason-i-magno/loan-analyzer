from calendar import monthrange
from datetime import date
from decimal import Decimal

import pandas as pd

from loan_utils.calc import monthly_payment
from loan_utils.dollar import Dollar
from loan_utils.formatting import format_aggregated, format_schedule
from loan_utils.models import LoanTerms
from loan_utils.rate import Rate
from loan_utils.schedule import aggregate_schedule, build_payment_events, build_schedule


class Loan:
    """A class to represent a generic loan."""

    def __init__(
        self,
        annual_interest_percent: float,
        down_payment_percent: float,
        origination_date: date,
        purchase_price: float,
        term_years: int,
        monthly_extra_payment: float = 0.0,
        one_time_extras: dict[date, float] | None = None,
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

        self.origination_date: date = origination_date
        self.purchase_price: Dollar = Dollar(purchase_price)
        self.down_payment: Dollar = self.purchase_price.multiply_by(
            down_payment_percent / 100.0
        )
        self.loan_amount: Dollar = self.purchase_price - self.down_payment
        self.annual_interest_rate: float = annual_interest_percent / 100
        self.monthly_interest_rate: float = Rate(annual_interest_percent).per_period(12)
        self.term_months: int = term_years * 12
        self.monthly_payment: Dollar = self.calculate_monthly_payment()
        self.total_amount_payed: Dollar = Dollar(0)
        self.total_interest: Dollar = Dollar(0)

        self.monthly_extra_payment: Dollar = Dollar(monthly_extra_payment)
        self.one_time_extras: dict[date, float] = one_time_extras or {}

    @staticmethod
    def is_last_day_of_feb(day: date) -> bool:
        return day.month == 2 and day.day == monthrange(day.year, 2)[1]

    def amortization_schedule(self) -> pd.DataFrame:
        """Return schedule and aggregated DataFrames for API compatibility."""
        terms = LoanTerms(
            principal=self.loan_amount.amount,
            purchase_price=self.purchase_price.amount,
            annual_rate=Decimal(str(self.annual_interest_rate)),
            monthly_rate=Decimal(str(self.monthly_interest_rate)),
            term_months=self.term_months,
            origination_date=self.origination_date,
        )

        events = build_payment_events(
            origination_date=terms.origination_date,
            term_months=terms.term_months,
            monthly_payment=self.monthly_payment.amount,
            monthly_extra=self.monthly_extra_payment.amount,
            extras={d: Decimal(str(a)) for d, a in self.one_time_extras.items()},
        )

        rows, total_interest, total_paid = build_schedule(terms, events)
        aggregated_rows = aggregate_schedule(rows)

        schedule_df = pd.DataFrame(format_schedule(rows))
        aggregated_df = pd.DataFrame(format_aggregated(aggregated_rows))

        self.total_interest = Dollar(str(total_interest))
        self.total_amount_payed = Dollar(str(total_paid))

        return schedule_df, aggregated_df

    def calculate_monthly_payment(self) -> Dollar:
        payment: Decimal = monthly_payment(
            principal=self.loan_amount.amount,
            monthly_rate=Decimal(str(self.monthly_interest_rate)),
            term_months=self.term_months,
        )
        return Dollar(str(payment))
