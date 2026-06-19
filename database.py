import sqlite3, json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('surgiscore.db')

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c=conn()
    c.execute('''CREATE TABLE IF NOT EXISTS operations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT, patient_name TEXT, age INTEGER, sex TEXT,
        diagnosis TEXT, operation_type TEXT, operation_date TEXT, start_time TEXT,
        surgeon TEXT, assistant TEXT, anesthesia TEXT, status TEXT,
        details TEXT, required_scores TEXT, score_status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS score_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER, score_name TEXT, result TEXT,
        interpretation TEXT, risk TEXT, skipped INTEGER DEFAULT 0,
        skip_reason TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attachments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER, filename TEXT, filetype TEXT, data BLOB,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.commit(); c.close()

def add_operation(data):
    init_db(); c=conn()
    c.execute('''INSERT INTO operations(patient_code,patient_name,age,sex,diagnosis,operation_type,operation_date,start_time,surgeon,assistant,anesthesia,status,details,required_scores,score_status)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data.get('patient_code'), data.get('patient_name'), data.get('age'), data.get('sex'), data.get('diagnosis'), data.get('operation_type'), data.get('operation_date'), data.get('start_time'), data.get('surgeon'), data.get('assistant'), data.get('anesthesia'), data.get('status'), data.get('details'), json.dumps(data.get('required_scores',[])), 'Pending'
    ))
    oid=c.lastrowid; c.commit(); c.close(); return oid

def get_operations():
    init_db(); c=conn()
    rows=[dict(r) for r in c.execute('SELECT * FROM operations ORDER BY operation_date DESC, start_time DESC')]
    c.close(); return rows

def get_operation(operation_id):
    init_db(); c=conn(); r=c.execute('SELECT * FROM operations WHERE id=?',(operation_id,)).fetchone(); c.close(); return dict(r) if r else None

def update_operation_status(operation_id, status, score_status=None):
    init_db(); c=conn()
    if score_status is None:
        c.execute('UPDATE operations SET status=? WHERE id=?',(status,operation_id))
    else:
        c.execute('UPDATE operations SET status=?, score_status=? WHERE id=?',(status,score_status,operation_id))
    c.commit(); c.close()

def delete_operation(operation_id):
    init_db(); c=conn(); c.execute('DELETE FROM score_results WHERE operation_id=?',(operation_id,)); c.execute('DELETE FROM attachments WHERE operation_id=?',(operation_id,)); c.execute('DELETE FROM operations WHERE id=?',(operation_id,)); c.commit(); c.close()

def add_score_result(operation_id, score_name, result, interpretation, risk, skipped=0, skip_reason=''):
    init_db(); c=conn()
    c.execute('DELETE FROM score_results WHERE operation_id=? AND score_name=?',(operation_id,score_name))
    c.execute('''INSERT INTO score_results(operation_id,score_name,result,interpretation,risk,skipped,skip_reason) VALUES(?,?,?,?,?,?,?)''',(operation_id,score_name,str(result),interpretation,risk,skipped,skip_reason))
    c.commit(); c.close()

def get_score_results(operation_id):
    init_db(); c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM score_results WHERE operation_id=? ORDER BY score_name',(operation_id,))]; c.close(); return rows

def add_attachment(operation_id, filename, filetype, data):
    init_db(); c=conn(); c.execute('INSERT INTO attachments(operation_id,filename,filetype,data) VALUES(?,?,?,?)',(operation_id,filename,filetype,data)); c.commit(); c.close()

def get_attachments(operation_id):
    init_db(); c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM attachments WHERE operation_id=? ORDER BY id DESC',(operation_id,))]; c.close(); return rows
