# 📊 Text-to-SQL AI Assistant

An intelligent **Text-to-SQL Query Generator** powered by **Google Gemini 3.0 (Flash)**.
It allows non-technical users to query a database using natural language, featuring **AI-driven visualization**, **schema-aware RAG**, and a **clean SaaS-style UI**.

---

## 🚀 Features
- **Natural Language Querying**: Converts specific questions (e.g. *"Show top 5 products"*) into safe SQL.
- **AI Visualization**: Automatically suggests and renders Charts (Bar, Line, etc.) based on data results.
- **RAG Engine** (Retrieval-Augmented Generation): Context-aware querying using Schema and Keyword search.
- **Mock Data Seeding**: Includes a generator for 19 realistic tables (Users, Orders, Logistics, etc.).
- **Modern Stack**: Built with **FastAPI**, **SQLite**, **Docker**, and **Clean Architecture**.

---

## 🛠️ Prerequisites
- **Python 3.10+** (for local run)
- **Docker & Docker Compose** (for container run)
- **Google Gemini API Key** (Get one at [aistudio.google.com](https://aistudio.google.com/))

---

## ⚙️ Setup & Installation

### Option A: Run with Docker (Recommended) 🐳

1.  **Clone the repository**
2.  **Create `.env` file**:
    ```bash
    cp .env.example .env
    # Edit .env and set GOOGLE_API_KEY=your_key_here
    ```
3.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
    - The server will start at `http://localhost:8000`.
    - It handles database initialization and dependency management automatically.

### Option B: Run Locally (Python) 🐍

1.  **Create `.env` file**:
    ```bash
    cp .env.example .env
    # Edit .env and set GOOGLE_API_KEY=your_key_here
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Initialize Database**:
    ```bash
    python init_db.py
    ```
4.  **Start Server**:
    ```bash
    python server.py
    # OR 
    uvicorn server:server --reload
    ```
    - Access at `http://localhost:8000`.

---

## 📂 Project Structure

```
texttosql/
├── app/
│   ├── domain/         # Interfaces & Models (Clean Arch)
│   ├── infrastructure/ # Implementations (Gemini, SQLite)
│   └── services/       # Business Logic (RAG, Validator)
├── data/               # SQLite database storage
├── static/             # CSS, JS, Assets
├── templates/          # Jinja2 HTML Templates
├── Dockerfile
├── docker-compose.yml
├── init_db.py          # Database Seeding Script
├── server.py           # FastAPI Entrypoint
└── requirements.txt
```

## 🧪 Usage Examples

Go to the web UI and try these queries:
- *"Show me the top 5 most expensive products"*
- *"List total sales per month"*
- *"How many orders were cancelled?"*
- *"Compare sales vs profit by product category"* (Triggers Multi-Series Chart)

---

## 🛠️ Tech Stack
- **Backend**: FastAPI, Uvicorn, Pydantic
- **AI/LLM**: Google GenAI SDK (Gemini 2.0 Flash)
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS, Chart.js
- **Ops**: Docker, Docker Compose

---
**Author**: Antigravity Team
**License**: MIT
