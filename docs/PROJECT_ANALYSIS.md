# Project Analysis — AI Loan Processing System

This document explains how the system works end to end, the algorithms
and libraries behind each feature, the defects found in the original
code base, and the changes made to fix them.

---

## 1. How the system works

```text
Login (app.py, bcrypt)
   │
   ├── Staff (admin / officer)
   │     1 Customer Registration ── validators (PAN regex, Aadhaar Verhoeff, phone, age)
   │     2 Loan Application ─────── live EMI / FOIR preview
   │     3 Upload Documents ─────── extension + size + magic-byte checks
   │     4 OCR Processing ───────── OpenCV → Tesseract → EasyOCR fallback → regex extraction
   │     5 KYC Verification ─────── fuzzy name match + PAN/Aadhaar/DOB equality → score
   │     6 Fraud Detection ──────── weighted rule scoring → LOW / MEDIUM / HIGH (persisted)
   │     7 AI Loan Decision ─────── deterministic policy engine → LLM writes explanation
   │     8 Loan Report ──────────── ReportLab PDF (masked identifiers)
   │     9 Dashboards ───────────── SQLite aggregates + Streamlit charts
   │
   └── Customer
         AI Loan Assistant ─────── keyword router → DB tools / MCP policy / LangGraph + Groq
         Application Tracker / Loan History (own applications only)
```

### Layers

| Layer | Folder | Responsibility |
|---|---|---|
| UI | `app.py`, `pages/` | Streamlit multipage app; every page calls `require_login()` / `require_staff()` |
| Services | `services/`, `src/` | KYC, fraud, decision engine, decision orchestration, tracker, PDF report |
| AI | `langchain_app/` | LangGraph agent, tools, RAG chain, question router |
| MCP | `mcp_server/`, `mcp_client/` | Loan-policy tools exposed over Model Context Protocol (stdio) |
| OCR | `ocr/`, `src/ocr.py`, `src/preprocessing.py` | Image preprocessing, OCR, field extraction |
| Data | `database/` | SQLite repositories (parameterised queries), schema + migrations |
| Shared | `utils/`, `config.py` | Validation, masking, uploads, sessions, env-based configuration |

---

## 2. Functionality, algorithms and libraries

### 2.1 Authentication & authorisation
- **bcrypt** password hashing with per-password salt (`langchain_app/auth.py`).
- Roles: `admin`, `officer` (staff pages) and `customer` (assistant, tracker, own history).
- Ownership check `is_application_authorized(application_id, customer_id)` before any
  customer-scoped data is returned, including inside the LLM tools.

### 2.2 Registration validation (`utils/validators.py`)
- **PAN**: `^[A-Z]{3}[ABCEFGHLJPT][A-Z][0-9]{4}[A-Z]$` — the 4th character is the holder type.
- **Aadhaar**: 12 digits, first digit 2–9, and the **Verhoeff checksum** (dihedral group D5
  multiplication + permutation tables). Detects every single-digit error and every adjacent
  transposition — exactly the errors OCR and typing introduce.
- Indian mobile number, email, minimum age 18.

### 2.3 OCR pipeline (`src/preprocessing.py`, `src/ocr.py`, `ocr/ocr_service.py`)
1. **OpenCV** preprocessing: resize → grayscale → bilateral filter (PAN) or
   Non-Local-Means denoising + **CLAHE** contrast (Aadhaar) → adaptive Gaussian threshold →
   morphological close → sharpening kernel.
2. **Tesseract** (`pytesseract`) with several page-segmentation modes (`--psm 6/4/11`);
   the mode with the highest mean word confidence wins (early exit at ≥ 70 %).
3. **EasyOCR** (deep-learning CRNN) fallback when Tesseract confidence is below 50–60 %.
4. **Regex + heuristics** to extract PAN number, Aadhaar number, DOB and name
   (name candidates near the DOB line are scored by distance and word shape).

