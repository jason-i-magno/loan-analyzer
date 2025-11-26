from decimal import Decimal

from loan_utils.models import PaymentBreakdown


def monthly_payment(principal: Decimal, monthly_rate: Decimal, term_months: int) -> Decimal:
    """Standard fixed-rate mortgage payment."""
    if monthly_rate == 0:
        return principal / term_months

    return principal * (
        monthly_rate / (Decimal(1) - (Decimal(1) + monthly_rate) ** (-term_months))
    )


def interest_for_period(balance: Decimal, monthly_rate: Decimal) -> Decimal:
    return balance * monthly_rate


def apply_payment(
    balance: Decimal, payment_amount: Decimal, monthly_rate: Decimal, kind: str
) -> PaymentBreakdown:
    """Return principal/interest split and new balance for an event."""
    if kind == "scheduled":
        interest = interest_for_period(balance, monthly_rate)
        principal = payment_amount - interest
    else:
        interest = Decimal("0")
        principal = payment_amount

    new_balance = balance - principal
    if new_balance < 0:
        new_balance = Decimal("0")

    return PaymentBreakdown(principal=principal, interest=interest, new_balance=new_balance)
