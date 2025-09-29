from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from . import auth, asr, rag, db_models, sql_exec
from .token_and_signup import router as token_router
from .db_api import router as db_router
from .db_api import router_rag  # if you really have this in db_api

# ✅ First create the app
app = FastAPI(title="Speech-to-SQL API")

# ✅ Then include routers
app.include_router(db_router, prefix="/api")
app.include_router(router_rag, prefix="/api")   # make sure router_rag is actually defined
app.include_router(token_router, prefix="/api")

# ✅ Mount static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Root route
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Upload audio -> transcribe
@app.post("/api/upload_audio")
async def upload_audio(file: UploadFile = File(...), token: str = Depends(auth.get_current_user)):
    contents = await file.read()
    tmp_path = "temp_audio.wav"
    with open(tmp_path, "wb") as f:
        f.write(contents)
    text = asr.transcribe(tmp_path)
    return {"transcript": text}

# Natural language query -> SQL -> Execute
@app.post("/api/query_nl")
async def query_nl(payload: dict, token: str = Depends(auth.get_current_user)):
    user_text = payload.get("query")
    if not user_text:
        raise HTTPException(status_code=400, detail="Missing query")

    schema_ctx = rag.retrieve_schema_context(user_text)
    sql = rag.generate_sql(user_text, schema_ctx)

    try:
        rows, cols = sql_exec.execute_sql(sql)
    except Exception as e:
        return {"error": str(e), "sql": sql}

    return {"sql": sql, "rows": rows, "cols": cols}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
