#! /usr/bin/python3

import argparse

from loan_utils.mortgage import Mortgage


def main():
    parser = argparse.ArgumentParser(description="Analyze loan details.")

    parser.add_argument(
        "--annual_interest_percentage", type=float, help="Annual interest percentage."
    )
    parser.add_argument("--closing_costs", type=float, help="Closing costs.")
    parser.add_argument(
        "--down_payment_percentage", type=float, help="Down payment percentage."
    )
    parser.add_argument(
        "--loan_type",
        type=str,
        choices=["mortgage", "auto"],
        help="Type of loan to analyze.",
    )
    parser.add_argument("--price", type=float, help="Price of the house or car.")
    parser.add_argument("--term_years", type=int, help="Term length in years.")

    args = parser.parse_args()

    if args.loan_type == "mortgage":
        mortgage_15_year: Mortgage = Mortgage(
            purchase_price=args.price,
            annual_interest_percent=args.annual_interest_percentage,
            term_years=args.term_years,
            down_payment_percent=args.down_payment_percentage,
            closing_costs=args.closing_costs,
        )

        mortgage_15_year.amortization_schedule()


if __name__ == "__main__":
    main()
