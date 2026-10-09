# 🤖 AI Loan Processing System

An end-to-end **AI-assisted loan processing platform**: customer onboarding,
document OCR, KYC verification, fraud screening, an **explainable rule-based
credit decision**, PDF reports, dashboards and a conversational
**AI Loan Assistant** built with **LangGraph, RAG (FAISS) and the Model
Context Protocol (MCP)**.

> Educational / portfolio project — not a production lending system.

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
git clone https://github.com/<your-username>/AI-Loan-Processing-System.git
cd AI-Loan-Processing-System
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
