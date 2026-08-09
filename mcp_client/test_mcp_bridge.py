import asyncio

from loan_policy_mcp import (
    get_car_loan_ltv,
    get_car_loan_tenure,
    get_eligible_car_vehicles,
    search_loan_policy,
)


async def main():

    print("\n====================================")
    print("MCP POLICY BRIDGE TEST")
    print("====================================")

    print("\n1. Car Loan LTV")

    result = await get_car_loan_ltv()

    print(result)

    print("\n2. Car Loan Tenure")

    result = await get_car_loan_tenure()

    print(result)

    print("\n3. Eligible Vehicles")

    result = await get_eligible_car_vehicles()

    print(result)

    print("\n4. Policy Search")

    result = await search_loan_policy(
        "What is the maximum LTV for a car loan?"
    )

    print(result)

    print("\n====================================")
    print("MCP POLICY BRIDGE TEST COMPLETED")
    print("====================================")


if __name__ == "__main__":
    asyncio.run(main())