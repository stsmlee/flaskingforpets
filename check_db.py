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
            print(f"user_id: {row['id']}, user_name: {row['username']}, nickname: {row['nickname']}")
            # print(row['username'])
            # print(row['password'])
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

# conn = get_db_connection()
# change = conn.execute('UPDATE saves SET results  = ? WHERE user_id = ?', ("{}", 1))
# conn.commit()
# conn.close()

# conn = get_db_connection()
# conn.execute('INSERT INTO session_table (user_token, user_id) VALUES (?,?)', ("239748492dfsdfsdf3", 1))
# conn.commit()
# conn.close()

# conn = get_db_connection()
# conn.execute('DELETE FROM session_table WHERE user_token = ?', ("239748492dfsdfsdf3",))
# conn.commit()
# conn.close()

# conn = get_db_connection()
# conn.execute('INSERT INTO users (username, nickname, password) VALUES (?,?, ?)', ('tofu', 'Tofu', 'password'))
# conn.execute('INSERT INTO session_table (user_token, user_id) VALUES (?,?)', ("239748492dfsdfsdf3", 1))
# conn.commit()
# conn.close()

get_info()

# def get_user_id():
#     conn = get_db_connection()
#     user = conn.execute('SELECT user_id FROM session_table WHERE user_token = ?', ("239748492dfsdfsdf3",)).fetchone()
#     conn.close()
#     return user[0]

# conn = get_db_connection()
# res= conn.execute('SELECT username FROM users INNER JOIN session_table ON users.id = session_table.user_id').fetchone()
# conn.close()
# print(res['username'])

# conn = get_db_connection()
# user_id = get_user_id()
# # username = conn.execute('SELECT username FROM users INNER JOIN session_table ON users.id = session_table.user_id').fetchone()
# username = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
# conn.close()
# print(username[0]) 


conn = get_db_connection()
check = conn.execute('SELECT * FROM session_table WHERE user_token = ?', ('222',)).fetchone()
if check:
    print("YAS")