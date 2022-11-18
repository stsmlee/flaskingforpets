import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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

# get_info()

# conn = get_db_connection()
# change = conn.execute('UPDATE saves SET results  = ? WHERE user_id = ?', ("{}", 1))
# conn.commit()
# conn.close()

# count_saves(1)
# count_saves(2)

def check_pragma_fkey():
    conn = get_db_connection()
    print(conn.execute("PRAGMA foreign_keys"))
    conn.close()