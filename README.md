# 🤖 AI Loan Processing System

An end-to-end **AI-powered loan processing platform** that combines traditional loan-processing workflows with **Generative AI, LangChain, RAG, FAISS, OCR, KYC verification, fraud detection, AI-based decisioning, and Model Context Protocol (MCP)**.

The system is designed to demonstrate how modern AI technologies can be integrated into a financial-services workflow to automate document processing, customer verification, risk analysis, loan decisions, and policy-based customer assistance.

---

## 🚀 Project Overview

The **AI Loan Processing System** simulates a complete digital loan-processing journey:

```text
Customer
   │
   ▼
Customer Registration
   │
   ▼
Loan Application
   │
   ▼
Document Upload
   │
   ▼
OCR Processing
   │
   ▼
KYC Verification
   │
   ▼
Fraud Detection
   │
   ▼
AI Loan Decision
   │
   ▼
Loan Report / Dashboard
   │
   ▼
AI Loan Assistant
   │
   ├── RAG / Knowledge Base
   └── MCP Loan Policy Tools
```

The application also provides an AI Loan Assistant that can answer questions about a customer's loan application and retrieve relevant loan-policy information.

---

# ✨ Key Features

## 🧑 Customer Management

* Customer registration
* Customer information management
* Existing customer lookup
* Customer-specific loan information
* Customer/application identification
* Authorization-aware application access

## 💰 Loan Processing

* Loan application workflow
* Loan amount and income capture
* Loan type handling
* Credit-score-based assessment
* Application status tracking
* Loan history
* Loan reports
* Application tracker

## 📄 Document Processing

* PAN document processing
* Aadhaar document processing
* OCR-based document extraction
* Document preprocessing
* OCR confidence handling
* Extracted-document information management

> **Security:** Actual PAN/Aadhaar image files are not stored in the GitHub repository.

## 🔐 KYC Verification

The KYC workflow evaluates:

* Name matching
* PAN verification
* Aadhaar verification
* Date-of-birth matching
* Similarity score
* Overall KYC verification status

Example:

```text
KYC Status: VERIFIED
Name Match: True
PAN Match: True
Aadhaar Match: True
DOB Match: True
Similarity Score: 100%
```

## 🛡️ Fraud Detection

The fraud-processing workflow evaluates application information and produces:

* Fraud status
* Fraud score
* Risk level
* Fraud-analysis reason

Example:

```text
Fraud Status: NO_FRAUD
Risk Level: LOW
Fraud Score: 8.5
```

## 🧠 AI Loan Decisioning

The system combines loan-processing information to generate an AI-assisted decision.

Decision inputs can include:

* Credit score
* KYC status
* Fraud status
* Income
* Loan information
* Risk level
* Loan-policy rules

Example:

```text
Decision: APPROVED
Risk Level: MEDIUM
```

The system also provides an explanation for the decision rather than returning only a binary result.

---

# 🧠 Generative AI Capabilities

The project integrates several modern AI technologies.

## LangChain

LangChain is used to structure the AI application around:

* LLM interaction
* Agents
* Tools
* Prompt management
* Retrieval
* Application state
* AI services

Relevant implementation areas include:

```text
langchain_app/
├── agent.py
├── agent_service.py
├── agent_tools.py
├── chains.py
├── chat_service.py
├── context.py
├── embeddings.py
├── llm.py
├── memory.py
├── prompts.py
├── question_router.py
├── rag_tool.py
├── retriever.py
├── state.py
├── tools.py
└── vector_store.py
```

---

# 📚 RAG — Retrieval Augmented Generation

The project contains a dedicated loan-policy knowledge base.

Example knowledge sources include:

```text
Knowledge_Base/
├── ai_decision.txt
├── car_loan.txt
├── credit_policy.txt
├── documents.txt
├── education_loan.txt
├── eligibility.txt
├── emi.txt
├── faq.txt
├── fraud_policy.txt
├── home_loan.txt
├── interest_rates.txt
├── kyc.txt
├── kyc_guidelines.txt
├── loan_policy.txt
├── ocr.txt
└── personal_loan.txt
```