### 2.4 KYC (`services/kyc_service.py`)
- Name similarity: `difflib.SequenceMatcher` ratio, also on token-sorted names
  (so "KUMAR RAVI" = "RAVI KUMAR"); both documents must reach 85 %.
- PAN, Aadhaar and DOB (normalised to ISO dates) compared with the registered profile.
- 4 checks × 25 points → `VERIFIED` (100), `PARTIAL` (75) or `MANUAL_REVIEW`.

### 2.5 Fraud screening (`src/fraud_agent.py`)
Weighted rule scoring (≥ 70 HIGH, ≥ 30 MEDIUM, else LOW):

| Signal | Points |
|---|---|
| Missing fields on PAN / Aadhaar | +30 each |
| OCR confidence < 40 % | +40 |
| OCR confidence 40–55 % with missing fields | +10 |
| Extracted PAN fails format check | +20 |
| Extracted Aadhaar fails Verhoeff checksum | +25 |
| Document PAN / Aadhaar ≠ registered value | +40 each |
| Name differs between PAN and Aadhaar (< 70 %) | +20 |
| DOB differs between PAN and Aadhaar | +20 |
| ≥ 3 other applications by the customer | +30 |
| Loan amount > 10 × annual income | +15 |

Results are stored in `fraud_results` so the assistant reports real findings.

### 2.6 Loan decision (`services/decision_engine.py`)
Deterministic, auditable rules derived from `Knowledge_Base/`:

- **EMI** (reducing balance): `EMI = P·r·(1+r)^n / ((1+r)^n − 1)`, r = monthly rate.
- **FOIR** (Fixed Obligation to Income Ratio) = EMI / monthly income.
  > 50 % → manual review, > 65 % → reject.
- **Maximum eligible amount**: inverse EMI formula at 50 % FOIR.
- Credit score: < 650 reject; 650–749 or below the product minimum → manual review.
- Product minimums (credit score, income, tenure, reference rate) per loan type.
- KYC must be `VERIFIED` for approval; HIGH fraud → reject; MEDIUM fraud → review.

The LLM (Gemini, falling back to Groq) only writes a customer-friendly explanation of
the already-made decision. With no API key the rule summary is used, so the decision
flow never depends on an external service.

### 2.7 AI Loan Assistant (`langchain_app/`)
- **Router** (`question_router.py`): whole-word keyword matching sends factual questions
  directly to DB tools or MCP policy tools (no LLM tokens); reasoning questions
  ("why", "explain", "should I"…) go to the agent.
- **LangGraph** ReAct-style loop: `agent` node (Groq `llama-3.3-70b-versatile` with bound
  tools) ↔ `ToolNode`, ending when the model stops calling tools.
- **Tools** read the customer/application ID from `RunnableConfig` (set by the
  authenticated session — the LLM cannot choose another customer) and mask PII.

### 2.8 RAG (`langchain_app/vector_store.py`, `retriever.py`, `chains.py`)
- 16 policy text files → `RecursiveCharacterTextSplitter` (500 chars, 50 overlap)
  → **sentence-transformers/all-MiniLM-L6-v2** embeddings (normalised)
  → **FAISS** flat index (cosine via inner product on normalised vectors), top-k = 5.
- Answering: exact regex extraction for LTV / tenure / vehicles / car-loan eligibility,
  otherwise local **FLAN-T5-small** generation constrained to the retrieved context.

### 2.9 MCP (`mcp_server/`, `mcp_client/`)
- **FastMCP** server over stdio exposing `search_loan_policy`, `get_car_loan_ltv`,
  `get_car_loan_tenure`, `get_eligible_car_vehicles`.
- Exact tools now parse `Knowledge_Base/car_loan.txt` (`policy_facts.py`) instead of
  returning hard-coded strings.
- Client: `langchain-mcp-adapters` `MultiServerMCPClient`; if the server is unreachable
  the assistant falls back to the in-process RAG chain.

