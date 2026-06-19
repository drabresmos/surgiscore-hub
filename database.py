import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('surgiscore.db')

PATIENT_COLUMNS = {
    'id':'INTEGER PRIMARY KEY AUTOINCREMENT','code':'TEXT UNIQUE','name':'TEXT','age':'INTEGER','sex':'TEXT',
    'diagnosis':'TEXT','operation':'TEXT','notes':'TEXT','created_at':'TEXT DEFAULT CURRENT_TIMESTAMP'
}
RESULT_COLUMNS = {
    'id':'INTEGER PRIMARY KEY AUTOINCREMENT','patient_id':'INTEGER','score_name':'TEXT','result':'TEXT','interpretation':'TEXT','risk':'TEXT','created_at':'TEXT DEFAULT CURRENT_TIMESTAMP'
}
ATTACH_COLUMNS = {
    'id':'INTEGER PRIMARY KEY AUTOINCREMENT','patient_id':'INTEGER','filename':'TEXT','filetype':'TEXT','data':'BLOB','created_at':'TEXT DEFAULT CURRENT_TIMESTAMP'
}
OP_COLUMNS = {
    'id':'INTEGER PRIMARY KEY AUTOINCREMENT','patient_id':'INTEGER','operation_title':'TEXT','operation_type':'TEXT','operation_date':'TEXT','operation_time':'TEXT','surgeon':'TEXT','hospital':'TEXT','status':'TEXT','notes':'TEXT','created_at':'TEXT DEFAULT CURRENT_TIMESTAMP'
}

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def ensure_table(c, table, columns):
    cols_sql = ', '.join([f'{k} {v}' for k,v in columns.items()])
    c.execute(f'CREATE TABLE IF NOT EXISTS {table} ({cols_sql})')
    existing = [r['name'] for r in c.execute(f'PRAGMA table_info({table})')]
    for name, definition in columns.items():
        if name not in existing and name != 'id':
            c.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')

def init_db():
    c = conn()
    ensure_table(c, 'patients', PATIENT_COLUMNS)
    ensure_table(c, 'results', RESULT_COLUMNS)
    ensure_table(c, 'attachments', ATTACH_COLUMNS)
    ensure_table(c, 'operations', OP_COLUMNS)
    c.commit(); c.close()

def get_patients():
    init_db(); c = conn()
    rows = [dict(r) for r in c.execute('SELECT * FROM patients ORDER BY id DESC')]
    c.close(); return rows

def get_patient(patient_id):
    init_db(); c = conn()
    row = c.execute('SELECT * FROM patients WHERE id=?', (patient_id,)).fetchone()
    c.close(); return dict(row) if row else None

def add_patient(code, name, age, sex, diagnosis, operation, notes):
    init_db(); c = conn()
    c.execute('INSERT OR IGNORE INTO patients(code,name,age,sex,diagnosis,operation,notes) VALUES (?,?,?,?,?,?,?)',
              (code,name,age,sex,diagnosis,operation,notes))
    c.commit(); c.close()

def update_patient(patient_id, code, name, age, sex, diagnosis, operation, notes):
    init_db(); c = conn()
    c.execute('UPDATE patients SET code=?, name=?, age=?, sex=?, diagnosis=?, operation=?, notes=? WHERE id=?',
              (code,name,age,sex,diagnosis,operation,notes,patient_id))
    c.commit(); c.close()

def delete_patient(patient_id):
    init_db(); c = conn()
    for table in ['results','attachments','operations']:
        c.execute(f'DELETE FROM {table} WHERE patient_id=?', (patient_id,))
    c.execute('DELETE FROM patients WHERE id=?', (patient_id,))
    c.commit(); c.close()

def add_result(patient_id, score_name, result, interpretation, risk):
    init_db(); c = conn()
    c.execute('INSERT INTO results(patient_id,score_name,result,interpretation,risk) VALUES (?,?,?,?,?)',
              (patient_id,score_name,str(result),interpretation,risk))
    c.commit(); c.close()

def get_results(patient_id=None):
    init_db(); c = conn()
    if patient_id:
        rows = [dict(r) for r in c.execute('SELECT * FROM results WHERE patient_id=? ORDER BY id DESC', (patient_id,))]
    else:
        rows = [dict(r) for r in c.execute('SELECT r.*, p.code, p.name FROM results r LEFT JOIN patients p ON p.id=r.patient_id ORDER BY r.id DESC')]
    c.close(); return rows

def add_attachment(patient_id, filename, filetype, data):
    init_db(); c=conn()
    c.execute('INSERT INTO attachments(patient_id,filename,filetype,data) VALUES (?,?,?,?)', (patient_id,filename,filetype,data))
    c.commit(); c.close()

def get_attachments(patient_id):
    init_db(); c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM attachments WHERE patient_id=? ORDER BY id DESC',(patient_id,))]; c.close(); return rows

def delete_attachment(attachment_id):
    init_db(); c=conn(); c.execute('DELETE FROM attachments WHERE id=?',(attachment_id,)); c.commit(); c.close()

def add_operation(patient_id, title, op_type, date, time, surgeon, hospital, status, notes):
    init_db(); c=conn()
    c.execute('INSERT INTO operations(patient_id,operation_title,operation_type,operation_date,operation_time,surgeon,hospital,status,notes) VALUES (?,?,?,?,?,?,?,?,?)',
              (patient_id,title,op_type,date,time,surgeon,hospital,status,notes))
    c.commit(); c.close()

def update_operation(op_id, patient_id, title, op_type, date, time, surgeon, hospital, status, notes):
    init_db(); c=conn()
    c.execute('UPDATE operations SET patient_id=?, operation_title=?, operation_type=?, operation_date=?, operation_time=?, surgeon=?, hospital=?, status=?, notes=? WHERE id=?',
              (patient_id,title,op_type,date,time,surgeon,hospital,status,notes,op_id))
    c.commit(); c.close()

def delete_operation(op_id):
    init_db(); c=conn(); c.execute('DELETE FROM operations WHERE id=?',(op_id,)); c.commit(); c.close()

def get_operations():
    init_db(); c=conn()
    rows=[dict(r) for r in c.execute('SELECT o.*, p.code, p.name, p.age, p.sex, p.diagnosis FROM operations o LEFT JOIN patients p ON p.id=o.patient_id ORDER BY o.operation_date ASC, o.operation_time ASC')]
    c.close(); return rows