The RAG pipeline enables the AI assistant to retrieve relevant policy information before generating an answer.

Example questions:

```text
What is the maximum LTV for a car loan?

What is the maximum tenure for a car loan?

Why is my credit score important for my loan?

What documents are required for KYC?
```

---

# 🗂️ FAISS Vector Store

FAISS is used for vector-based similarity search.

```text
faiss_index/
├── index.faiss
└── index.pkl
```

The workflow is approximately:

```text
Loan Policy Documents
        │
        ▼
Document Loading
        │
        ▼
Text Processing
        │
        ▼
Embeddings
        │
        ▼
FAISS Vector Store
        │
        ▼
Retriever
        │
        ▼
Relevant Context
        │
        ▼
LLM
        │
        ▼
AI Response
```

---

# 🔌 MCP Integration

The project also integrates **Model Context Protocol (MCP)** to expose loan-policy functionality as tools that can be consumed by an AI client.

### MCP Architecture

```text
                  AI Loan Assistant
                         │
                         ▼
                   MCP Client
                         │
                         │ Tool Calls
                         ▼
                ┌──────────────────┐
                │   MCP Server     │
                │ Loan Policy      │
                │ Tools            │
                └────────┬─────────┘
                         │
                         ▼
                  Loan Policy Data
```

Current MCP components:

```text
mcp_client/
├── loan_policy_mcp.py
├── loan_policy_tools.py
├── mcp_groq_agent.py
├── test_loan_policy_mcp.py
├── test_mcp_bridge.py
├── test_mcp_client.py
├── test_mcp_policy_helpers.py
└── test_mcp_tool_call.py

mcp_server/
└── loan_policy_server.py
```

The MCP layer allows the AI application to interact with externalized loan-policy capabilities through structured tools instead of embedding every capability directly inside the LLM prompt.

---

# 💬 AI Loan Assistant

The Streamlit-based AI Loan Assistant provides a conversational interface for customers to ask questions about their loan application.

Example interactions:

```text
What is my name?

What is my email?

Show my customer information.

What is my loan amount?

What is my loan status?

Show my complete loan details.

What is my KYC status?

What is my fraud risk?

Why was my loan approved?

What is my credit score?

Why is my credit score important for my loan?

What is the maximum LTV for a car loan?

What is the maximum tenure for a car loan?
```

The assistant can combine:

```text
Customer Context
       +
Loan Application Data
       +
KYC Results
       +
Fraud Results
       +
RAG Knowledge
       +
MCP Loan Policy Tools
       ↓
AI Loan Assistant
```

---

# 🖥️ Application Modules

The Streamlit application contains multiple workflow pages.

```text
pages/
├── 0_Existing_Customer.py
├── 1_customer_registration.py
├── 2_loan_application.py
├── 3_upload_documents.py
├── 4_OCR_Processing.py
├── 5_KYC_Verification.py
├── 6_Fraud_Detection.py
├── 7_AI_Loan_Decision.py
├── 8_Loan_Report.py
├── 9_Dashboard.py
├── 10_Loan_History.py
├── AI_Loan_Assistant.py
├── Admin_Dashboard.py
└── application_tracker.py
```

---

# 🏗️ High-Level Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│                                                          │
│ Customer Registration │ Loan Application │ Dashboard    │
│ OCR │ KYC │ Fraud │ Decision │ Reports │ AI Assistant   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  Application Services                     │
│                                                          │
│ Customer │ Loan │ OCR │ KYC │ Fraud │ Decision │ Tracker │
└──────────────────────────┬───────────────────────────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        ┌─────────┐   ┌──────────┐   ┌─────────────┐
        │Database │   │ RAG/FAISS│   │ MCP Server  │
        │         │   │          │   │             │
        │Customer │   │Knowledge │   │Loan Policy  │
        │Loan     │   │Base      │   │Tools        │
        │KYC      │   │          │   │             │
        │Fraud    │   │Retriever │   │             │
        └─────────┘   └────┬─────┘   └──────┬──────┘
                           │                │
                           └───────┬────────┘
                                   ▼
                             ┌───────────┐
                             │    LLM    │
                             │ AI Agent  │
                             └───────────┘
