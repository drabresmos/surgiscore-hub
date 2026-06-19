import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('surgiscore.db')


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = conn()
    c.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT,
        age INTEGER,
        sex TEXT,
        diagnosis TEXT,
        operation TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        score_name TEXT NOT NULL,
        category TEXT,
        result TEXT,
        interpretation TEXT,
        risk TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        filename TEXT,
        filetype TEXT,
        size_kb REAL,
        data BLOB,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )''')
    c.commit(); c.close()


def add_patient(code, name, age, sex, diagnosis, operation, notes):
    init_db(); c=conn()
    c.execute('''INSERT INTO patients(code,name,age,sex,diagnosis,operation,notes,created_at,updated_at)
                 VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)''',
              (code,name,age,sex,diagnosis,operation,notes))
    c.commit(); c.close()


def update_patient(pid, code, name, age, sex, diagnosis, operation, notes):
    init_db(); c=conn()
    c.execute('''UPDATE patients SET code=?,name=?,age=?,sex=?,diagnosis=?,operation=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',
              (code,name,age,sex,diagnosis,operation,notes,pid))
    c.commit(); c.close()


def get_patients():
    init_db(); c=conn()
    rows=[dict(r) for r in c.execute('SELECT * FROM patients ORDER BY id DESC')]
    c.close(); return rows


def get_patient(pid):
    init_db(); c=conn()
    row=c.execute('SELECT * FROM patients WHERE id=?',(pid,)).fetchone()
    c.close(); return dict(row) if row else None


def delete_patient(pid):
    init_db(); c=conn()
    c.execute('DELETE FROM attachments WHERE patient_id=?',(pid,))
    c.execute('DELETE FROM results WHERE patient_id=?',(pid,))
    c.execute('DELETE FROM patients WHERE id=?',(pid,))
    c.commit(); c.close()


def add_result(patient_id, score_name, category, result, interpretation, risk, details=''):
    init_db(); c=conn()
    c.execute('''INSERT INTO results(patient_id,score_name,category,result,interpretation,risk,details,created_at)
                 VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)''',
              (patient_id,score_name,category,str(result),interpretation,risk,details))
    c.commit(); c.close()


def get_results(patient_id=None):
    init_db(); c=conn()
    if patient_id:
        rows=[dict(r) for r in c.execute('''SELECT r.*, p.code, p.name FROM results r JOIN patients p ON p.id=r.patient_id WHERE patient_id=? ORDER BY r.id DESC''',(patient_id,))]
    else:
        rows=[dict(r) for r in c.execute('''SELECT r.*, p.code, p.name FROM results r JOIN patients p ON p.id=r.patient_id ORDER BY r.id DESC''')]
    c.close(); return rows


def delete_result(rid):
    init_db(); c=conn(); c.execute('DELETE FROM results WHERE id=?',(rid,)); c.commit(); c.close()


def add_attachment(patient_id, filename, filetype, size_kb, data):
    init_db(); c=conn()
    c.execute('''INSERT INTO attachments(patient_id,filename,filetype,size_kb,data,created_at)
                 VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)''', (patient_id,filename,filetype,size_kb,data))
    c.commit(); c.close()


def get_attachments(patient_id):
    init_db(); c=conn()
    rows=[dict(r) for r in c.execute('SELECT id,patient_id,filename,filetype,size_kb,created_at FROM attachments WHERE patient_id=? ORDER BY id DESC',(patient_id,))]
    c.close(); return rows


def get_attachment_data(aid):
    init_db(); c=conn(); row=c.execute('SELECT * FROM attachments WHERE id=?',(aid,)).fetchone(); c.close(); return dict(row) if row else None


def delete_attachment(aid):
    init_db(); c=conn(); c.execute('DELETE FROM attachments WHERE id=?',(aid,)); c.commit(); c.close()
