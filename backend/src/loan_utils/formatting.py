from decimal import Decimal

from loan_utils.dollar import Dollar
from loan_utils.models import AggregatedRow, ScheduleRow


def format_money(value: Decimal) -> str:
    """Return a user-friendly dollar string."""
    return str(Dollar(str(value)))


def format_schedule(rows: list[ScheduleRow]) -> list[dict]:
    return [
        {
            "payment_id": r.payment_id,
            "due_date": r.due_date.isoformat(),
            "payment_date": r.payment_date.isoformat(),
            "description": r.description,
            "payment_amount": format_money(r.payment_amount),
            "principal_portion": format_money(r.principal_portion),
            "interest_portion": format_money(r.interest_portion),
            "total_interest": format_money(r.total_interest),
            "ending_balance": format_money(r.ending_balance),
            "resulting_ltv": f"{r.resulting_ltv * 100:.3f}%",
        }
        for r in rows
    ]


def format_aggregated(rows: list[AggregatedRow]) -> list[dict]:
    return [
        {
            "due_date": r.due_date.isoformat(),
            "principal_portion": float(r.principal_portion),
            "interest_portion": float(r.interest_portion),
        }
        for r in rows
    ]
