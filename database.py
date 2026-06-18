import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('surgiscore.db')

def conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    c = conn()
    cur = c.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS patients (
        code TEXT PRIMARY KEY, name TEXT, age INTEGER, sex TEXT,
        diagnosis TEXT, operation TEXT, notes TEXT, created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_code TEXT, score TEXT,
        result TEXT, interpretation TEXT, risk TEXT, created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_code TEXT, filename TEXT,
        mime TEXT, size_kb REAL, data BLOB, created_at TEXT
    )''')
    c.commit(); c.close()

def add_patient(code, name, age, sex, diagnosis, operation, notes):
    c=conn(); cur=c.cursor()
    cur.execute('INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)',
        (code,name,age,sex,diagnosis,operation,notes,datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()

def list_patients():
    c=conn(); c.row_factory=sqlite3.Row; cur=c.cursor()
    rows=cur.execute('SELECT * FROM patients ORDER BY created_at DESC').fetchall(); c.close()
    return [dict(r) for r in rows]

def get_patient(code):
    c=conn(); c.row_factory=sqlite3.Row; cur=c.cursor()
    r=cur.execute('SELECT * FROM patients WHERE code=?',(code,)).fetchone(); c.close()
    return dict(r) if r else None

def delete_patient(code):
    c=conn(); cur=c.cursor()
    cur.execute('DELETE FROM patients WHERE code=?',(code,))
    cur.execute('DELETE FROM results WHERE patient_code=?',(code,))
    cur.execute('DELETE FROM attachments WHERE patient_code=?',(code,))
    c.commit(); c.close()

def save_result(patient_code, score, result, interpretation, risk):
    c=conn(); cur=c.cursor()
    cur.execute('INSERT INTO results(patient_code,score,result,interpretation,risk,created_at) VALUES (?,?,?,?,?,?)',
        (patient_code, score, str(result), interpretation, risk, datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()

def list_results():
    c=conn(); c.row_factory=sqlite3.Row; cur=c.cursor()
    rows=cur.execute('SELECT * FROM results ORDER BY id DESC').fetchall(); c.close()
    return [dict(r) for r in rows]

def add_attachment(patient_code, file):
    c=conn(); cur=c.cursor()
    data=file.getvalue()
    cur.execute('INSERT INTO attachments(patient_code,filename,mime,size_kb,data,created_at) VALUES (?,?,?,?,?,?)',
        (patient_code, file.name, file.type, round(file.size/1024,1), data, datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()

def list_attachments(patient_code):
    c=conn(); c.row_factory=sqlite3.Row; cur=c.cursor()
    rows=cur.execute('SELECT id,patient_code,filename,mime,size_kb,created_at FROM attachments WHERE patient_code=? ORDER BY id DESC',(patient_code,)).fetchall(); c.close()
    return [dict(r) for r in rows]

def get_attachment(att_id):
    c=conn(); c.row_factory=sqlite3.Row; cur=c.cursor()
    r=cur.execute('SELECT * FROM attachments WHERE id=?',(att_id,)).fetchone(); c.close()
    return dict(r) if r else None

def delete_attachment(att_id):
    c=conn(); cur=c.cursor(); cur.execute('DELETE FROM attachments WHERE id=?',(att_id,)); c.commit(); c.close()
