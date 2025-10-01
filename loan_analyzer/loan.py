from Dollar import Dollar


class Loan:
    federal_tax_rate: float = 0.22
    inflation_rate: float = 0.03
    sp500_ror: float = 0.1
    standard_deduction: Dollar = Dollar(15000.0)

    def calculate_monthly_payment(
        self, loan_amount: Dollar, loan_interest_rate: float, term_length_months: int
    ) -> Dollar:
        monthly_interest_rate: float = loan_interest_rate / 12

        return (
            loan_amount
            * monthly_interest_rate
            / (1 - (1 + monthly_interest_rate) ** -term_length_months)
        )
