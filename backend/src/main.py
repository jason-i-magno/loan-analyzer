import math
from datetime import date
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loan_utils.mortgage import Mortgage
from loan_utils.schedule import final_due_date
from pydantic import BaseModel

MAX_ANNUAL_INTEREST_PERCENTAGE = 100
# Caps every dollar input; also keeps amounts within Decimal's 28-digit precision.
MAX_DOLLAR_AMOUNT = 1_000_000_000
MAX_TERM_YEARS = 50

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
    one_time_extras: dict[date, float] | None = None


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Report schema errors in the same {"errors": [...]} shape as validate_payload."""
    errors = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part != "body")
        errors.append(f"{field}: {err['msg']}" if field else err["msg"])
    return JSONResponse(status_code=422, content={"errors": errors})


def _validate_number(
    name: str,
    value: float,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> str | None:
    if not math.isfinite(value):
        return f"{name} must be a finite number."
    if min_value is not None and value < min_value:
        return f"{name} must be >= {min_value}."
    if max_value is not None and value > max_value:
        return f"{name} must be <= {max_value}."
    return None


def validate_payload(data: LoanInput) -> Tuple[Dict[str, Any] | None, List[str]]:
    errors: list[str] = []

    checks = [
        (
            "annual_interest_percentage",
            data.annual_interest_percentage,
            0,
            MAX_ANNUAL_INTEREST_PERCENTAGE,
        ),
        ("closing_costs", data.closing_costs, 0, MAX_DOLLAR_AMOUNT),
        ("down_payment_percentage", data.down_payment_percentage, 0, 100),
        ("monthly_extra_payment", data.monthly_extra_payment, 0, MAX_DOLLAR_AMOUNT),
        ("purchase_price", data.purchase_price, 0.01, MAX_DOLLAR_AMOUNT),
        ("term_years", data.term_years, 1, MAX_TERM_YEARS),
    ]

    for name, value, min_v, max_v in checks:
        err = _validate_number(name, float(value), min_value=min_v, max_value=max_v)
        if err:
            errors.append(err)

    term_is_valid = 1 <= data.term_years <= MAX_TERM_YEARS
    last_due_date = (
        final_due_date(data.origination_date, data.term_years * 12)
        if term_is_valid
        else None
    )

    normalized_extras: dict[date, float] = {}
    for extra_date, amount in (data.one_time_extras or {}).items():
        err = _validate_number(
            f"one_time_extras amount on {extra_date}",
            float(amount),
            min_value=0,
            max_value=MAX_DOLLAR_AMOUNT,
        )
        if err:
            errors.append(err)
        elif extra_date < data.origination_date:
            errors.append(
                f"one_time_extras date {extra_date} is before the origination date."
            )
        # The final scheduled payment clears the loan, so a later extra would be ignored.
        elif last_due_date and extra_date >= last_due_date:
            errors.append(
                f"one_time_extras date {extra_date} must be before the final payment due date ({last_due_date})."
            )
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
        "schedule": schedule,
        "aggregated": aggregated,
        "total_interest": mortgage.total_interest.amount,
        "total_paid": mortgage.total_amount_payed.amount,
        "total_cost": mortgage.total_cost.amount,
    }
