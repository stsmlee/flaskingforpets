import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def get_info():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users').fetchall()
    if not user:
        print('No users in the database.')
    else:
        for row in user:
            print(f"user_id: {row['id']}, user_name: {row['username']}, nickname: {row['nickname']}")
            # print(row['username'])
            print(row['password'])
    saved = conn.execute('SELECT * FROM saves').fetchall()
    if not saved:
        print('No saved searches in the database.')
    else:
        for row in saved:
            print(row[0])
            print(row[1])
            print(row[2])
            print(row[3])
    session = conn.execute('SELECT * FROM session_table').fetchall()
    if not session:
        print('No sessions in the database.')
    else:
        for row in session:
            print(row['user_token'])
            print(row['user_id'])
            print(row[2])
    conn.close()

def get_savenames():
    conn = get_db_connection()
    res = conn.execute('SELECT savename FROM saves WHERE user_id = ?', (1,)).fetchall()
    conn.close()
    results = [row['savename'] for row in res]
    print(results) 

def count_saves(user_id):
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT (*) FROM saves WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    print(count[0])

def check_pragma_fkey():
    conn = get_db_connection()
    print(conn.execute("PRAGMA foreign_keys"))
    conn.close()

def check_expired_sessions():
    conn = get_db_connection()
    set_time = 30
    expire = datetime.now() - timedelta(days=set_time)
    res = conn.execute('SELECT age,user_id FROM session_table WHERE age < ?', (expire,)).fetchall()
    if res:
        print('These sessions are too old and will be deleted')
        for row in res:
            print(row['age'])
            print('user_id:', row['user_id'])
    else:
        print('No expired sessions.')
    conn.execute('DELETE FROM session_table WHERE age < ?', (expire,))
    conn.commit()
    conn.close()

get_info()
check_expired_sessions()
