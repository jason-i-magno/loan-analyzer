import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "annual_interest_percentage": 6.0,
    "closing_costs": 5000,
    "down_payment_percentage": 20,
    "monthly_extra_payment": 0,
    "origination_date": "2024-01-15",
    "purchase_price": 300000,
    "term_years": 30,
    "one_time_extras": {},
}


def post(**overrides):
    return client.post("/analyze", json={**VALID_PAYLOAD, **overrides})


def test_analyze_accepts_valid_payload():
    response = post()
    assert response.status_code == 200
    data = response.json()

    assert data["monthly_payment"] == 1438.92
    assert data["principal"] == 240000
    assert len(data["schedule"]) == 360


def test_analyze_one_time_extras_is_optional():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "one_time_extras"}
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200


def test_schema_errors_use_errors_shape():
    response = post(term_years="abc")
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert len(errors) == 1
    assert errors[0].startswith("term_years:")


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"term_years": 51}, "term_years must be <= 50"),
        ({"term_years": 0}, "term_years must be >= 1"),
        ({"purchase_price": 2e9}, "purchase_price must be <="),
        ({"closing_costs": 1e30}, "closing_costs must be <="),
        ({"monthly_extra_payment": 1e30}, "monthly_extra_payment must be <="),
        ({"one_time_extras": {"2024-06-01": 1e30}}, "amount on 2024-06-01 must be <="),
        ({"annual_interest_percentage": 101}, "annual_interest_percentage must be <="),
        ({"down_payment_percentage": -1}, "down_payment_percentage must be >="),
        ({"one_time_extras": {"2023-12-31": 1000}}, "before the origination date"),
        ({"one_time_extras": {"2054-02-01": 1000}}, "before the final payment due date"),
        ({"one_time_extras": {"2024-06-01": -5}}, "amount on 2024-06-01 must be >="),
    ],
)
def test_validation_errors(overrides, expected):
    response = post(**overrides)
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any(expected in e for e in errors), errors


def test_extra_just_before_final_due_date_is_applied():
    # First due 2024-03-01, so the 360th payment is due 2054-02-01.
    response = post(one_time_extras={"2054-01-31": 100})
    assert response.status_code == 200
    schedule = response.json()["schedule"]
    assert schedule[-2]["description"] == "Curtailment"
    assert schedule[-2]["payment_amount"] == "$100.00"
