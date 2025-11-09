from calendar import monthrange
from datetime import date
from decimal import Decimal

import pandas as pd
from dateutil.relativedelta import relativedelta

from loan_utils.dollar import Dollar
from loan_utils.rate import Rate


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
        schedule = pd.DataFrame(
            columns=[
                "payment_id",
                "due_date",
                "payment_date",
                "description",
                "payment_amount",
                "principal_portion",
                "interest_portion",
                "total_interest",
                "ending_balance",
                "resulting_ltv",
            ]
        )

        balance: Dollar = self.loan_amount
        self.total_interest: Dollar = Dollar(0)

        # Build all events (scheduled + extras)
        events = []
        due_date: date = (self.origination_date + relativedelta(months=+2)).replace(
            day=1
        )
        payment_date: date = due_date
        for _ in range(self.term_months):
            if self.monthly_extra_payment > Dollar(0):
                events.append(
                    (
                        "curtailment",
                        payment_date + relativedelta(days=-1),
                        self.monthly_extra_payment,
                    )
                )
            events.append(("scheduled", payment_date, self.monthly_payment))
            payment_date += relativedelta(months=+1)

        for payment_date, amount in self.one_time_extras.items():
            events.append(("curtailment", payment_date, Dollar(amount)))

        events.sort(key=lambda e: e[1])  # sort by date

        payment_id: int = 0

        for event_type, current_date, amount in events:
            if balance.amount <= 0:
                break

            payment_id += 1

            # --- apply payment ---
            if event_type == "scheduled":
                interest = balance.multiply_by(self.monthly_interest_rate)
                principal = amount - interest
                balance -= principal
                self.total_interest += interest
                description = "Scheduled"
            else:  # one-time extra payment
                principal = amount
                interest = Dollar(0)
                balance -= amount
                description = "Curtailment"

            self.total_amount_payed += amount

            if balance.amount < 0:
                balance = Dollar(0)

            schedule = pd.concat(
                [
                    schedule,
                    pd.DataFrame(
                        {
                            "payment_id": [payment_id],
                            "due_date": [due_date.isoformat()],
                            "payment_date": [current_date.isoformat()],
                            "description": [description],
                            "payment_amount": [str(amount)],
                            "principal_portion": [principal],
                            "interest_portion": [interest],
                            "total_interest": [str(self.total_interest)],
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

            if event_type == "scheduled":
                due_date += relativedelta(months=+1)

        # Group by due_date and sum principal + interest for plotting convenience
        aggregated = (
            schedule.groupby("due_date", as_index=False)
            .agg(
                {
                    "principal_portion": lambda x: sum(v.amount for v in x),
                    "interest_portion": lambda x: sum(v.amount for v in x),
                }
            )
            .sort_values("due_date")
        )

        # Convert numeric columns back to strings for JSON serialization
        schedule["principal_portion"] = schedule["principal_portion"].map(
            lambda v: str(v)
        )
        schedule["interest_portion"] = schedule["interest_portion"].map(
            lambda v: str(v)
        )

        return schedule, aggregated

    def calculate_monthly_payment(self) -> Dollar:
        if self.monthly_interest_rate == 0.0:
            return self.loan_amount.divide_by(self.term_months)

        interest_rate: Decimal = Decimal(str(self.monthly_interest_rate))

        return self.loan_amount.multiply_by(
            interest_rate
            / (Decimal(1) - (Decimal(1) + interest_rate) ** -self.term_months)
        )
