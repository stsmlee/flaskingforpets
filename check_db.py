import sqlite3
from datetime import datetime, timedelta
import pytz
import copy
import random

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def get_info():
    conn = get_db_connection()
    user = zip_results('users')
    if not user:
        print('No users in the database.')
    else:
        print('USERS TABLE')
        for u in user:
            print(u)
    saved = zip_results('saves')
    if not saved:
        print('No saved searches in the database.')
    else:
        print('SAVED TABLE')
        for save in saved:
            print(save)
    session = zip_results('session_table')
    if not session:
        print('No sessions in the database.')
    else:
        print('SESSIONS TABLE')
        for s in session:
            print(s)
    puzzlers = zip_results('puzzlers')
    if puzzlers:
        print("PUZZLERS TABLE")
        for p in puzzlers:
            print(p)
    else:
        print('No puzzlers yet.')
    puzzles = zip_results('puzzles')
    if puzzles:
        print("PUZZLES TABLE")
        for puzz in puzzles:
            print(puzz)
    # print('ALL OUR TABLES:')
    # sql_query = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # for row in sql_query:
    #     print(row['name'])
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

def zip_results(tablename):
    conn = get_db_connection()
    curs = conn.execute(f'SELECT * FROM {tablename}')
    cols = [description[0] for description in curs.description]
    rows = curs.fetchall()
    entries = []
    for row in rows:
        entry = {}
        for col, val in zip(cols, row):
            if col != 'password':
                entry[col]=val
        entries.append(entry)
    conn.close()
    return entries

def delete_expired_sessions(set_days):
    conn = get_db_connection()
    expire = datetime.now() - timedelta(days=set_days)
    res = conn.execute('SELECT age,user_id FROM session_table WHERE age < ?', (expire,)).fetchall()
    if res:
        print('These sessions are too old and will be deleted:')
        for row in res:
            print(row['age'], 'user_id:', row['user_id'])
    else:
        print('No expired sessions.')
    conn.execute('DELETE FROM session_table WHERE age < ?', (expire,))
    conn.commit()
    conn.close()

def clear_results(savename):
    conn = get_db_connection()
    conn.execute('UPDATE saves SET results = "{}" WHERE savename = ?', (savename,))
    conn.commit()
    conn.close()

def joinery():
    conn = get_db_connection()
    res = conn.execute('SELECT username, savename FROM users JOIN saves ON id = user_id').fetchall()
    for row in res:
        for col in row:
            print(col)    
    
# get_info()
# delete_expired_sessions(30)

def add_puzzle_word_db(word):
    conn = get_db_connection()
    conn.execute('INSERT INTO puzzles (word) VALUES (?)', (word.upper(),))
    conn.commit()
    conn.close()

def add_puzzle_to_puzzler(user_id, puzzle_id):
    conn = get_db_connection()
    conn.execute(f'INSERT INTO puzzlers (user_id, puzzle_id) VALUES (?,?)', (user_id, puzzle_id))
    conn.commit()
    conn.close()

def played_puzzles(user_id):
    conn = get_db_connection()
    curs = conn.execute('SELECT * FROM puzzlers JOIN puzzles ON puzzlers.puzzle_id = puzzles.id WHERE puzzlers.user_id = ?', (user_id,))
    cols = [description[0] for description in curs.description]
    rows = curs.fetchall()
    entries = []
    for row in rows:
        entry = {}
        for col, val in zip(cols, row):
            if col == 'creator_id':
                continue
            if col == 'word':
                if row['complete'] != 1:
                    continue
            entry[col] = val
        entries.append(entry)
    conn.close()
    return entries

def get_random_puzzle_id(user_id):
    conn = get_db_connection()
    curs = conn.execute("SELECT puzzle_id FROM puzzlers WHERE user_id = ?", (user_id,)).fetchall()
    prev_puzzles = {row[0] for row in curs}
    curs = conn.execute("SELECT creator_id, id as puzzle_id FROM puzzles").fetchall()
    new_puzzles = [row['puzzle_id'] for row in curs if row[0] not in prev_puzzles]
    pick = random.randint(0, len(new_puzzles)-1)
    return new_puzzles[pick]

def get_puzzle_word(puzzle_id):
    conn = get_db_connection()
    word = conn.execute("SELECT word FROM puzzles WHERE id = ?", (puzzle_id,)).fetchone()
    return word[0]

def get_created_puzzles(user_id):
    conn = get_db_connection()
    curs = conn.execute("SELECT id as puzzle_id,word,plays,wins FROM puzzles WHERE creator_id = ?", (user_id,))
    if curs:
        cols = [description[0] for description in curs.description]
        rows = curs.fetchall()
        entries = []
        for row in rows:
            entry = {}
            for col, val in zip(cols, row):
                entry[col] = val
            entries.append(entry)
        conn.close()
        return entries

# conn = get_db_connection()
# conn.execute("ALTER TABLE puzzles RENAME COLUMN play TO plays")
# conn.commit()
# conn.close()

# conn = get_db_connection()
# conn.execute('UPDATE puzzlers SET complete = 1 WHERE puzzle_id = 1')
# conn.commit()
# conn.close()

# conn = get_db_connection()
# # conn.execute("ALTER TABLE puzzles ADD COLUMN wins INTEGER NOT NULL DEFAULT 0")
# # conn.execute('UPDATE puzzles SET creator_id = 1 WHERE id = 1')
# conn.commit()
# conn.close()

# add_puzzle_to_puzzler(1,1)
# rand_id = get_random_puzzle_id(1)
# add_puzzle_to_puzzler(1, rand_id)
# print(get_puzzle_word(rand_id))
puzzles = played_puzzles(1)
for p in puzzles:
    print(p)
print(get_created_puzzles(1))

# get_info()