from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


@dataclass
class LoanTerms:
    principal: Decimal
    purchase_price: Decimal
    annual_rate: Decimal
    monthly_rate: Decimal
    term_months: int
    origination_date: date


@dataclass
class PaymentEvent:
    kind: Literal["scheduled", "curtailment"]
    when: date
    amount: Decimal


@dataclass
class PaymentBreakdown:
    principal: Decimal
    interest: Decimal
    new_balance: Decimal


@dataclass
class ScheduleRow:
    payment_id: int
    due_date: date
    payment_date: date
    description: str
    payment_amount: Decimal
    principal_portion: Decimal
    interest_portion: Decimal
    total_interest: Decimal
    ending_balance: Decimal
    resulting_ltv: Decimal  # fraction (e.g., 0.80)


@dataclass
class AggregatedRow:
    due_date: date
    principal_portion: Decimal
    interest_portion: Decimal
