import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.loan_utils.mortgage import Mortgage

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
    purchase_price: float
    term_years: int


@app.get("/analyze")
def analyze():
    return {"message": "Loan analysis complete!"}


@app.post("/analyze")
def analyze_loan(data: LoanInput):
    mortgage: Mortgage = Mortgage(
        annual_interest_percent=data.annual_interest_percentage,
        closing_costs=data.closing_costs,
        down_payment_percent=data.down_payment_percentage,
        purchase_price=data.purchase_price,
        term_years=data.term_years,
    )

    return {
        "monthly_payment": mortgage.monthly_payment.amount,
        "principal": mortgage.loan_amount.amount,
        "total_interest": mortgage.total_interest.amount,
        "total_cost": mortgage.total_amount_payed.amount,
    }
