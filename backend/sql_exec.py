# backend/sql_exec.py (updated)
import sqlite3, os
from pathlib import Path

BASE = Path(__file__).parent
DEFAULT_DB = BASE / "sample.db"
ACTIVE_DB = BASE / "current_data.db"

def get_db_path():
    return str(ACTIVE_DB if ACTIVE_DB.exists() else DEFAULT_DB)

def init_sample_db():
    if DEFAULT_DB.exists():
        return
    conn = sqlite3.connect(str(DEFAULT_DB))
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY, name TEXT, department_id INTEGER, salary REAL);
    INSERT INTO departments(id, name) VALUES (1,'HR'),(2,'Marketing'),(3,'IT');
    INSERT INTO employees(name, department_id, salary) VALUES
    ('Alice',2,70000),('Bob',1,50000),('Charlie',2,65000),('David',3,80000);
    ''')
    conn.commit(); conn.close()

def execute_sql(sql):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    conn.close()
    return rows, cols
