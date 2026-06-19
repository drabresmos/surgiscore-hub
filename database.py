import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('surgiscore_ward.db')
ATTACH_DIR = Path('attachments')
ATTACH_DIR.mkdir(exist_ok=True)

SCHEMA_VERSION = 7

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('''CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT,
        patient_name TEXT,
        age INTEGER,
        sex TEXT,
        phone TEXT,
        diagnosis TEXT,
        operation_type TEXT,
        operation_date TEXT,
        start_time TEXT,
        surgeon TEXT,
        assistant TEXT,
        anesthesia TEXT,
        urgency TEXT,
        wound_class TEXT,
        status TEXT,
        bed TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER,
        score_name TEXT,
        result TEXT,
        interpretation TEXT,
        risk TEXT,
        notes TEXT,
        status TEXT DEFAULT 'Calculated',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER,
        filename TEXT,
        stored_path TEXT,
        filetype TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ward_rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER,
        round_date TEXT,
        shift TEXT,
        temp REAL,
        pulse INTEGER,
        bp TEXT,
        rr INTEGER,
        spo2 INTEGER,
        pain_score INTEGER,
        urine_output TEXT,
        drain_output TEXT,
        wound_status TEXT,
        oral_intake TEXT,
        bowel_function TEXT,
        mobility TEXT,
        antibiotics TEXT,
        anticoagulation TEXT,
        plan TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS intraop_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER,
        incision_time TEXT,
        closure_time TEXT,
        findings TEXT,
        procedure_done TEXT,
        blood_loss TEXT,
        specimens TEXT,
        drains TEXT,
        complications TEXT,
        sign_in_done INTEGER DEFAULT 0,
        time_out_done INTEGER DEFAULT 0,
        sign_out_done INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation_id INTEGER,
        phase TEXT,
        task TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)', ('schema_version', str(SCHEMA_VERSION)))
    c.commit(); c.close()

def execute(q, params=()):
    init_db(); c=conn(); cur=c.execute(q, params); c.commit(); rid=cur.lastrowid; c.close(); return rid

def query(q, params=()):
    init_db(); c=conn(); rows=[dict(r) for r in c.execute(q, params)]; c.close(); return rows

def add_operation(data):
    cols = ','.join(data.keys())
    qs = ','.join(['?']*len(data))
    return execute(f'INSERT INTO operations ({cols}) VALUES ({qs})', tuple(data.values()))

def update_operation(op_id, data):
    data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    sets = ','.join([f'{k}=?' for k in data.keys()])
    execute(f'UPDATE operations SET {sets} WHERE id=?', tuple(data.values())+(op_id,))

def get_operations(): return query('SELECT * FROM operations ORDER BY operation_date ASC, start_time ASC')
def get_operation(op_id):
    rows=query('SELECT * FROM operations WHERE id=?',(op_id,)); return rows[0] if rows else None

def get_ops_by_month(year, month):
    prefix=f'{year:04d}-{month:02d}'
    return query('SELECT * FROM operations WHERE operation_date LIKE ? ORDER BY operation_date,start_time', (prefix+'%',))

def delete_operation(op_id):
    execute('DELETE FROM operations WHERE id=?',(op_id,)); execute('DELETE FROM scores WHERE operation_id=?',(op_id,)); execute('DELETE FROM ward_rounds WHERE operation_id=?',(op_id,)); execute('DELETE FROM attachments WHERE operation_id=?',(op_id,)); execute('DELETE FROM intraop_notes WHERE operation_id=?',(op_id,)); execute('DELETE FROM tasks WHERE operation_id=?',(op_id,))

def add_score(operation_id, name, result, interpretation, risk, notes='', status='Calculated'):
    execute('INSERT INTO scores(operation_id,score_name,result,interpretation,risk,notes,status) VALUES(?,?,?,?,?,?,?)', (operation_id,name,str(result),interpretation,risk,notes,status))

def get_scores(operation_id): return query('SELECT * FROM scores WHERE operation_id=? ORDER BY id DESC', (operation_id,))
def get_all_scores(): return query('SELECT * FROM scores ORDER BY id DESC')

def add_round(data):
    cols=','.join(data.keys()); qs=','.join(['?']*len(data)); return execute(f'INSERT INTO ward_rounds ({cols}) VALUES ({qs})', tuple(data.values()))
def get_rounds(operation_id): return query('SELECT * FROM ward_rounds WHERE operation_id=? ORDER BY round_date DESC, shift DESC', (operation_id,))

def add_intraop(data):
    cols=','.join(data.keys()); qs=','.join(['?']*len(data)); return execute(f'INSERT INTO intraop_notes ({cols}) VALUES ({qs})', tuple(data.values()))
def get_intraop(operation_id): return query('SELECT * FROM intraop_notes WHERE operation_id=? ORDER BY id DESC', (operation_id,))

def add_attachment(operation_id, uploaded_file, description=''):
    safe = uploaded_file.name.replace('/','_').replace('\\','_')
    path = ATTACH_DIR / f'op{operation_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}_{safe}'
    path.write_bytes(uploaded_file.getvalue())
    execute('INSERT INTO attachments(operation_id,filename,stored_path,filetype,description) VALUES(?,?,?,?,?)', (operation_id, uploaded_file.name, str(path), uploaded_file.type, description))

def get_attachments(operation_id): return query('SELECT * FROM attachments WHERE operation_id=? ORDER BY id DESC', (operation_id,))
