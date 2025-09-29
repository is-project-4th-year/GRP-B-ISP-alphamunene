# backend/db_api.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os, shutil, sqlite3
from pathlib import Path

router = APIRouter()

BACKEND_DIR = Path(__file__).parent
DATA_DB = BACKEND_DIR / "current_data.db"    # active DB file used by SQL executor
# add near top of db_api.py or new file rag_api.py

from . import rag

router_rag = APIRouter()

@router_rag.post("/api/rebuild_schema_index")
def rebuild_schema_index():
    try:
        rag.build_index()
        return {"ok": True, "message": "Schema index rebuilt."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/upload_db")
async def upload_db(file: UploadFile = File(...)):
    """Upload a SQLite file and set it as the active DB."""
    if not file.filename.lower().endswith((".db", ".sqlite")):
        raise HTTPException(status_code=400, detail="Only .db or .sqlite files accepted.")
    target = BACKEND_DIR / f"uploaded_{file.filename}"
    with open(target, "wb") as f:
        content = await file.read()
        f.write(content)
    # quick validation: can we open it?
    try:
        conn = sqlite3.connect(str(target))
        conn.execute("PRAGMA schema_version;")
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid SQLite file: {e}")
    # set as active DB (overwrite previous)
    if DATA_DB.exists():
        DATA_DB.unlink()
    shutil.copyfile(target, DATA_DB)
    return {"message": f"Uploaded and set {file.filename} as active database."}


@router.post("/api/connect_db")
async def connect_db(conn_str: str = Form(...)):
    """
    Accept a connection string for external DBs.
    For security and simplicity, only accept SQLite local paths or
    store connection string in a config (production needs secrets manager).
    """
    # Only accept sqlite file path (raw path or URL not supported here)
    # In production you'd validate host/credentials and create a secure connection config.
    if conn_str.startswith("sqlite:///") or conn_str.endswith(".db") or conn_str.endswith(".sqlite"):
        # try to open
        path = conn_str.replace("sqlite:///", "")
        if not os.path.exists(path):
            raise HTTPException(status_code=400, detail="SQLite file path not found on server.")
        # copy to active DB
        if DATA_DB.exists():
            DATA_DB.unlink()
        shutil.copyfile(path, DATA_DB)
        return {"message": "Connected to provided SQLite DB file."}
    else:
        # Optionally support other DB types: store connection string for later use
        # WARNING: storing DB credentials requires secure storage.
        return {"message": "Connection string received. For this demo only SQLite file paths are accepted."}
