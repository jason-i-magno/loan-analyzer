from datetime import date
from decimal import Decimal

from loan_utils.formatting import format_aggregated, format_money, format_schedule
from loan_utils.models import AggregatedRow, ScheduleRow


def test_format_money_rounds_and_signs():
    assert format_money(Decimal("123.456")) == "$123.46"
    assert format_money(Decimal("-50.1")) == "-$50.10"


def test_format_schedule_serializes_fields():
    rows = [
        ScheduleRow(
            payment_id=1,
            due_date=date(2024, 3, 1),
            payment_date=date(2024, 3, 1),
            description="Scheduled",
            payment_amount=Decimal("100"),
            principal_portion=Decimal("80"),
            interest_portion=Decimal("20"),
            total_interest=Decimal("20"),
            ending_balance=Decimal("900"),
            resulting_ltv=Decimal("0.60"),
        )
    ]

    formatted = format_schedule(rows)
    assert formatted[0]["due_date"] == "2024-03-01"
    assert formatted[0]["payment_amount"] == "$100.00"
    assert formatted[0]["resulting_ltv"].startswith("60.000")


def test_format_aggregated_serializes_to_primitives():
    rows = [
        AggregatedRow(
            due_date=date(2024, 3, 1),
            principal_portion=Decimal("80"),
            interest_portion=Decimal("20"),
        )
    ]

    formatted = format_aggregated(rows)
    assert formatted[0]["due_date"] == "2024-03-01"
    assert isinstance(formatted[0]["principal_portion"], float)
    assert isinstance(formatted[0]["interest_portion"], float)
