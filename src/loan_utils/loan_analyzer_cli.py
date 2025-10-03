#! /usr/bin/python3

import argparse

import matplotlib.pyplot as plt

from loan_utils.mortgage import Mortgage


def main():
    parser = argparse.ArgumentParser(description="Analyze loan details.")

    parser.add_argument(
        "--annual_insurance_premium", type=float, help="Annual insurance premium."
    )
    parser.add_argument("--closing_costs", type=float, help="Closing costs.")
    parser.add_argument(
        "--down_payment_percentage", type=float, help="Down payment percentage."
    )
    parser.add_argument(
        "--interest_rate_percentage", type=float, help="Interest rate percentage."
    )
    parser.add_argument(
        "--loan_type",
        type=str,
        choices=["mortgage", "auto"],
        help="Type of loan to analyze.",
    )
    parser.add_argument("--price", type=float, help="Price of the house or car.")
    parser.add_argument(
        "--property_tax_rate_percentage", type=float, help="Property tax rate."
    )
    parser.add_argument("--term_years", type=int, help="Term length in years.")

    args = parser.parse_args()

    if args.loan_type == "mortgage":
        mortgage_15_year: Mortgage = Mortgage(
            price=args.price,
            interest_rate_percentage=args.interest_rate_percentage,
            term_years=args.term_years,
            down_payment_percentage=args.down_payment_percentage,
            property_tax_rate_percentage=args.property_tax_rate_percentage,
            annual_insurance_premium=args.annual_insurance_premium,
            closing_costs=args.closing_costs,
        )

        mortgage_15_year.mortgage_details()

    plt.show()


if __name__ == "__main__":
    main()
