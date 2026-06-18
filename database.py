import sqlite3
from pathlib import Path

DB_PATH = Path("surgiscore.db")

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            age INTEGER,
            sex TEXT,
            diagnosis TEXT,
            operation TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            score_name TEXT,
            result TEXT,
            interpretation TEXT,
            risk TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            filename TEXT,
            filetype TEXT,
            data BLOB,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.commit()
    c.close()

def get_patients():
    init_db()
    c = conn()
    rows = [dict(r) for r in c.execute("SELECT * FROM patients ORDER BY id DESC")]
    c.close()
    return rows
