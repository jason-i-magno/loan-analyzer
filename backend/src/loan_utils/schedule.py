from datetime import date
from decimal import Decimal
from typing import Iterable

from dateutil.relativedelta import relativedelta

from loan_utils.calc import apply_payment
from loan_utils.models import AggregatedRow, LoanTerms, PaymentEvent, ScheduleRow


def build_payment_events(
    origination_date: date,
    term_months: int,
    monthly_payment: Decimal,
    monthly_extra: Decimal,
    extras: dict[date, Decimal],
) -> list[PaymentEvent]:
    events: list[PaymentEvent] = []
    first_due_date = (origination_date + relativedelta(months=+2)).replace(day=1)
    payment_date = first_due_date

    for _ in range(term_months):
        if monthly_extra > Decimal("0"):
            events.append(
                PaymentEvent(
                    kind="curtailment",
                    when=payment_date + relativedelta(days=-1),
                    amount=monthly_extra,
                )
            )
        events.append(PaymentEvent(kind="scheduled", when=payment_date, amount=monthly_payment))
        payment_date += relativedelta(months=+1)

    for extra_date, amount in extras.items():
        events.append(PaymentEvent(kind="curtailment", when=extra_date, amount=amount))

    events.sort(key=lambda e: e.when)
    return events


def build_schedule(
    terms: LoanTerms, events: Iterable[PaymentEvent]
) -> tuple[list[ScheduleRow], Decimal, Decimal]:
    """Return schedule rows plus totals (interest, amount paid)."""
    balance = terms.principal
    total_interest = Decimal("0")
    total_paid = Decimal("0")
    rows: list[ScheduleRow] = []
    payment_id = 0
    due_date = (terms.origination_date + relativedelta(months=+2)).replace(day=1)

    for event in events:
        if balance <= 0:
            break

        payment_id += 1
        breakdown = apply_payment(balance, event.amount, terms.monthly_rate, event.kind)

        total_interest += breakdown.interest
        total_paid += event.amount
        balance = breakdown.new_balance

        rows.append(
            ScheduleRow(
                payment_id=payment_id,
                due_date=due_date,
                payment_date=event.when,
                description="Scheduled" if event.kind == "scheduled" else "Curtailment",
                payment_amount=event.amount,
                principal_portion=breakdown.principal,
                interest_portion=breakdown.interest,
                total_interest=total_interest,
                ending_balance=balance,
                resulting_ltv=balance / terms.purchase_price,
            )
        )

        if event.kind == "scheduled":
            due_date += relativedelta(months=+1)

    return rows, total_interest, total_paid


def aggregate_schedule(rows: list[ScheduleRow]) -> list[AggregatedRow]:
    by_date: dict[date, dict[str, Decimal]] = {}
    for row in rows:
        if row.due_date not in by_date:
            by_date[row.due_date] = {"principal": Decimal("0"), "interest": Decimal("0")}
        by_date[row.due_date]["principal"] += row.principal_portion
        by_date[row.due_date]["interest"] += row.interest_portion

    aggregated: list[AggregatedRow] = []
    for due_date, values in sorted(by_date.items()):
        aggregated.append(
            AggregatedRow(
                due_date=due_date,
                principal_portion=values["principal"],
                interest_portion=values["interest"],
            )
        )

    return aggregated
