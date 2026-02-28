# AI Document Automation Pipeline

An enterprise-ready, LLM-powered document processing pipeline designed to violently accelerate manual data entry workflows. Built using **LangChain**, **LangGraph**, and **FastAPI**, this project demonstrates the ability to ingest unstructured documents, automatically classify them, accurately extract key JSON fields, and generate AI summaries securely and quickly locally or via webhooks.

## 🚀 Features

* **Intelligent Document Ingestion:** Supports automated text extraction from PDF (`.pdf`), Word (`.docx`), and standard Text (`.txt`) documents.
* **LangGraph State Machine:** Implements a robust 4-node acyclic graph:
  1. `Extractor`: Cleans and normalizes raw text.
  2. `Classifier`: Uses LLM zero-shot classification to categorize the file (Invoice, Report, HR Form, etc.).
  3. `Field Extraction`: Dynamically routes to specialized extraction schemas based on precisely what type of document it is.
  4. `Summarizer`: Condenses the document into a strict 2-3 sentence overview.
* **Multi-LLM Support:** Interchangeable architecture natively supporting both **Google Gemini** and **Groq (Llama 3)**.
* **Modern Dashboard GUI:** A sleek, glassmorphic dark-theme analytics tracking interface to view live processed documents.
* **Webhook Web-listener:** Built-in REST API `POST /api/webhook/ingest` base-64 decoder for receiving external automated triggers.
* **Database Layer:** Fully asynchronous SQLAlchemy configuration powered by SQLite / PostgreSQL to maintain audit trails.

## 🛠️ Technology Stack
* **Backend Framework:** FastAPI, Uvicorn, SQLAlchemy
* **AI/LLM Framework:** LangChain, LangGraph, Groq API, Google GenAI
* **Database:** SQLite (default) / PostgreSQL
* **Frontend:** Vanilla JS, HTML5, CSS3 

---

## 💻 Local Setup & Installation

Follow these steps to run the pipeline flawlessly on your local machine.

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Configure Environment
Clone the repository, create a virtual environment, and install all necessary dependencies:

```bash
# Clone and enter the directory
git clone https://github.com/vineelsaireddy/AI-Document-Automation-Pipeline.git
cd AI-Document-Automation-Pipeline

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Depending on OS, might be `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. API Keys
You will need your own API keys to run the LLM operations.
1. Copy the example configuration to your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and assign either a **Groq API Key** or **Google Gemini API Key**. Make sure `LLM_PROVIDER` is set exactly to `"groq"` or `"gemini"` based on the key you use!

### 4. Run the Server
Launch the FastAPI development environment:

```bash
uvicorn app.main:app --reload --port 8000
```
* **Dashboard App:** Open `http://localhost:8000` in your web browser to access the graphical tool.
* **API Documentation:** Visit `http://localhost:8000/docs` to see the live Swagger UI.

---

## 🧪 How to Test
A folder named `/sample_docs/` is provided locally containing tests files:
- `sample_invoice.txt`
- `sample_hr_form.txt`
- `sample_report.txt`

Just click **Upload Document** on the beautiful UI Dashboard, drag any of these files in, and watch the pipeline automatically categorize, extract, and summarize them!
