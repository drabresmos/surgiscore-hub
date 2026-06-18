import sqlite3, os, json
from datetime import datetime
DB_PATH = os.environ.get('SURGISCORE_DB', 'surgiscore.db')
ATTACH_DIR = 'attachments'
os.makedirs(ATTACH_DIR, exist_ok=True)

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c=conn(); cur=c.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT, age INTEGER, sex TEXT, diagnosis TEXT, operation TEXT, notes TEXT, created_at TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY AUTOINCREMENT, patient_code TEXT, category TEXT, score_name TEXT, result TEXT, risk TEXT, interpretation TEXT, inputs_json TEXT, created_at TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS attachments(id INTEGER PRIMARY KEY AUTOINCREMENT, patient_code TEXT, filename TEXT, filetype TEXT, size_kb REAL, path TEXT, created_at TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS learning_log(id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, note TEXT, created_at TEXT)''')
    c.commit(); c.close()

def add_patient(code,name,age,sex,diagnosis,operation,notes):
    c=conn(); cur=c.cursor()
    cur.execute('INSERT INTO patients(code,name,age,sex,diagnosis,operation,notes,created_at) VALUES(?,?,?,?,?,?,?,?)',(code,name,age,sex,diagnosis,operation,notes,datetime.now().strftime('%Y-%m-%d %H:%M')))
    c.commit(); c.close()

def update_patient(code,name,age,sex,diagnosis,operation,notes):
    c=conn(); cur=c.cursor(); cur.execute('UPDATE patients SET name=?,age=?,sex=?,diagnosis=?,operation=?,notes=? WHERE code=?',(name,age,sex,diagnosis,operation,notes,code)); c.commit(); c.close()

def delete_patient(code):
    c=conn(); cur=c.cursor(); cur.execute('DELETE FROM patients WHERE code=?',(code,)); cur.execute('DELETE FROM results WHERE patient_code=?',(code,)); cur.execute('DELETE FROM attachments WHERE patient_code=?',(code,)); c.commit(); c.close()

def get_patients():
    c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM patients ORDER BY id DESC')]; c.close(); return rows

def get_patient(code):
    c=conn(); r=c.execute('SELECT * FROM patients WHERE code=?',(code,)).fetchone(); c.close(); return dict(r) if r else None

def save_result(patient_code,category,score_name,result,risk,interpretation,inputs):
    c=conn(); cur=c.cursor(); cur.execute('INSERT INTO results(patient_code,category,score_name,result,risk,interpretation,inputs_json,created_at) VALUES(?,?,?,?,?,?,?,?)',(patient_code,category,score_name,str(result),risk,interpretation,json.dumps(inputs,ensure_ascii=False),datetime.now().strftime('%Y-%m-%d %H:%M'))); c.commit(); c.close()

def get_results(patient_code=None):
    c=conn();
    if patient_code: rows=[dict(r) for r in c.execute('SELECT * FROM results WHERE patient_code=? ORDER BY id DESC',(patient_code,))]
    else: rows=[dict(r) for r in c.execute('SELECT * FROM results ORDER BY id DESC')]
    c.close(); return rows

def delete_result(rid):
    c=conn(); c.execute('DELETE FROM results WHERE id=?',(rid,)); c.commit(); c.close()

def save_attachment(patient_code, uploaded_file):
    ts=datetime.now().strftime('%Y%m%d%H%M%S')
    safe=uploaded_file.name.replace('/','_').replace('\\','_')
    path=os.path.join(ATTACH_DIR, f'{patient_code}_{ts}_{safe}')
    data=uploaded_file.getvalue()
    with open(path,'wb') as f: f.write(data)
    c=conn(); c.execute('INSERT INTO attachments(patient_code,filename,filetype,size_kb,path,created_at) VALUES(?,?,?,?,?,?)',(patient_code,uploaded_file.name,uploaded_file.type,round(len(data)/1024,1),path,datetime.now().strftime('%Y-%m-%d %H:%M'))); c.commit(); c.close()

def get_attachments(patient_code):
    c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM attachments WHERE patient_code=? ORDER BY id DESC',(patient_code,))]; c.close(); return rows

def delete_attachment(aid):
    c=conn(); r=c.execute('SELECT path FROM attachments WHERE id=?',(aid,)).fetchone()
    if r and os.path.exists(r['path']): os.remove(r['path'])
    c.execute('DELETE FROM attachments WHERE id=?',(aid,)); c.commit(); c.close()

def add_learning_note(topic,note):
    c=conn(); c.execute('INSERT INTO learning_log(topic,note,created_at) VALUES(?,?,?)',(topic,note,datetime.now().strftime('%Y-%m-%d %H:%M'))); c.commit(); c.close()

def get_learning_notes():
    c=conn(); rows=[dict(r) for r in c.execute('SELECT * FROM learning_log ORDER BY id DESC')]; c.close(); return rows
