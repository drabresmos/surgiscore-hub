import sqlite3
from pathlib import Path

DB_PATH = Path('surgiscore.db')

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.execute('''CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        age INTEGER,
        sex TEXT,
        phone TEXT,
        diagnosis TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS operations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        op_date TEXT,
        start_time TEXT,
        operation_type TEXT,
        surgeon TEXT,
        assistant TEXT,
        anesthesia TEXT,
        priority TEXT,
        status TEXT,
        theatre TEXT,
        indication TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        operation_id INTEGER,
        score_name TEXT,
        result TEXT,
        interpretation TEXT,
        risk TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attachments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        operation_id INTEGER,
        filename TEXT,
        filetype TEXT,
        data BLOB,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.commit(); c.close()

def add_patient(code,name,age,sex,phone,diagnosis,notes):
    init_db(); c=conn()
    c.execute('INSERT OR IGNORE INTO patients(code,name,age,sex,phone,diagnosis,notes) VALUES(?,?,?,?,?,?,?)',(code,name,age,sex,phone,diagnosis,notes))
    c.commit(); pid=c.execute('SELECT id FROM patients WHERE code=?',(code,)).fetchone()['id']; c.close(); return pid

def get_patients():
    init_db(); c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM patients ORDER BY id DESC')]; c.close(); return rows

def get_patient(pid):
    init_db(); c=conn(); r=c.execute('SELECT * FROM patients WHERE id=?',(pid,)).fetchone(); c.close(); return dict(r) if r else None

def delete_patient(pid):
    init_db(); c=conn()
    c.execute('DELETE FROM attachments WHERE patient_id=?',(pid,)); c.execute('DELETE FROM results WHERE patient_id=?',(pid,)); c.execute('DELETE FROM operations WHERE patient_id=?',(pid,)); c.execute('DELETE FROM patients WHERE id=?',(pid,))
    c.commit(); c.close()

def add_operation(patient_id, op_date, start_time, operation_type, surgeon, assistant, anesthesia, priority, status, theatre, indication, details):
    init_db(); c=conn()
    c.execute('''INSERT INTO operations(patient_id,op_date,start_time,operation_type,surgeon,assistant,anesthesia,priority,status,theatre,indication,details)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',(patient_id,op_date,start_time,operation_type,surgeon,assistant,anesthesia,priority,status,theatre,indication,details))
    c.commit(); oid=c.execute('SELECT last_insert_rowid() AS id').fetchone()['id']; c.close(); return oid

def get_operations(month=None):
    init_db(); c=conn()
    q='''SELECT o.*, p.name, p.code, p.age, p.sex, p.diagnosis FROM operations o JOIN patients p ON p.id=o.patient_id'''
    params=[]
    if month:
        q += ' WHERE substr(o.op_date,1,7)=?'; params.append(month)
    q += ' ORDER BY o.op_date ASC, o.start_time ASC'
    rows=[dict(r) for r in c.execute(q,params)]; c.close(); return rows

def get_operation(oid):
    init_db(); c=conn(); r=c.execute('''SELECT o.*, p.name, p.code, p.age, p.sex, p.diagnosis FROM operations o JOIN patients p ON p.id=o.patient_id WHERE o.id=?''',(oid,)).fetchone(); c.close(); return dict(r) if r else None

def add_result(patient_id, operation_id, score_name, result, interpretation, risk):
    init_db(); c=conn(); c.execute('INSERT INTO results(patient_id,operation_id,score_name,result,interpretation,risk) VALUES(?,?,?,?,?,?)',(patient_id,operation_id,score_name,str(result),interpretation,risk)); c.commit(); c.close()

def get_results(operation_id=None):
    init_db(); c=conn();
    if operation_id:
        rows=[dict(r) for r in c.execute('SELECT * FROM results WHERE operation_id=? ORDER BY id DESC',(operation_id,))]
    else:
        rows=[dict(r) for r in c.execute('SELECT r.*, p.name, p.code FROM results r LEFT JOIN patients p ON p.id=r.patient_id ORDER BY r.id DESC')]
    c.close(); return rows

def add_attachment(patient_id, operation_id, filename, filetype, data):
    init_db(); c=conn(); c.execute('INSERT INTO attachments(patient_id,operation_id,filename,filetype,data) VALUES(?,?,?,?,?)',(patient_id,operation_id,filename,filetype,data)); c.commit(); c.close()

def get_attachments(operation_id=None):
    init_db(); c=conn()
    if operation_id:
        rows=[dict(r) for r in c.execute('SELECT * FROM attachments WHERE operation_id=? ORDER BY id DESC',(operation_id,))]
    else:
        rows=[dict(r) for r in c.execute('SELECT * FROM attachments ORDER BY id DESC')]
    c.close(); return rows

def delete_attachment(aid):
    init_db(); c=conn(); c.execute('DELETE FROM attachments WHERE id=?',(aid,)); c.commit(); c.close()
