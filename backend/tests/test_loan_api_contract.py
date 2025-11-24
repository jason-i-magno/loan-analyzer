from datetime import date

from loan_utils.loan import Loan


def test_amortization_schedule_contract_shape():
    loan = Loan(
        annual_interest_percent=6.0,
        down_payment_percent=20.0,
        origination_date=date(2024, 1, 15),
        purchase_price=300000,
        term_years=30,
        monthly_extra_payment=0.0,
        one_time_extras={},
    )

    schedule_df, aggregated_df = loan.amortization_schedule()

    expected_schedule_cols = {
        "payment_id",
        "due_date",
        "payment_date",
        "description",
        "payment_amount",
        "principal_portion",
        "interest_portion",
        "total_interest",
        "ending_balance",
        "resulting_ltv",
    }
    assert expected_schedule_cols.issubset(schedule_df.columns)
    assert len(schedule_df) > 0

    expected_agg_cols = {"due_date", "principal_portion", "interest_portion"}
    assert expected_agg_cols.issubset(aggregated_df.columns)
    assert len(aggregated_df) > 0
