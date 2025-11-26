import math
from datetime import date
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loan_utils.mortgage import Mortgage
from pydantic import BaseModel

app = FastAPI(title="Loan Analyzer API")

# Allow frontend origin (in dev: localhost:8050)
origins = [
    "http://localhost:8050",  # Nginx frontend
]

# Allow frontend to talk to backend from a different container
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoanInput(BaseModel):
    annual_interest_percentage: float
    closing_costs: float
    down_payment_percentage: float
    monthly_extra_payment: float
    origination_date: date
    purchase_price: float
    term_years: int
    one_time_extras: dict[date, float] | None


def _validate_number(
    name: str,
    value: float,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> str | None:
    if value is None:
        return f"{name} is required."
    if isinstance(value, float) and not math.isfinite(value):
        return f"{name} must be a finite number."
    if min_value is not None and value < min_value:
        return f"{name} must be >= {min_value}."
    if max_value is not None and value > max_value:
        return f"{name} must be <= {max_value}."
    return None


def validate_payload(data: LoanInput) -> Tuple[Dict[str, Any] | None, List[str]]:
    errors: list[str] = []

    checks = [
        ("annual_interest_percentage", data.annual_interest_percentage, 0.0, None),
        ("closing_costs", data.closing_costs, 0.0, None),
        ("down_payment_percentage", data.down_payment_percentage, 0.0, 100.0),
        ("monthly_extra_payment", data.monthly_extra_payment, 0.0, None),
        ("purchase_price", data.purchase_price, 0.01, None),
        ("term_years", data.term_years, 1, None),
    ]

    for name, value, min_v, max_v in checks:
        err = _validate_number(name, float(value), min_value=min_v, max_value=max_v)
        if err:
            errors.append(err)

    if not isinstance(data.origination_date, date):
        errors.append("origination_date is required and must be a date.")

    normalized_extras: dict[date, float] = {}
    if data.one_time_extras:
        for extra_date, amount in data.one_time_extras.items():
            if not isinstance(extra_date, date):
                errors.append("one_time_extras keys must be dates.")
                continue
            err = _validate_number(
                "one_time_extras amount", float(amount), min_value=0.0
            )
            if err:
                errors.append(err)
            else:
                normalized_extras[extra_date] = float(amount)

    if errors:
        return None, errors

    payload = {
        "annual_interest_percentage": float(data.annual_interest_percentage),
        "closing_costs": float(data.closing_costs),
        "down_payment_percentage": float(data.down_payment_percentage),
        "monthly_extra_payment": float(data.monthly_extra_payment),
        "origination_date": data.origination_date,
        "purchase_price": float(data.purchase_price),
        "term_years": int(data.term_years),
        "one_time_extras": normalized_extras,
    }
    return payload, errors


@app.post("/analyze")
def analyze_loan(data: LoanInput):
    cleaned, errors = validate_payload(data)
    print("cleaned")
    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    mortgage: Mortgage = Mortgage(
        annual_interest_percent=cleaned["annual_interest_percentage"],
        closing_costs=cleaned["closing_costs"],
        down_payment_percent=cleaned["down_payment_percentage"],
        origination_date=cleaned["origination_date"],
        purchase_price=cleaned["purchase_price"],
        term_years=cleaned["term_years"],
        monthly_extra_payment=cleaned["monthly_extra_payment"],
        one_time_extras=cleaned["one_time_extras"],
    )

    schedule, aggregated = mortgage.amortization_schedule()

    return {
        "monthly_payment": mortgage.monthly_payment.amount,
        "principal": mortgage.loan_amount.amount,
        "schedule": schedule.to_dict(orient="records"),
        "aggregated": aggregated.to_dict(orient="records"),
        "total_interest": mortgage.total_interest.amount,
        "total_cost": mortgage.total_amount_payed.amount,
    }
