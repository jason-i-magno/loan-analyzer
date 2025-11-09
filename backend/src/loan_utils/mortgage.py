from datetime import date

from loan_utils.dollar import Dollar
from loan_utils.loan import Loan


class Mortgage(Loan):
    def __init__(
        self,
        annual_interest_percent: float,
        closing_costs: float,
        down_payment_percent: float,
        origination_date: date,
        purchase_price: float,
        term_years: int,
        monthly_extra_payment: float = 0.0,
        one_time_extras: dict[date, float] | None = None,
    ):
        super().__init__(
            annual_interest_percent=annual_interest_percent,
            down_payment_percent=down_payment_percent,
            origination_date=origination_date,
            purchase_price=purchase_price,
            term_years=term_years,
            monthly_extra_payment=monthly_extra_payment,
            one_time_extras=one_time_extras,
        )
        self.closing_costs: Dollar = Dollar(closing_costs)
