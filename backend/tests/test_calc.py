from decimal import Decimal

from loan_utils.calc import apply_payment, monthly_payment


def quantize(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places))


def test_monthly_payment_zero_rate():
    payment = monthly_payment(Decimal("120000"), Decimal("0"), 120)
    assert payment == Decimal("1000")


def test_monthly_payment_positive_rate_rounding():
    # 6% annual -> 0.5% monthly; 100k over 30 years ≈ $599.55
    payment = monthly_payment(Decimal("100000"), Decimal("0.005"), 360)
    assert quantize(payment) == Decimal("599.55")


def test_apply_payment_scheduled_splits_interest_principal():
    breakdown = apply_payment(
        balance=Decimal("1000"),
        payment_amount=Decimal("120"),
        monthly_rate=Decimal("0.01"),
        kind="scheduled",
    )
    assert breakdown.interest == Decimal("10.00")
    assert breakdown.principal == Decimal("110.00")
    assert breakdown.new_balance == Decimal("890.00")


def test_apply_payment_curtailment_no_interest():
    breakdown = apply_payment(
        balance=Decimal("1000"),
        payment_amount=Decimal("200"),
        monthly_rate=Decimal("0.01"),
        kind="curtailment",
    )
    assert breakdown.interest == Decimal("0")
    assert breakdown.principal == Decimal("200")
    assert breakdown.new_balance == Decimal("800")
