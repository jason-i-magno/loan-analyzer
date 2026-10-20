from decimal import ROUND_HALF_UP, Decimal

from loan_utils.models import PaymentBreakdown

CENT = Decimal("0.01")


def monthly_payment(principal: Decimal, monthly_rate: Decimal, term_months: int) -> Decimal:
    """Standard fixed-rate mortgage payment."""
    if monthly_rate == 0:
        return principal / term_months

    return principal * (
        monthly_rate / (Decimal(1) - (Decimal(1) + monthly_rate) ** (-term_months))
    )


def interest_for_period(balance: Decimal, monthly_rate: Decimal) -> Decimal:
    """Interest accrued for one period, rounded to the cent."""
    return (balance * monthly_rate).quantize(CENT, rounding=ROUND_HALF_UP)


def apply_payment(
    balance: Decimal,
    payment_amount: Decimal,
    monthly_rate: Decimal,
    kind: str,
    final: bool = False,
) -> PaymentBreakdown:
    """Return the amount applied, principal/interest split, and new balance for an event.

    A payment never pays down more than the outstanding balance, and the final
    scheduled payment (``final=True``) clears whatever balance remains so that
    cent-rounding of the monthly payment doesn't leave a residue.
    """
    if kind == "scheduled":
        interest = interest_for_period(balance, monthly_rate)
    else:
        interest = Decimal("0")

    principal = payment_amount - interest
    if principal > balance or final:
        principal = balance

    return PaymentBreakdown(
        amount=principal + interest,
        principal=principal,
        interest=interest,
        new_balance=balance - principal,
    )
