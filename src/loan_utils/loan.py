from loan_utils.dollar import Dollar


class Loan:
    def calculate_monthly_payment(
        self, loan_amount: Dollar, loan_interest_rate: float, term_length_months: int
    ) -> Dollar:
        monthly_interest_rate: float = loan_interest_rate / 12

        return loan_amount.multiply_by_rate(
            monthly_interest_rate
            / (1 - (1 + monthly_interest_rate) ** -term_length_months)
        )
