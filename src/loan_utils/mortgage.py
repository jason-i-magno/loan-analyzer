import matplotlib.pyplot as plt

from loan_utils.balance_tracker import BalanceTracker
from loan_utils.calendar import Calendar
from loan_utils.dollar import Dollar
from loan_utils.loan import Loan


class Mortgage(Loan):
    real_estate_ror: float = 0.043

    def __init__(
        self,
        price: float,
        interest_rate_percentage: float,
        term_years: int,
        down_payment_percentage: float,
        property_tax_rate_percentage: float,
        annual_insurance_premium: float,
        closing_costs: float,
    ):
        self.price: Dollar = Dollar(price)
        self.house_value: Dollar = self.price
        self.interest_rate_percentage: float = interest_rate_percentage
        self.term_years: int = term_years
        self.down_payment_percentage: float = down_payment_percentage
        self.property_tax_rate_percentage: float = property_tax_rate_percentage
        self.annual_insurance_premium: Dollar = Dollar(annual_insurance_premium)
        self.closing_costs: Dollar = Dollar(closing_costs)

    @property
    def down_payment(self) -> Dollar:
        return self.price * self.down_payment_percentage / 100.0

    @property
    def loan_amount(self) -> Dollar:
        return self.price - self.down_payment

    @property
    def term_length_months(self) -> int:
        return self.term_years * 12

    @property
    def yearly_property_tax(self) -> Dollar:
        return self.house_value * self.property_tax_rate_percentage / 100.0

    @property
    def monthly_interest_rate(self) -> float:
        return self.interest_rate_percentage / 12.0 / 100.0

    @property
    def monthly_property_tax(self) -> Dollar:
        return self.yearly_property_tax / 12.0

    @property
    def monthly_insurance_payment(self) -> Dollar:
        return self.annual_insurance_premium / 12.0

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
            f"Loan interest rate: {self.interest_rate_percentage:.2%}\n"
            f"Term length: {self.term_years} years ({self.term_length_months} months)\n"
            f"Down payment percentage: {self.down_payment_percentage:.2%}\n"
            f"Down payment: {self.down_payment}\n"
            f"Loan amount: {self.loan_amount}\n"
            f"Closing costs: {self.closing_costs}\n"
            f"Property tax rate: {self.property_tax_rate_percentage:.3%}\n"
            f"Yearly property tax: {self.yearly_property_tax}\n"
            f"Monthly property tax: {self.monthly_property_tax}\n"
            f"Yearly insurance payment: {self.annual_insurance_premium}\n"
            f"Monthly insurance payment: {self.monthly_insurance_payment}\n"
            f"Monthly escrow payment: {self.monthly_escrow_payment}\n"
            f"Monthly payment: {self.monthly_payment}\n"
        )

    def mortgage_details(self, figure_num: int) -> None:
        loan_balance_tracker: BalanceTracker = BalanceTracker(self.term_length_months)
        cumulative_loan_interest_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months
        )
        monthly_interest_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months
        )
        cumulative_non_equity_payment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months + 1
        )
        non_equity_payment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months
        )
        real_estate_investment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months + 1
        )
        real_estate_investment_tracker.update_balance(0, self.down_payment)
        tax_benefit_investment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months + 1
        )
        hybrid_investment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months + 1
        )
        hybrid_investment_tracker.update_balance(0, self.down_payment)
        sp500_investment_tracker: BalanceTracker = BalanceTracker(
            self.term_length_months + 1
        )
        sp500_investment_tracker.update_balance(
            0, self.down_payment + self.closing_costs
        )

        loan_balance: Dollar = self.loan_amount
        total_loan_interest: Dollar = Dollar(0)
        month_count: int = 0
        tax_benefit_totol: Dollar = Dollar(0)
        extra_payment: Dollar = Dollar(0)

        current_year: int = 2025

        for _ in range(self.term_years):
            current_year += 1
            itemized_deduction: Dollar = Dollar(0.0)
            calendar: dict[str, int] = Calendar(year=current_year)

            for _, _ in calendar.months.items():
                loan_interest: Dollar = loan_balance * self.monthly_interest_rate
                itemized_deduction += loan_interest

                monthly_interest_tracker.update_balance(month_count, loan_interest)

                non_equity_payment_tracker.update_balance(month_count, loan_interest)

                principle_payment = self.monthly_payment - loan_interest
                loan_balance = loan_balance - principle_payment - extra_payment

                total_loan_interest += loan_interest

                loan_balance_tracker.update_balance(month_count, loan_balance)
                cumulative_loan_interest_tracker.update_balance(
                    month_count, total_loan_interest
                )
                cumulative_non_equity_payment_tracker.update_balance(
                    month_count + 1,
                    cumulative_non_equity_payment_tracker.get_balance(month_count)
                    + loan_interest,
                )

                real_estate_investment_tracker.update_balance(
                    month_count + 1,
                    real_estate_investment_tracker.get_balance(month_count)
                    * (1 + self.real_estate_ror / 12)
                    + principle_payment
                    + extra_payment,
                )
                tax_benefit_investment_tracker.update_balance(
                    month_count + 1,
                    tax_benefit_investment_tracker.get_balance(month_count)
                    * (1 + self.sp500_ror / 12),
                )
                hybrid_investment_tracker.update_balance(
                    month_count + 1,
                    real_estate_investment_tracker.get_balance(month_count + 1),
                )

                sp500_investment_tracker.update_balance(
                    month_count + 1,
                    sp500_investment_tracker.get_balance(month_count)
                    * (1 + self.sp500_ror / 12)
                    + principle_payment
                    + extra_payment,
                )

                month_count += 1

                if loan_balance <= Dollar(0):
                    break

            if self.standard_deduction < itemized_deduction:
                itemized_vs_standard_deduction = (
                    itemized_deduction - self.standard_deduction
                )
                tax_benefit = itemized_vs_standard_deduction * self.federal_tax_rate
                tax_benefit_totol += tax_benefit

                tax_benefit_investment_tracker.update_balance(
                    month_count,
                    tax_benefit_investment_tracker.get_balance(month_count)
                    + tax_benefit,
                )
                hybrid_investment_tracker.update_balance(
                    month_count,
                    hybrid_investment_tracker.get_balance(month_count) + tax_benefit,
                )

            cumulative_non_equity_payment_tracker.update_balance(
                month_count,
                cumulative_non_equity_payment_tracker.get_balance(month_count)
                + self.yearly_property_tax
                + self.annual_insurance_premium,
            )

            self.house_value *= 1 + self.inflation_rate
            self.annual_insurance_premium *= 1 + self.inflation_rate

            if loan_balance <= Dollar(0):
                break

        print(f"Tax benefit Total: {tax_benefit_totol}")

        plt.figure(figure_num, figsize=(15, 5))
        plt.subplot(1, 3, 1)
        plt.plot(loan_balance_tracker.extract_values(), label="Loan balance")
        plt.plot(
            cumulative_loan_interest_tracker.extract_values(),
            label="Total interest paid",
        )
        plt.plot(
            cumulative_non_equity_payment_tracker.extract_values(),
            label="Total non-equity payment",
        )
        plt.legend()

        plt.subplot(1, 3, 2)
        plt.plot(monthly_interest_tracker.extract_values(), label="Monthly interest")
        plt.plot(
            non_equity_payment_tracker.extract_values(), label="Non-equity payment"
        )
        plt.legend()

        plt.subplot(1, 3, 3)
        plt.plot(
            real_estate_investment_tracker.extract_values(),
            label="Real estate investment",
        )
        plt.plot(tax_benefit_investment_tracker.extract_values(), label="Tax benefit")
        plt.plot(hybrid_investment_tracker.extract_values(), label="Hybrid investment")
        plt.plot(sp500_investment_tracker.extract_values(), label="S&P 500 investment")
        plt.legend()
