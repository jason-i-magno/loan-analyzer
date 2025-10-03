import matplotlib.pyplot as plt

from loan_utils.balance_tracker import BalanceTracker
from loan_utils.dollar import Dollar
from loan_utils.loan import Loan


class Mortgage(Loan):
    def __init__(
        self,
        annual_insurance_premium: float,
        closing_costs: float,
        down_payment_percentage: float,
        interest_rate_percentage: float,
        price: float,
        property_tax_rate_percentage: float,
        term_years: int,
    ):
        self.annual_insurance_premium: Dollar = Dollar(annual_insurance_premium)
        self.closing_costs: Dollar = Dollar(closing_costs)
        self.down_payment_percentage: float = down_payment_percentage
        self.interest_rate_percentage: float = interest_rate_percentage
        self.price: Dollar = Dollar(price)
        self.term_years: int = term_years
        self.property_tax_rate_percentage: float = property_tax_rate_percentage

        self.house_value: Dollar = self.price

    @property
    def down_payment(self) -> Dollar:
        return self.price.multiply_by_rate(self.down_payment_percentage / 100.0)

    @property
    def loan_amount(self) -> Dollar:
        return self.price - self.down_payment

    @property
    def term_length_months(self) -> int:
        return self.term_years * 12

    @property
    def yearly_property_tax(self) -> Dollar:
        return self.house_value.divide_by_rate(
            self.property_tax_rate_percentage / 100.0
        )

    @property
    def monthly_interest_rate(self) -> float:
        return self.interest_rate_percentage / 12.0 / 100.0

    @property
    def monthly_property_tax(self) -> Dollar:
        return self.yearly_property_tax.divide_by_rate(12.0)

    @property
    def monthly_insurance_payment(self) -> Dollar:
        return self.annual_insurance_premium.divide_by_rate(12.0)

    @property
    def monthly_escrow_payment(self) -> Dollar:
        return self.monthly_property_tax + self.monthly_insurance_payment

    @property
    def monthly_payment(self) -> Dollar:
        return self.calculate_monthly_payment(
            self.loan_amount,
            self.interest_rate_percentage / 100.0,
            self.term_length_months,
        )

    def __str__(self) -> str:
        return (
            f"House price: {self.price}\n"
            f"House value: {self.house_value}\n"
            f"Loan interest rate: {self.interest_rate_percentage}%\n"
            f"Term length: {self.term_years} years ({self.term_length_months} months)\n"
            f"Down payment percentage: {self.down_payment_percentage}%\n"
            f"Down payment: {self.down_payment}\n"
            f"Loan amount: {self.loan_amount}\n"
            f"Closing costs: {self.closing_costs}\n"
            f"Property tax rate: {self.property_tax_rate_percentage}%\n"
            f"Yearly property tax: {self.yearly_property_tax}\n"
            f"Monthly property tax: {self.monthly_property_tax}\n"
            f"Yearly insurance payment: {self.annual_insurance_premium}\n"
            f"Monthly insurance payment: {self.monthly_insurance_payment}\n"
            f"Monthly escrow payment: {self.monthly_escrow_payment}\n"
            f"Monthly payment: {self.monthly_payment}\n"
        )

    def mortgage_details(self) -> None:
        loan_balance_tracker: BalanceTracker = BalanceTracker(self.term_length_months)
        cumulative_loan_interest_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months
        )

        extra_payment: Dollar = Dollar(0)
        loan_balance: Dollar = self.loan_amount
        month_count: int = 0
        total_loan_interest: Dollar = Dollar(0)

        while loan_balance.amount > 0 and month_count < self.term_length_months:
            loan_interest: Dollar = loan_balance.multiply_by_rate(
                self.monthly_interest_rate
            )

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
