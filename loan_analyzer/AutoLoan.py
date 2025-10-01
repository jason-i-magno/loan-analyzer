import matplotlib.pyplot as plt
from BalanceTracker import BalanceTracker
from Dollar import Dollar
from Loan import Loan


class AutoLoan(Loan):
    def auto_loan_details(self) -> None:
        loan_amount: Dollar = Dollar(21893.01)
        loan_interest_rate: float = 0.0699
        term_length_months: int = 48
        extra_insurance_monthly_payment: Dollar = Dollar(71.75)

        monthly_interest_rate: float = loan_interest_rate / 12
        monthly_payment: Dollar = self.calculate_monthly_payment(
            loan_amount, loan_interest_rate, term_length_months
        )
        print(f"Monthly payment: {monthly_payment}")

        loan_balance_tracker: BalanceTracker = BalanceTracker(term_length_months)
        loan_interest_tracker: BalanceTracker = BalanceTracker(term_length_months)
        savings_balance_tracker: BalanceTracker = BalanceTracker(term_length_months)
        savings_interest_tracker: BalanceTracker = BalanceTracker(term_length_months)

        loan_balance: Dollar = loan_amount
        total_loan_interest: Dollar = Dollar(0)
        savings_balance: Dollar = loan_amount
        total_savings_interest: Dollar = Dollar(0)
        present_value: Dollar = Dollar(0)
        total_extra_insurance: float = Dollar(0)

        for month in range(term_length_months):
            loan_interest: Dollar = loan_balance * monthly_interest_rate
            loan_balance = loan_balance - (monthly_payment - loan_interest)
            savings_interest: Dollar = savings_balance * self.sp500_ror / 12
            principle_payment = monthly_payment - loan_interest
            savings_balance = savings_balance + savings_interest - principle_payment

            total_loan_interest += loan_interest
            total_savings_interest += savings_interest
            total_extra_insurance += extra_insurance_monthly_payment

            present_value += principle_payment / (1 + self.inflation_rate / 12) ** month

            loan_balance_tracker.update_balance(month, loan_balance)
            loan_interest_tracker.update_balance(
                month, total_loan_interest + total_extra_insurance
            )
            savings_balance_tracker.update_balance(month, savings_balance)
            savings_interest_tracker.update_balance(month, total_savings_interest)

        depreciation_savings = loan_amount - present_value

        margin: Dollar = (
            total_savings_interest
            + depreciation_savings
            - total_loan_interest
            - total_extra_insurance
        )

        print(f"Total loan interest: {total_loan_interest}")
        print(f"Total savings interest: {total_savings_interest}")
        print(f"Total extra insurance: {total_extra_insurance}")
        print(f"Present value: {present_value}")
        print(f"Depreciation of savings: {depreciation_savings}")
        print(f"Margin: {margin}")

        plt.figure()
        plt.plot(loan_balance_tracker.extract_values(), label="Loan Balance")
        plt.plot(loan_interest_tracker.extract_values(), label="Loan Interest")
        plt.plot(savings_balance_tracker.extract_values(), label="Savings Balance")
        plt.plot(savings_interest_tracker.extract_values(), label="Savings Interest")
        plt.legend()
        plt.show()


def main():
    blanco_taco: AutoLoan = AutoLoan()

    blanco_taco.auto_loan_details()


if __name__ == "__main__":
    main()