```

---

# 🛠️ Technology Stack

| Area                      | Technology                            |
| ------------------------- | ------------------------------------- |
| Language                  | Python                                |
| UI                        | Streamlit                             |
| LLM Application Framework | LangChain                             |
| Generative AI             | Gemini / supported LLM providers      |
| Agent Framework           | LangChain Agents                      |
| RAG                       | Retrieval Augmented Generation        |
| Vector Database           | FAISS                                 |
| Embeddings                | LangChain-compatible embedding models |
| Protocol                  | Model Context Protocol (MCP)          |
| OCR                       | EasyOCR / OCR processing              |
| Database                  | SQLite / repository-based persistence |
| Testing                   | Python test scripts                   |
| Environment               | Python virtual environment            |
| Version Control           | Git / GitHub                          |

---

# 📁 Project Structure

```text
AI-Loan-Processing-System/
│
├── Knowledge_Base/
├── database/
├── faiss_index/
├── langchain_app/
├── mcp_client/
├── mcp_server/
├── ocr/
├── pages/
├── services/
├── src/
├── utils/
│
├── app.py
├── streamlit_app.py
├── config.py
├── init_db.py
├── build_vector_db.py
│
├── check_stages.py
├── cleanup_duplicates.py
│
├── test_agent.py
├── test_customer.py
├── test_db.py
├── test_documents.py
├── test_get_documents.py
├── test_helper.py
├── test_import.py
├── test_loans.py
├── test_ocr.py
│
└── .gitignore
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/mdfaiz7777-tech/AI-Loan-Processing-System.git
cd AI-Loan-Processing-System
```

Create and activate a Python virtual environment:

### Windows

```powershell
python -m venv mcp_env
.\mcp_env\Scripts\Activate.ps1
```

Install project dependencies according to the project's dependency configuration.

---

# 🔐 Environment Configuration

API keys and secrets must be provided through environment variables.

Example:

```text
GOOGLE_API_KEY=<your-api-key>
GROQ_API_KEY=<your-api-key>
```

Do **not** commit API keys, credentials, `.env` files, customer documents, PAN images, Aadhaar images, or other sensitive information.

The repository's `.gitignore` excludes sensitive/local files such as:

```text
.env
*.db
*.sqlite3
temp/
pan.png
aadhar.png
aadhaar.png
```

---

# ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The application will open in the local browser.

The AI Loan Assistant can then be used to test customer-specific and policy-related questions.

---

# 🔌 Running the MCP Server

The project contains an MCP loan-policy server under:

```text
mcp_server/loan_policy_server.py
```

The MCP development tools can be used to run and inspect the server during development.

The MCP Inspector can be used to verify:

* Server connectivity
* Available tools
* Tool schemas
* Tool calls
* Tool responses

---

# 🧪 Testing

The project includes multiple test scripts covering areas such as:

```text
Customer
Database
Documents
OCR
Loans
Agents
MCP
Helpers
Imports
```

Examples:

```bash
python test_customer.py
python test_db.py
python test_documents.py
python test_ocr.py
python test_agent.py
```

MCP-specific tests are available under:

```text
mcp_client/
```

---

# 🔒 Security Considerations

This project handles workflows involving sensitive financial/customer information.

The repository follows these principles:

* Do not commit PAN/Aadhaar images.
* Do not commit `.env` files.
* Do not commit API keys or credentials.
* Keep generated customer documents outside Git.
* Use masked customer information when demonstrating the application.
* Use synthetic/test customer data for public demonstrations.
* Separate application logic from sensitive customer data.

**Important:** This project is intended as a learning/portfolio implementation and should not be considered production-ready financial software without additional security, compliance, privacy, audit, and infrastructure controls.

---

# 📊 Current Implementation Status

| Capability                     | Status         |
| ------------------------------ | -------------- |
| Streamlit UI                   | ✅ Implemented  |
| Customer Registration          | ✅ Implemented  |
| Loan Application               | ✅ Implemented  |
| Document Processing            | ✅ Implemented  |
| OCR                            | ✅ Implemented  |
| KYC Verification               | ✅ Implemented  |
| Fraud Detection                | ✅ Implemented  |
| AI Loan Decision               | ✅ Implemented  |
| Loan Reports                   | ✅ Implemented  |
| Loan History                   | ✅ Implemented  |
| AI Loan Assistant              | ✅ Implemented  |
| LangChain                      | ✅ Integrated   |
| RAG                            | ✅ Integrated   |
| FAISS                          | ✅ Integrated   |
| MCP Server                     | ✅ Integrated   |
| MCP Client                     | ✅ Integrated   |
| Loan Policy Tools              | ✅ Integrated   |
| Authentication                 | 🔄 Enhancement |
| Persistent Conversation Memory | 🔄 Enhancement |
| Multiple Chat Sessions         | 🔄 Enhancement |
| React Frontend                 | 🔄 Roadmap     |
| AWS DynamoDB                   | 🔄 Roadmap     |
| Production Deployment          | 🔄 Roadmap     |

---

# 🗺️ Future Roadmap

The next evolution of the system is planned around a more production-oriented architecture.

### Phase 1 — Authentication

* Login/sign-up
* User identity
* Session management
* Role-based access
* Customer/admin separation

### Phase 2 — Conversational Memory

* Short-term conversation memory
* Long-term customer context
* Session-based memory
* Multiple conversations per user
* Conversation history

### Phase 3 — AWS Integration

Planned components:

```text
React Frontend
       │
       ▼
