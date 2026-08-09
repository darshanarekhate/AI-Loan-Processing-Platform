import asyncio

from langchain_groq import ChatGroq

from mcp_client.loan_policy_tools import MCP_TOOLS


# ============================================================
# GROQ
# ============================================================

llm = ChatGroq(
    model="your-existing-groq-model",
    temperature=0,
)


# ============================================================
# BIND MCP TOOLS
# ============================================================

llm_with_tools = llm.bind_tools(MCP_TOOLS)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Loan Assistant.

You answer questions about loan products using the available
loan policy tools.

Rules:

1. Use the loan policy tools whenever the answer depends on
   bank loan policy.

2. Do not invent loan policy information.

3. For car-loan LTV questions, use get_car_loan_ltv.

4. For car-loan tenure questions, use get_car_loan_tenure.

5. For eligible vehicle questions, use get_eligible_car_vehicles.

6. For other policy-related questions, use search_loan_policy.

7. After receiving information from a tool, explain the answer
   clearly and concisely to the customer.

8. If the policy does not provide enough information, say so
   rather than making up an answer.
"""


# ============================================================
# MCP + GROQ
# ============================================================

async def ask_loan_assistant(question: str):

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", question),
    ]

    response = await llm_with_tools.ainvoke(messages)

    # --------------------------------------------------------
    # TOOL CALL
    # --------------------------------------------------------

    if response.tool_calls:

        messages.append(response)

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tool = next(
                (
                    t
                    for t in MCP_TOOLS
                    if t.name == tool_name
                ),
                None,
            )

            if tool is None:
                raise RuntimeError(
                    f"Tool '{tool_name}' not found."
                )

            tool_result = await tool.ainvoke(tool_args)

            messages.append(
                (
                    "tool",
                    str(tool_result),
                    tool_call["id"],
                )
            )

        # ----------------------------------------------------
        # FINAL GROQ RESPONSE
        # ----------------------------------------------------

        final_response = await llm_with_tools.ainvoke(messages)

        return final_response.content

    return response.content


# ============================================================
# TEST
# ============================================================

async def main():

    questions = [
        "What is the maximum LTV for a car loan?",
        "What is the maximum tenure for a car loan?",
        "Which vehicles are eligible for a car loan?",
        "What credit score is required for a car loan?",
    ]

    for question in questions:

        print("\n========================================")
        print("QUESTION:")
        print(question)
        print("========================================")

        answer = await ask_loan_assistant(question)

        print("\nANSWER:")
        print(answer)


if __name__ == "__main__":
    asyncio.run(main())