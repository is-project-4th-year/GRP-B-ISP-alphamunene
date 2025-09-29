# Speech-to-SQL Website by Alpha Munene

This project is a full-stack prototype for a Speech-to-SQL website that uses RAG for database schema retrieval, an ASR engine (Whisper), and an LLM for SQL generation. The UI is styled in black/gray/white and includes authentication, signup/login, database connection, and data visualization endpoints.

## Features
- Frontend: Minimal HTML/CSS/JS UI 
- Backend: FastAPI (Python) with JWT auth
- ASR: Whisper wrapper (local)
- RAG: SentenceTransformers + FAISS for schema retrieval
- SQL execution: SQLite (local)
- Visualization: Frontend tables + simple chart (Chart.js)
- Offline-first: All embeddings and DB stored locally. LLM usage optional (OpenAI key or local model)

## Requirements
Python 3.10+ recommended.

Install dependencies:
```bash
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Quickstart (Local)
1. Initialize database and embeddings:
   ```bash
   python backend/db_init.py
   python backend/build_embeddings.py
   ```
2. Run the API server:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Open `http://localhost:8000/` in your browser.

## Notes
- There was a trial implementation For SQL generation, set `OPENAI_API_KEY` environment variable to use OpenAI or alternatively, configure LOCAL_LLM in `backend/rag.py` to use a local HF model.
- This is a prototype hence Fine-tuning, production hardening, and security review are required for deployment.