API Layer
       │
       ├── Authentication
       ├── Loan Services
       ├── AI Assistant
       └── MCP Integration
       │
       ▼
AWS Services
       │
       ├── DynamoDB
       ├── Authentication
       ├── Object Storage
       └── Email / Notifications
```

### Phase 4 — React Frontend

Move from the current Streamlit-focused UI toward a dedicated React application supporting:

* Login
* Sign-up
* Customer dashboard
* Multiple chat sessions
* Loan dashboard
* Application tracking
* AI Loan Assistant
* Admin dashboard

### Phase 5 — Production AI Architecture

Future enhancements include:

* Better agent orchestration
* Guardrails
* Structured tool calling
* Improved RAG evaluation
* Observability
* Prompt/version management
* Model fallback
* Automated evaluation
* Audit logging

---

# 🎯 Project Objective

The primary objective of this project is to demonstrate how **Generative AI and modern AI engineering techniques can be integrated into a realistic financial-services workflow**.

The project brings together:

```text
Traditional Software Engineering
             +
Data Processing
             +
OCR
             +
KYC
             +
Fraud Detection
             +
AI Decisioning
             +
LangChain
             +
RAG
             +
FAISS
             +
MCP
             +
Conversational AI
```

into a single end-to-end application.

---

# 👨‍💻 Author

**Mohamed Faiz**

IT / Software Testing Professional | AI & Generative AI Enthusiast

This project represents an ongoing exploration of:

* Generative AI
* LangChain
* RAG
* AI Agents
* MCP
* Intelligent Document Processing
* Financial AI workflows
* AI-assisted decision systems

---

# ⚠️ Disclaimer

This project is created for **educational, demonstration, and portfolio purposes**.

It does not constitute financial advice, credit advice, lending advice, or a production banking/financial system.

All customer information used for demonstrations should be synthetic or appropriately anonymized.

---

⭐ If you find this project useful or interesting, consider starring the repository.
