import sqlite3
from datetime import datetime, timedelta
import pytz
import copy

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
        print('USERS TABLE')
        for row in user:
            print(f"user_id: {row['id']}, user_name: {row['username']}, nickname: {row['nickname']}")
    saved = conn.execute('SELECT * FROM saves').fetchall()
    if not saved:
        print('No saved searches in the database.')
    else:
        print('SAVED TABLE')
        for row in saved:
            print("savename:", row['savename'], ", user_id:", row['user_id'])
            print("params:", row['params'])
            print("results:", row['results'])
    session = conn.execute('SELECT * FROM session_table').fetchall()
    if not session:
        print('No sessions in the database.')
    else:
        print('SESSIONS TABLE')
        for row in session:
            print("user_token:", row['user_token'])
            print("user_id:", row['user_id'])
            print("timestamp:", row[2])
    puzzlers = conn.execute('SELECT * FROM puzzlers').fetchall()
    if puzzlers:
        print("PUZZLERS TABLE")
        for row in puzzlers:
            print("user_id:",row['user_id'], row["word"], "guess count:", row['guess_count'], "guess words:",row['guess_words'], "complete:", [row['complete']])
    else:
        print('No puzzlers yet.')
    puzzles = conn.execute('SELECT * FROM puzzles').fetchall()
    print("PUZZLES TABLE")
    for row in puzzles:
        print(row['word'], "creator id:", row['creator_id'],)
    print('ALL OUR TABLES:')
    sql_query = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in sql_query:
        print(row['name'])
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
    
get_info()
# delete_expired_sessions(30)

# published_at ="2018-12-22T20:31:32+0000"
# date_published_utc = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")
# print(datetime.strftime(date_published_utc, "%b %d, %Y at %I:%M%p %Z"))
# date_published_est = date_published_utc.astimezone(pytz.timezone('US/Eastern'))
# publish_str = datetime.strftime(date_published_est, "%b %d, %Y at %I:%M%p %Z")
# print(publish_str)

# def change_tz(dt, tz):
#     if not tz:
#         tz = pytz.timezone('US/Eastern')
#     return dt.astimezone(pytz.timezone(tz))
# publish_date_utc = datetime.strptime(pet['published_at'], "%Y-%m-%dT%H:%M:%S%z")
# publish_date_tz = change_tz(publish_date_utc, tz)
# publish_str = datetime.strftime(publish_date_tz, "%b %d, %Y at %I:%M%p %Z")

# print(pytz.common_timezones)

# tz_list = ['America/Cancun', 'America/Hermosillo', 'America/Mexico_City', 'America/Tijuana', 'Canada/Atlantic', 'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'US/Alaska', 'US/Arizona', 'US/Central', 'US/Eastern', 'US/Hawaii', 'US/Mountain', 'US/Pacific']
# tz_tuples = []
# for tz in tz_list:
#     tz_split = tz.split('/')
#     if tz_split[0] == 'America':
#         label = 'Mexico/'+tz_split[1]
#         tz_tuples.append((tz, label))
#     else:
#         tz_tuples.append((tz,tz))
# tz_tuples.append(('UTC','UTC'))
# print(tz_tuples)
