# backend/rag.py
import os, pickle, textwrap, sqlite3
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import openai

BASE = Path(__file__).parent
INDEX_PATH = BASE / "schema.index"
META_PATH = BASE / "schema.meta.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"
embedder = None
index = None
meta = []

ACTIVE_DB = BASE / "current_data.db"
DEFAULT_DB = BASE / "sample.db"
DB_TO_INTROSPECT = ACTIVE_DB if ACTIVE_DB.exists() else DEFAULT_DB

def ensure_embedder():
    global embedder
    if embedder is None:
        embedder = SentenceTransformer(MODEL_NAME)
    return embedder

def introspect_schema(db_path=None):
    """Return a list of schema strings like 'employees(id, name, department_id, salary)'."""
    db = db_path or str(DB_TO_INTROSPECT)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    schemas = []
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = [r[1] for r in cur.fetchall()]
        schemas.append(f"{t}({', '.join(cols)})")
    conn.close()
    return schemas

def build_index():
    global index, meta
    ensure_embedder()
    meta = introspect_schema()
    vectors = embedder.encode(meta)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)
    return True

def load_index():
    global index, meta
    if INDEX_PATH.exists() and META_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "rb") as f:
            meta = pickle.load(f)
    else:
        build_index(); load_index()

def retrieve_schema_context(query, k=3):
    load_index()
    ensure_embedder()
    qv = embedder.encode([query])
    D, I = index.search(qv, k)
    ctx = [meta[i] for i in I[0] if i < len(meta)]
    return ctx

def generate_sql(user_query, schema_ctx):
    """
    Prefer OpenAI if key is present; otherwise use a template heuristic.
    You can replace this with a local LLM call (transformers/generation) if desired.
    """
    prompt = textwrap.dedent(f"""You are an AI assistant that converts natural language questions into SQL.
Schema:
{('\\n'.join(schema_ctx))}
User question:
{user_query}
SQL:
""")
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        openai.api_key = api_key
        resp = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=200, temperature=0)
        return resp.choices[0].text.strip()
    # fallback (very small heuristics)
    uq = user_query.lower()
    if "average" in uq and "salary" in uq:
        return "SELECT AVG(salary) FROM employees;"
    if "employees" in uq and "marketing" in uq:
        return "SELECT name FROM employees WHERE department_id = 2;"
    return "SELECT * FROM employees LIMIT 50;"
