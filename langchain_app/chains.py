import re

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)

from langchain_app.retriever import get_retriever


# ============================================================
# Loan Policy Retriever
# ============================================================

retriever = get_retriever()


# ============================================================
# Local Hugging Face Model
# ============================================================

MODEL_NAME = "google/flan-t5-small"

print("Loading local policy model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

policy_model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

print("Local policy model loaded successfully.")


# ============================================================
# Retrieve Policy Documents
# ============================================================

def retrieve_policy(question: str):
    """
    Retrieve relevant loan policy documents from FAISS.
    """

    return retriever.invoke(question)


# ============================================================
# Build Policy Context
# ============================================================

def build_context(docs) -> str:
    """
    Combine retrieved policy documents.
    """

    context_parts = []

    for doc in docs:

        text = doc.page_content.strip()

        if text:
            context_parts.append(text)

    return "\n\n".join(context_parts)


# ============================================================
# Exact LTV Extraction
# ============================================================

def extract_ltv_answer(context: str) -> str | None:

    if (
        "loan-to-value" not in context.lower()
        and "ltv" not in context.lower()
    ):
        return None

    match = re.search(
        r"(?:up to|max(?:imum)?)[\s:]*(\d+(?:\.\d+)?)\s*%",
        context,
        re.IGNORECASE,
    )

    if not match:
        return None

    percentage = match.group(1)

    return (
        f"The maximum LTV for a car loan is {percentage}% "
        "of the vehicle's on-road price, subject to "
        "policy and customer eligibility."
    )


# ============================================================
# Exact Tenure Extraction
# ============================================================

def extract_tenure_answer(context: str) -> str | None:

    if "loan tenure" not in context.lower():
        return None

    minimum_match = re.search(
        r"Minimum\s*:\s*(\d+)\s*Months",
        context,
        re.IGNORECASE,
    )

    maximum_match = re.search(
        r"Maximum\s*:\s*(\d+)\s*Months",
        context,
        re.IGNORECASE,
    )

    if not minimum_match or not maximum_match:
        return None

    minimum = minimum_match.group(1)
    maximum = maximum_match.group(1)

    return (
        f"The car loan tenure ranges from {minimum} "
        f"months to {maximum} months."
    )


# ============================================================
# Eligible Vehicles Extraction
# ============================================================

def extract_vehicle_answer(context: str) -> str | None:

    if "eligible vehicles" not in context.lower():
        return None

    vehicles = [
        "New Cars",
        "Used Cars",
        "SUVs",
        "Hatchbacks",
        "Sedans",
        "Multi-Utility Vehicles (MUVs)",
    ]

    found_vehicles = []

    for vehicle in vehicles:

        if vehicle.lower() in context.lower():
            found_vehicles.append(vehicle)

    if not found_vehicles:
        return None

    return (
        "Eligible vehicles for a car loan include: "
        + ", ".join(found_vehicles)
        + "."
    )


# ============================================================
# Car Loan Eligibility Extraction
# ============================================================

def extract_car_loan_eligibility(context: str) -> str | None:
    """
    Build a complete car-loan eligibility response directly
    from the retrieved policy.

    This avoids relying on FLAN-T5 to select important
    policy facts.
    """

    context_lower = context.lower()

    # --------------------------------------------------------
    # Check whether this is actually car-loan policy
    # --------------------------------------------------------

    if "car loan" not in context_lower:
        return None

    eligibility_points = []

    # --------------------------------------------------------
    # Basic eligibility
    # --------------------------------------------------------

    if (
        "financial" in context_lower
        and "personal" in context_lower
        and "regulatory" in context_lower
    ):
        eligibility_points.append(
            "Eligibility is assessed based on financial, "
            "personal, and regulatory criteria."
        )

    # --------------------------------------------------------
    # Credit score
    # --------------------------------------------------------

    credit_match = re.search(
        r"Car Loan\s*.*?"
        r"Minimum credit score\s*:\s*(\d+)",
        context,
        re.IGNORECASE | re.DOTALL,
    )

    if credit_match:

        credit_score = credit_match.group(1)

        eligibility_points.append(
            f"Minimum credit score: {credit_score}."
        )

    # --------------------------------------------------------
    # LTV
    # --------------------------------------------------------

    ltv_match = re.search(
        r"(?:up to|max(?:imum)?)[\s:]*(\d+(?:\.\d+)?)\s*%"
        r".{0,120}?"
        r"vehicle",
        context,
        re.IGNORECASE | re.DOTALL,
    )

    if ltv_match:

        ltv = ltv_match.group(1)

        eligibility_points.append(
            f"Financing may be available up to {ltv}% "
            "of the vehicle's on-road price, subject to "
            "policy and customer eligibility."
        )

    # --------------------------------------------------------
    # Loan tenure
    # --------------------------------------------------------

    minimum_match = re.search(
        r"Minimum\s*:\s*(\d+)\s*Months",
        context,
        re.IGNORECASE,
    )

    maximum_match = re.search(
        r"Maximum\s*:\s*(\d+)\s*Months",
        context,
        re.IGNORECASE,
    )

    if minimum_match and maximum_match:

        minimum = minimum_match.group(1)
        maximum = maximum_match.group(1)

        eligibility_points.append(
            f"Loan tenure: {minimum} to {maximum} months."
        )

    # --------------------------------------------------------
    # Eligible vehicles
    # --------------------------------------------------------

    vehicles = [
        "New Cars",
        "Used Cars",
        "SUVs",
        "Hatchbacks",
        "Sedans",
        "Multi-Utility Vehicles (MUVs)",
    ]

    found_vehicles = [
        vehicle
        for vehicle in vehicles
        if vehicle.lower() in context_lower
    ]

    if found_vehicles:

        eligibility_points.append(
            "Eligible vehicles: "
            + ", ".join(found_vehicles)
            + "."
        )

    # --------------------------------------------------------
    # Application assessment
    # --------------------------------------------------------

    if "every loan application undergoes an eligibility assessment" in context_lower:

        eligibility_points.append(
            "Every loan application undergoes an eligibility "
            "assessment before approval."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    if not eligibility_points:
        return None

    return (
        "### Car Loan Eligibility\n\n"
        + "\n".join(
            f"- {point}"
            for point in eligibility_points
        )
    )


# ============================================================
# Exact Policy Router
# ============================================================

def get_exact_policy_answer(
    question: str,
    context: str,
) -> str | None:

    question_lower = question.lower()

    # --------------------------------------------------------
    # Car Loan Eligibility
    # --------------------------------------------------------

    if (
        "eligibility" in question_lower
        and "car loan" in question_lower
    ):

        answer = extract_car_loan_eligibility(context)

        if answer:
            return answer

    # --------------------------------------------------------
    # LTV
    # --------------------------------------------------------

    if (
        "ltv" in question_lower
        or "loan-to-value" in question_lower
        or "loan to value" in question_lower
    ):

        answer = extract_ltv_answer(context)

        if answer:
            return answer

    # --------------------------------------------------------
    # Loan Tenure
    # --------------------------------------------------------

    if (
        "tenure" in question_lower
        or "loan duration" in question_lower
        or "repayment period" in question_lower
    ):

        answer = extract_tenure_answer(context)

        if answer:
            return answer

    # --------------------------------------------------------
    # Eligible Vehicles
    # --------------------------------------------------------

    if (
        "eligible vehicle" in question_lower
        or "vehicles are eligible" in question_lower
        or "vehicle types" in question_lower
    ):

        answer = extract_vehicle_answer(context)

        if answer:
            return answer

    return None


# ============================================================
# Local FLAN-T5 Generation
# ============================================================

def generate_answer(prompt: str) -> str:

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    outputs = policy_model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False,
    )

    return tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    ).strip()


