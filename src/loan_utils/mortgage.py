import matplotlib.pyplot as plt

from loan_utils.balance_tracker import BalanceTracker
from loan_utils.dollar import Dollar
from loan_utils.loan import Loan


class Mortgage(Loan):
    def __init__(
        self,
        annual_interest_percent: float,
        closing_costs: float,
        down_payment_percent: float,
        purchase_price: float,
        term_years: int,
    ):
        super().__init__(
            annual_interest_percent=annual_interest_percent,
            down_payment_percent=down_payment_percent,
            purchase_price=purchase_price,
            term_years=term_years,
        )
        self.closing_costs: Dollar = Dollar(closing_costs)
        self.home_value: Dollar = Dollar(purchase_price)

        print(self.monthly_payment)

    def mortgage_details(self) -> None:
        loan_balance_tracker: BalanceTracker = BalanceTracker(self.term_months)
        cumulative_loan_interest_tracker: BalanceTracker = BalanceTracker(
            self.term_months
        )

        extra_payment: Dollar = Dollar(0)
        loan_balance: Dollar = self.loan_amount
        month_count: int = 0
        total_loan_interest: Dollar = Dollar(0)

        while loan_balance.amount > 0 and month_count < self.term_months:
            loan_interest: Dollar = loan_balance.multiply_by(self.monthly_interest_rate)

            principle_payment = self.monthly_payment - loan_interest
            loan_balance = loan_balance - principle_payment - extra_payment
            total_loan_interest += loan_interest

            loan_balance_tracker.update_balance(month_count, loan_balance)
            cumulative_loan_interest_tracker.update_balance(
                month_count, total_loan_interest
            )

            month_count += 1
        plt.figure()
        plt.plot(loan_balance_tracker.extract_values(), label="Loan balance")
        plt.plot(
            cumulative_loan_interest_tracker.extract_values(),
            label="Total interest paid",
        )
        plt.legend()
