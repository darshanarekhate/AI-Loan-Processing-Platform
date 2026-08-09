from loan_policy_mcp import call_mcp_tool_sync


def main():

    print("\n====================================")
    print("MCP LOAN POLICY BRIDGE TEST")
    print("====================================")

    # --------------------------------------------------------
    # Test 1: LTV
    # --------------------------------------------------------

    print("\nTesting: get_car_loan_ltv")

    result = call_mcp_tool_sync(
        "get_car_loan_ltv"
    )

    print("Result:")
    print(result)

    # --------------------------------------------------------
    # Test 2: Tenure
    # --------------------------------------------------------

    print("\nTesting: get_car_loan_tenure")

    result = call_mcp_tool_sync(
        "get_car_loan_tenure"
    )

    print("Result:")
    print(result)

    # --------------------------------------------------------
    # Test 3: Eligible vehicles
    # --------------------------------------------------------

    print("\nTesting: get_eligible_car_vehicles")

    result = call_mcp_tool_sync(
        "get_eligible_car_vehicles"
    )

    print("Result:")
    print(result)

    print("\n====================================")
    print("MCP BRIDGE TEST COMPLETED")
    print("====================================")


if __name__ == "__main__":
    main()