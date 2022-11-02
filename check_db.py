import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_tofu(username):
    conn = get_db_connection()
    userid = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    print(userid['id'])
    print(userid[0])

def get_info():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users').fetchall()
    if not user:
        print('No users in the database.')
    else:
        for row in user:
            # print(row[0])
            # print(row[1])
            print(row['id'])
            print(row['username'])
    saved = conn.execute('SELECT * FROM saves').fetchall()
    if not saved:
        print('No saved searches in the database.')
    else:
        for row in saved:
            print(row[0])
            print(row[1])
            print(row[2])       
    conn.close()

def get_savenames():
    conn = get_db_connection()
    res = conn.execute('SELECT savename FROM saves WHERE user_id = ?', (1,)).fetchall()
    conn.close()
    results = [row['savename'] for row in res]
    print(results) 

get_info()
# get_tofu('Tofu')
# get_saved_searches()