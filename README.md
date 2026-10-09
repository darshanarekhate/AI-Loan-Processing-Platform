# 🤖 AI Loan Processing Platform

[![tests](https://github.com/darshanarekhate/AI-Loan-Processing-Platform/actions/workflows/tests.yml/badge.svg)](https://github.com/darshanarekhate/AI-Loan-Processing-Platform/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![LangGraph](https://img.shields.io/badge/AI-LangGraph%20%7C%20RAG%20%7C%20MCP-purple)

An end-to-end **AI-assisted loan processing platform**: customer onboarding,
document OCR, KYC verification, fraud screening, an **explainable rule-based
credit decision**, PDF reports, dashboards and a conversational
**AI Loan Assistant** built with **LangGraph, RAG (FAISS) and the Model
Context Protocol (MCP)**.

> Educational / portfolio project — not a production lending system.

---

## 📖 What does it do? (in plain words)

A bank receives a loan request. Normally an officer must check the
customer's identity documents, look for signs of fraud, work out whether
the customer can afford the monthly payment, and then approve or reject.
This platform automates that journey:

| Step | What happens | Behind the scenes |
|---|---|---|
| 1. **Register customer** | Officer enters name, phone, PAN, Aadhaar, DOB | Inputs validated — PAN format, Aadhaar checksum, age ≥ 18, no duplicates |
| 2. **Loan application** | Choose loan type, amount, income, tenure, credit score | Live **EMI** preview and how much of the income it uses |
| 3. **Upload documents** | Upload PAN and Aadhaar card images | File type, size and real file content are checked |
| 4. **OCR** | Text is read from the card images | Image cleaned with OpenCV → read with Tesseract / EasyOCR → number, name, DOB extracted |
| 5. **KYC** | Is this really the registered person? | Name, PAN, Aadhaar and DOB on the cards compared with the registration |
| 6. **Fraud check** | Anything suspicious? | Risk score from blurry scans, missing fields, invalid numbers, mismatches, too many applications |
| 7. **Decision** | Approve, reject or send to an officer | Transparent bank rules decide; AI writes a friendly explanation |
| 8. **Report & dashboards** | Download a PDF, see statistics | ReportLab PDF with masked ID numbers; charts of approvals and risk |
| 9. **AI Loan Assistant** | Customer chats: *"Why was my loan rejected?"* | Answers from their own data and the bank's policy documents |

### Example: one application

```text
Car Loan · ₹5,00,000 · 60 months · income ₹80,000 · credit score 780

EMI at 10.5%  = ₹10,747  →  13% of income (limit 50%)   ✅
Credit score  = 780       →  ≥ 750 auto-approve band     ✅
KYC           = VERIFIED                                 ✅
Fraud risk    = LOW                                      ✅
Decision      = APPROVED  (risk LOW)
```

---

## ✨ Highlights

| | |
|---|---|
| 🧮 **Explainable decisions** | EMI, FOIR (EMI-to-income), credit bands, KYC and fraud rules decide; the LLM only *explains*. Every decision lists the checks that passed or failed. |
| 🛡️ **Fraud screening** | Weighted rules: OCR quality, missing fields, PAN format, **Aadhaar Verhoeff checksum**, document-vs-profile and cross-document consistency, application velocity. |
| 🪪 **KYC** | Fuzzy, order-insensitive name matching + PAN / Aadhaar / DOB verification. |
| 📄 **OCR** | OpenCV preprocessing → Tesseract (multi-PSM) → EasyOCR fallback → regex extraction. |
| 💬 **AI Loan Assistant** | Keyword router answers factual questions from the DB with zero LLM tokens; reasoning questions go through a LangGraph tool-calling agent (Groq Llama 3.3). |
| 📚 **RAG + MCP** | 16 policy documents in FAISS (MiniLM embeddings); policy tools served over MCP with automatic fallback to local RAG. |
| 🔐 **Security** | bcrypt, role-based page guards, per-customer authorisation inside LLM tools, PII masking, hardened uploads. |
| ✅ **Tested** | 92 pytest tests + GitHub Actions CI. |

---

## 🏗️ Architecture

```text
┌────────────────────────── Streamlit UI ──────────────────────────┐
│ Login · Registration · Application · Upload · OCR · KYC · Fraud  │
│ Decision · Report · Dashboards · Tracker · AI Loan Assistant     │
└───────────────┬───────────────────────────────┬──────────────────┘
                │                               │
        ┌───────▼────────┐              ┌───────▼─────────┐
        │   Services     │              │  AI Assistant   │
        │ KYC · Fraud    │              │ Router          │
        │ Decision engine│              │ LangGraph agent │
        │ Tracker · PDF  │              │ DB tools (masked)│
        └───────┬────────┘              └──┬───────────┬──┘
                │                          │           │
        ┌───────▼────────┐        ┌────────▼───┐  ┌────▼──────────┐
        │ SQLite         │        │ Groq LLM   │  │ MCP server    │
        │ repositories   │        │ Gemini     │  │ policy tools  │
        └────────────────┘        └────────────┘  │ FAISS RAG     │
                                                  └───────────────┘
```

A full walkthrough of every module, algorithm and library is in
**[docs/PROJECT_ANALYSIS.md](docs/PROJECT_ANALYSIS.md)**.

---

## 🧮 How a loan is decided

```text
fraud HIGH ............................ REJECTED
credit score < 650 .................... REJECTED
income < product minimum .............. REJECTED
EMI > 65% of income ................... REJECTED
KYC not VERIFIED ...................... MANUAL_REVIEW
fraud MEDIUM .......................... MANUAL_REVIEW
credit 650–749 / below product minimum  MANUAL_REVIEW
EMI 50–65% of income .................. MANUAL_REVIEW
otherwise ............................. APPROVED
```

`EMI = P·r·(1+r)^n / ((1+r)^n − 1)` using the product's reference rate.
The decision page also shows the **maximum affordable amount** at a 50 % FOIR.

| Product | Min credit | Min income | Tenure | Ref. rate |
|---|---|---|---|---|
| Home Loan | 700 | ₹25,000 | 5–30 yrs | 9.25 % |
| Car Loan | 680 | ₹25,000 | 12–84 mo | 10.50 % |
| Personal Loan | 720 | ₹20,000 | 12–60 mo | 14.25 % |
| Education Loan | 650 | co-applicant | 5–15 yrs | 10.50 % |

---

## ⚙️ Setup

**Requirements:** Python 3.11+, [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
installed (auto-detected on `PATH` or the default Windows folder).

```bash
git clone https://github.com/darshanarekhate/AI-Loan-Processing-Platform.git
cd AI-Loan-Processing-Platform
python -m venv .venv
```

Activate it (`.venv\Scripts\activate` on Windows, `source .venv/bin/activate` elsewhere), then:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your keys:

```text
GROQ_API_KEY=...      # AI Loan Assistant reasoning
GOOGLE_API_KEY=...    # decision explanations (optional)
```

Without keys the app still works: decisions use the rule summary and the
assistant answers factual and policy questions directly.

Initialise the database and create a staff login:

```bash
python init_db.py
```

```bash
python -m scripts.create_user --role admin --username admin --email admin@example.com
```

Customers get a login after they have an application:

```bash
python -m scripts.create_user --role customer --username ravi --email ravi@example.com --customer-id CUST-XXXXXXXX
```

(Re)build the policy vector index after editing `Knowledge_Base/`:

```bash
python build_vector_db.py
```

## ▶️ Run

```bash
streamlit run app.py
```

Log in as staff and follow the sidebar: **Registration → Loan Application →
Upload → OCR → KYC → Fraud → AI Decision → Report**.

### 💬 Try the AI Loan Assistant

Create a customer login for an application, log in as that customer and open
**AI Loan Assistant**:

| Question | Answered by |
|---|---|
| *What is my loan status?* | Database (instant, no AI cost) |
| *What is my KYC status?* / *What is my fraud risk?* | Database |
| *What is the maximum LTV for a car loan?* | MCP policy tool |
| *What documents are required for KYC?* | Policy documents (RAG) |
| *Why was my loan sent for manual review?* | LangGraph agent + Groq LLM |
| *Based on my income, should I choose a longer tenure?* | LangGraph agent + Groq LLM |

Customers only ever see their own application; PAN, Aadhaar and phone are masked.

MCP server check (optional):

```bash
python -m scripts.check_mcp
```

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
```

```bash
python -m pytest -q
```

The suite runs on a temporary database and needs no API keys or ML models.

---

## 📁 Project structure

```text
app.py                  Login + home
pages/                  Streamlit workflow pages
services/               decision_engine, decision_service, kyc_service,
                        tracker_service, report_service
src/                    fraud_agent, decision_agent (LLM explanation), OCR
langchain_app/          LangGraph agent, tools, router, RAG chain, embeddings
mcp_server/             FastMCP loan-policy server + policy fact parsers
mcp_client/             MCP client used by the assistant
database/               SQLite schema, migrations, repositories
utils/                  validators, masking, uploads, sessions, dates, names
Knowledge_Base/         Loan policy documents (RAG source)
faiss_index/            Prebuilt vector index
scripts/                create_user, check_mcp
tests/                  pytest suite
docs/                   Project analysis
```

---

## 🔒 Security notes

- Never commit `.env`, databases, uploads or real identity documents (all git-ignored).
- Use synthetic data for demos. The test identities are synthetic, checksum-valid numbers.
- `faiss_index/index.pkl` is loaded with pickle — only load indexes you built yourself.

---

## 👥 Credits

- **Original project:** [Mohamed Faiz](https://github.com/mdfaiz7777-tech/AI-Loan-Processing-System) —
  initial Streamlit workflow, OCR, KYC, LangChain/RAG assistant and MCP integration.
- **Improved version maintained by:** Darshana Rekhate — rule-based explainable decision
  engine (EMI/FOIR), fraud and KYC rework, Aadhaar/PAN validation, role-based access
  control, upload hardening, PII masking, PDF reports, MCP portability, test suite + CI,
  and bug fixes. See [docs/PROJECT_ANALYSIS.md](docs/PROJECT_ANALYSIS.md#3-defects-found-in-the-original-code).

## ⚠️ Disclaimer

For educational and demonstration purposes only. Not financial, credit or lending advice.