# ============================================================
# Ask Loan Policy
# ============================================================

def ask_policy(question: str) -> str:
    """
    RAG-based loan policy question answering.

    Flow:

        Question
            |
            v
        FAISS Retriever
            |
            v
        Retrieved Policy
            |
            +----------------------+
            |                      |
            v                      v
      Exact Policy             General
       Extraction              Question
            |                      |
            v                      v
      Direct Answer            FLAN-T5
            |                      |
            +----------+-----------+
                       |
                       v
                    Response

    Groq is NOT used.
    """

    question = question.strip()

    if not question:

        return "Please enter a loan policy question."

    # --------------------------------------------------------
    # Retrieve documents
    # --------------------------------------------------------

    docs = retrieve_policy(question)

    if not docs:

        return (
            "I couldn't find any relevant information in the "
            "loan policy knowledge base for your question."
        )

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = build_context(docs)

    if not context:

        return (
            "I couldn't find any relevant information in the "
            "loan policy knowledge base for your question."
        )

    # --------------------------------------------------------
    # Exact policy route
    # --------------------------------------------------------

    exact_answer = get_exact_policy_answer(
        question,
        context,
    )

    if exact_answer:

        print("POLICY ROUTE: EXACT POLICY EXTRACTION")

        return exact_answer

    # --------------------------------------------------------
    # General local model route
    # --------------------------------------------------------

    print("POLICY ROUTE: LOCAL FLAN-T5")

    prompt = f"""
You are a bank loan policy assistant.

Answer the customer's question using ONLY the policy
information provided below.

POLICY:
{context}

QUESTION:
{question}

RULES:

1. Give a direct answer.
2. Use only information supported by the policy.
3. Do not invent bank-specific information.
4. Do not repeat the entire policy.
5. If the policy does not contain the answer, say:

"The requested information is not available in the
bank policy provided."

Answer:
"""

    try:

        answer = generate_answer(prompt)

    except Exception as exc:

        print("Policy model error:", exc)

        return (
            "Unable to generate a loan policy answer "
            "at this time."
        )

    if not answer:

        return (
            "I couldn't generate an answer from the "
            "loan policy information."
        )

    return answer