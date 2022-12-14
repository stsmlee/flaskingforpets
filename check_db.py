import sqlite3
from datetime import datetime, timedelta
import pytz
import copy
import random
import json
from app.pet_helper.squeerdle import Puzzle

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

def print_tables():
    conn=get_db_connection()
    print('ALL OUR TABLES:')
    sql_query = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in sql_query:
        print(row['name'])
    conn.close()


def print_puzzlers_puzzles():
    conn = get_db_connection()
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

def valid_word(word):
    conn = get_db_connection()
    first_char = word[0]
    res = conn.execute(f'''SELECT * FROM {first_char} WHERE word = "{word}"''').fetchone()
    conn.close()
    if res:
        return True

def add_puzzle_word_db(word, user_id = None):
    if valid_word(word.upper()):
        conn = get_db_connection()
        res = conn.execute("SELECT word, id FROM puzzles WHERE word = ?", (word,)).fetchone()
        if res:
            print(f'{res["word"]}, id #{res["id"]}, already exists in our puzzle database.')
        else:
            conn.execute('INSERT INTO puzzles (word, creator_id) VALUES (?,?)', (word.upper(), user_id))
            conn.commit()
        conn.close()
    else:
        print(f"{word} is an invalid word")

# def get_puzzlers_puzzles(user_id):
#     conn = get_db_connection()
#     curs = conn.execute('SELECT word, puzzle_id, guess_count, guess_words, evals, complete, success FROM puzzlers JOIN puzzles ON puzzlers.puzzle_id = puzzles.id WHERE puzzlers.user_id = ? ORDER BY word', (user_id,))
#     rows = curs.fetchall()
#     if rows:
#         cols = [description[0] for description in curs.description]
#         entries = []
#         for row in rows:
#             entry = {}
#             for col, val in zip(cols, row):
#                 if col == 'guess_words' and val:
#                     entry[col] = json.loads(val)
#                     continue
#                 entry[col] = val
#             entries.append(entry)
#         conn.close()
#         return entries

def get_attrs(puzzle):
    # ['expected_letter_count', 'guess_count', 'guess_letter_count', 'guess_words', 'max_guesses', 'reset_letter_count', 'word']
    # attrs = [a for a in dir(puzzle) if not a.startswith('__')]
    return puzzle.__dict__.items()
    # return attrs

def puzzle_starter_pack():
    starter_pack = ['archer', 'bandit', 'earth', 'front', 'ghost', 'treat', 'chart', 'death', 'blast', 'shout', 'doubt', 'verge', 'dealt', 'beast', 'healer', 'idiot', 'jockey', 'knife', 'lemon', 'minion', 'never', 'option', 'prime', 'quick', 'risky', 'under', 'wicked', 'young','snatch', 'zesty']
    for word in starter_pack:
        add_puzzle_word_db(word)

# get_info()

# print_tables()

# puzzle_starter_pack()
print_puzzlers_puzzles()
