from loan_policy_mcp import (
    get_car_loan_ltv,
    get_car_loan_tenure,
    get_eligible_car_vehicles,
    search_loan_policy,
)


def main():

    print("\n====================================")
    print("MCP POLICY HELPER TEST")
    print("====================================")

    print("\n1. Car Loan LTV")
    print(get_car_loan_ltv())

    print("\n2. Car Loan Tenure")
    print(get_car_loan_tenure())

    print("\n3. Eligible Vehicles")
    print(get_eligible_car_vehicles())

    print("\n4. Policy Search")
    print(
        search_loan_policy(
            "What is the maximum LTV for a car loan?"
        )
    )

    print("\n====================================")
    print("TEST COMPLETED")
    print("====================================")


if __name__ == "__main__":
    main()