### 2.10 Persistence
SQLite with `sqlite3.Row`, parameterised SQL everywhere (no SQL injection),
`PRAGMA foreign_keys = ON`, indexes on every `application_id` lookup, idempotent
`init_db()` with column migrations.

---

## 3. Defects found in the original code

### Critical — wrong results or crashes
| # | Problem | Where |
|---|---|---|
| 1 | Loan approval was decided by an LLM reading rules from a prompt; the decision was then parsed by searching the text for "APPROVED" (an explanation saying "not APPROVED" counted as approved). Loan amount vs income was never actually checked. | `pages/7_AI_Loan_Decision.py`, `src/decision_agent.py` |
| 2 | Fraud results were never saved; `fraud_results` was filled by a seed script with fake `NO_FRAUD / LOW / 8.5` for every application, which the assistant then reported to customers. | `database/seed_fraud_results.py` |
| 3 | Indentation bug: the Aadhaar low-confidence branch was attached to the confidence `if` chain, so high-confidence Aadhaar scans were flagged and PAN always got +10. Two f-strings were missing a closing parenthesis. | `src/fraud_agent.py` |
| 4 | MEDIUM fraud risk set `fraud = True`. | `src/fraud_agent.py` |
| 5 | `verify_kyc` crashed (`None.upper()`) whenever OCR missed a PAN or Aadhaar number. | `services/kyc_service.py` |
| 6 | Aadhaar extraction returned the truthy string `"Not Found"`, so incomplete scans were marked `SUCCESS`. | `src/ocr.py` |
| 7 | Tracker turned every non-approved decision (including manual review) into `REJECTED / HIGH`; OCR, fraud and decision stages were never recorded. | `services/tracker_service.py` |
| 8 | Loan Report page imported `reports.loan_report`, which was never committed (`reports/` is git-ignored) → `ModuleNotFoundError`. | `pages/8_Loan_Report.py` |
| 9 | `fraud_results` table was missing from `schema.py`; `tools.get_fraud_info` read a `customer_id` key that did not exist. | `database/schema.py` |
| 10 | Two different database files (`loan_kyc.db` in `config.py`, `loan_system.db` in `database.py`). | `config.py` |
| 11 | `streamlit_app.py` (the README's start command) imported `calculate_kyc_score`, which does not exist, plus a whole legacy layer (`src/auth.py`, `src/workflow.py`, …) writing to columns that no longer exist. | legacy files |
| 12 | `vector_store.py` read `knowledge_base` but the folder is `Knowledge_Base` → index build fails on Linux/macOS. | `langchain_app/vector_store.py` |
| 13 | Existing Customer page crashed with `dict(None)` for an unknown PAN; its "Customer not found" `else` was attached to the wrong `if`. | `pages/0_Existing_Customer.py` |
| 14 | Dashboard counted `'MANUAL REVIEW'` while other code wrote `'MANUAL_REVIEW'`; "fraud cases" counted any HIGH *loan* risk. | `database/dashboard_repository.py` |

### Security & privacy
| # | Problem |
|---|---|
| 15 | No page except Home checked login — every page (dashboards, PAN lookup, history by customer ID) was reachable directly by URL. |
| 16 | File upload wrote the client-supplied filename to disk (path traversal, e.g. `../../app.py`), no size or content checks. |
| 17 | Module-level "current context" fallback in the agent tools would be shared by all concurrent Streamlit sessions. |
| 18 | OCR tool returned full PAN and Aadhaar numbers to the LLM and the chat; registration page echoed full PAN/Aadhaar with `st.json`. |
| 19 | Real-looking PAN / Aadhaar / phone numbers committed in test scripts and code comments. |
| 20 | Hard-coded password (`Loan@123`) in `database/create_user.py`. |
| 21 | Customer IDs, questions and full answers `print`ed to stdout; raw exception text shown to customers. |
| 22 | Script `cleanup_duplicates.py` deleted hard-coded document IDs from whatever DB it ran against. |

### Engineering / portability
| # | Problem |
|---|---|
| 23 | No `requirements.txt` — the project could not be installed reproducibly. |
| 24 | Hard-coded Windows paths: `C:\Users\Dell\...\tesseract.exe`, `mcp_env\Scripts\python.exe`, `C:\Users\Dell\OneDrive\...\mcp.exe`. |
| 25 | `GROQ_API_KEY` missing → whole assistant crashed at import, even for DB-only questions. |
| 26 | FLAN-T5, FAISS and EasyOCR models loaded at import time; `matplotlib` imported for nothing. |
| 27 | "Tests" were ad-hoc scripts with hard-coded IDs, no assertions, not runnable in CI; one imported a function that doesn't exist. |
| 28 | Duplicate/dead modules (`chat_service.py`, `tools.py`, `memory.py`, `prompts.py`, `rag_tool.py`, `mcp_groq_agent.py` with model `"your-existing-groq-model"`, empty `report.py`, `validation.py`, `_init_.py` typo). |
| 29 | MCP server returned hard-coded policy strings that could silently drift from the documents. |
| 30 | Router keyword bugs: "What documents are required for KYC?" returned the customer's KYC status; "emi" matched inside "remind". |
| 31 | No input validation on PAN / Aadhaar / phone / age; no loan tenure captured, so no EMI could be computed. |

---

## 4. What was changed

| Area | Change |
|---|---|
| Decision engine | New `services/decision_engine.py`: EMI, FOIR, max-eligible amount, product policies, credit bands, explicit APPROVED / MANUAL_REVIEW / REJECTED with reasons and per-check results. LLM only explains. |
| Decision flow | New `services/decision_service.py` orchestrates fraud → rules → explanation → persist → tracker. |
| Fraud | Rewritten as pure `evaluate_fraud()` + persisted `fraud_check()`; 6 new identity-consistency signals; fixed indentation and MEDIUM≠fraud. |
| KYC | Null-safe, token-order-insensitive name matching, both documents must match, explicit failure remarks. |
| Validation | PAN holder-type regex, Aadhaar Verhoeff checksum, phone, email, age ≥ 18, duplicate checks. |
| Access control | `utils/session.py` guard on every page, staff vs customer roles, ownership checks in tracker / history / assistant tools. |
| Uploads | Server-side file names, extension whitelist, 5 MB limit, magic-byte verification, ID sanitisation. |
| PII | Shared masking helpers; masked in tools, OCR page, existing-customer page and PDF report; real-looking PII removed. |
| Loan application | Tenure capture + live EMI / FOIR / max-amount preview. |
| Reports | Implemented the missing PDF generator (`services/report_service.py`, ReportLab). |
| Assistant | Lazy LLM / agent / model loading, logging instead of prints, user-safe errors, MCP → local RAG fallback, whole-word router with policy-first rules. |
| MCP | Portable interpreter (`sys.executable`), facts parsed from the policy documents, single `call_policy_tool` API, `scripts/check_mcp.py` health check. |
| Database | Single env-configurable DB path, `fraud_results` in schema, `tenure_months` migration, indexes, foreign keys on, upsert for fraud results. |
| Config | `config.py` reads everything from env; Tesseract auto-detected; `.env.example`. |
| Quality | 92 pytest tests (unit + workflow integration on a temp DB), pyflakes-clean, GitHub Actions CI on Python 3.11 & 3.12. |
| Cleanup | ~40 dead / broken / unsafe files removed; `requirements.txt` + `requirements-dev.txt`. |

---

## 5. Known limitations / next steps

- Streamlit is single-process; no login rate limiting or account lockout yet.
- FAISS index is loaded with pickle deserialisation — only load indexes you built.
- OCR heuristics are tuned for clear, front-facing PAN / Aadhaar images; PDFs are
  accepted only for salary slips and bank statements.
- Product policies are code constants; a real system would version them in a database.
- Credit score is entered manually; a bureau integration would replace it.
