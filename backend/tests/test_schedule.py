from datetime import date
from decimal import Decimal

from loan_utils.models import LoanTerms, PaymentEvent
from loan_utils.schedule import aggregate_schedule, build_payment_events, build_schedule


def quantize(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places))


def test_build_payment_events_ordering_and_counts():
    origination = date(2024, 1, 15)
    events = build_payment_events(
        origination_date=origination,
        term_months=2,
        monthly_payment=Decimal("100"),
        monthly_extra=Decimal("50"),
        extras={date(2024, 2, 20): Decimal("75")},
    )

    # 2 scheduled + 2 monthly extras + 1 one-time
    assert len(events) == 5
    assert events == sorted(events, key=lambda e: e.when)
    assert events[0].when == date(2024, 2, 20)  # one-time extra
    assert events[1].kind == "curtailment"  # monthly extra before first scheduled
    assert events[-1].kind == "scheduled"


def test_build_schedule_pays_off_early_with_large_extra():
    terms = LoanTerms(
        principal=Decimal("1000"),
        purchase_price=Decimal("1500"),
        annual_rate=Decimal("0.12"),
        monthly_rate=Decimal("0.01"),
        term_months=12,
        origination_date=date(2024, 1, 15),
    )
    events = [
        PaymentEvent(kind="curtailment", when=date(2024, 2, 15), amount=Decimal("900")),
        PaymentEvent(kind="scheduled", when=date(2024, 3, 1), amount=Decimal("120")),
        PaymentEvent(kind="scheduled", when=date(2024, 4, 1), amount=Decimal("120")),
    ]

    rows, total_interest, total_paid = build_schedule(terms, events)

    # Should stop once balance hits zero; only two events needed.
    assert len(rows) == 2
    assert rows[-1].ending_balance == Decimal("0")
    assert total_paid == Decimal("1020")  # 900 + 120
    assert quantize(total_interest) == Decimal("1.00")


def test_aggregate_schedule_sums_by_due_date():
    terms = LoanTerms(
        principal=Decimal("500"),
        purchase_price=Decimal("1000"),
        annual_rate=Decimal("0.12"),
        monthly_rate=Decimal("0.01"),
        term_months=6,
        origination_date=date(2024, 1, 15),
    )
    events = [
        PaymentEvent(kind="scheduled", when=date(2024, 3, 1), amount=Decimal("100")),
        PaymentEvent(kind="curtailment", when=date(2024, 3, 2), amount=Decimal("50")),
        PaymentEvent(kind="scheduled", when=date(2024, 4, 1), amount=Decimal("100")),
    ]

    rows, total_interest, _ = build_schedule(terms, events)
    aggregated = aggregate_schedule(rows)

    assert len(aggregated) == 2

    march = aggregated[0]
    april = aggregated[1]

    assert march.due_date.month == 3
    march_principal = quantize(march.principal_portion)
    # First scheduled payment: $100 with $5 interest -> $95 principal.
    assert march_principal == Decimal("95.00")
    assert quantize(total_interest) >= Decimal("0.0")

    assert april.due_date.month == 4
    # April bucket includes the curtailment (50) + second scheduled payment principal (~96.45)
    assert quantize(april.principal_portion) == Decimal("146.45")
