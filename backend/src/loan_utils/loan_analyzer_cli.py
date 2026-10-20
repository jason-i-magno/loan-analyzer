#! /usr/bin/python3

import argparse
from datetime import date

from loan_utils.mortgage import Mortgage


def main():
    parser = argparse.ArgumentParser(description="Analyze mortgage details.")

    parser.add_argument(
        "--annual_interest_percentage",
        type=float,
        required=True,
        help="Annual interest percentage.",
    )
    parser.add_argument(
        "--closing_costs", type=float, default=0.0, help="Closing costs."
    )
    parser.add_argument(
        "--down_payment_percentage",
        type=float,
        required=True,
        help="Down payment percentage.",
    )
    parser.add_argument(
        "--origination_date",
        type=date.fromisoformat,
        default=date.today(),
        help="Origination date (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--price", type=float, required=True, help="Price of the house."
    )
    parser.add_argument(
        "--term_years", type=int, required=True, help="Term length in years."
    )

    args = parser.parse_args()

    mortgage: Mortgage = Mortgage(
        annual_interest_percent=args.annual_interest_percentage,
        closing_costs=args.closing_costs,
        down_payment_percent=args.down_payment_percentage,
        origination_date=args.origination_date,
        purchase_price=args.price,
        term_years=args.term_years,
    )

    schedule, _ = mortgage.amortization_schedule()

    print(
        f"{'#':>4}  {'Date':<10}  {'Payment':>12}  {'Principal':>12}"
        f"  {'Interest':>12}  {'Balance':>14}"
    )
    for row in schedule:
        print(
            f"{row['payment_id']:>4}  {row['payment_date']:<10}  {row['payment_amount']:>12}"
            f"  {row['principal_portion']:>12}  {row['interest_portion']:>12}"
            f"  {row['ending_balance']:>14}"
        )

    print()
    print(f"Loan amount:     {mortgage.loan_amount}")
    print(f"Monthly payment: {mortgage.monthly_payment}")
    print(f"Total interest:  {mortgage.total_interest}")
    print(f"Total paid:      {mortgage.total_amount_payed}")
    print(f"Total cost:      {mortgage.total_cost}")


if __name__ == "__main__":
    main()
