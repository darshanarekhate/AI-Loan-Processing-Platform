import sqlite3

from langgraph.graph import StateGraph, START, END

from config import DATABASE_PATH
from src.state import LoanState
from src.decision_agent import ai_decision
from src.fraud_agent import fraud_check
from src.name_match import name_match_node
from src.review import review_check

# =====================================================
# Database Connection
# =====================================================

def get_connection():
    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


# =====================================================
# Login Node
# =====================================================

def login_node(state):

    print("=" * 60)
    print("LOGIN")
    print("=" * 60)

    state["login"] = True

    print("Login Successful")

    return state


# =====================================================
# Document Verification
# =====================================================

def document_node(state):

    print("=" * 60)
    print("DOCUMENT VERIFICATION")
    print("=" * 60)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM documents
        WHERE user_id=?
    """, (state["user_id"],))

    total = cursor.fetchone()[0]

    conn.close()

    state["documents_uploaded"] = total >= 2

    print("Documents Uploaded :", state["documents_uploaded"])

    return state


# =====================================================
# OCR Verification
# =====================================================

def ocr_node(state):

    print("=" * 60)
    print("OCR VERIFICATION")
    print("=" * 60)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM documents
        WHERE user_id=?
        AND extracted_number IS NOT NULL
    """, (state["user_id"],))

    total = cursor.fetchone()[0]

    conn.close()

    state["ocr_completed"] = total > 0

    print("OCR Completed :", state["ocr_completed"])

    return state


# =====================================================
# KYC Node
# =====================================================

def kyc_node(state):

    print("=" * 60)
    print("KYC SCORE")
    print("=" * 60)

    print("Score :", state["kyc_score"])
    print("Status :", state["kyc_status"])

    return state


# =====================================================
# Loan Decision
# =====================================================

def loan_node(state):

    print("=" * 60)
    print("AI LOAN DECISION")
    print("=" * 60)

    result = ai_decision(state)

    print(result)

    # ---------------------------------
    # Extract Decision Safely
    # ---------------------------------

    decision = "REJECTED"

    lines = result.splitlines()

    for i, line in enumerate(lines):

        if line.strip().upper() == "DECISION:":

            if i + 1 < len(lines):

                decision = lines[i + 1].strip().upper()

            break

    state["loan_status"] = decision
    state["decision"] = decision
    state["explanation"] = result

    return state

# =====================================================
# Build Workflow
# =====================================================

graph = StateGraph(LoanState)

graph.add_node("Login", login_node)
graph.add_node("Documents", document_node)
graph.add_node("OCR", ocr_node)
graph.add_node("Name Match", name_match_node)
graph.add_node("KYC", kyc_node)
graph.add_node("Fraud",fraud_check)
graph.add_node("Review", review_check)
graph.add_node("Loan", loan_node)


graph.add_edge(START, "Login")
graph.add_edge("Login", "Documents")
graph.add_edge("Documents", "OCR")
graph.add_edge("OCR", "Name Match")
graph.add_edge("Name Match", "Fraud")
graph.add_edge("Fraud", "Review")
graph.add_edge("Review", "KYC")
graph.add_edge("KYC", "Loan")
graph.add_edge("Loan", END)

workflow = graph.compile()