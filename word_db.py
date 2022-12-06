import json
import sqlite3
import string

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def create_table(first_char):
    conn = get_db_connection()
    conn.execute(f"""DROP TABLE IF EXISTS {first_char}""")
    conn.execute(f"""CREATE TABLE {first_char} (
        word TEXT PRIMARY KEY ON CONFLICT IGNORE)""")
    conn.commit()
    conn.close()

def insert_word(first_char, word):
    conn= get_db_connection()
    conn.execute(f"""INSERT INTO {first_char} (word) 
            VALUES ('{word}')""")
    conn.commit()
    conn.close()

def get_words_json():
    with open('all_english_words.json', 'r') as openfile:
        json_obj = json.load(openfile)
    return json_obj

def update_words_json(dict):
    json_obj = json.dumps(dict, indent = 4)
    with open('english_words_trimmed.json', 'w') as outfile:
        outfile.write(json_obj)

def get_updated_words_json():
    with open('english_words_trimmed.json', 'r') as openfile:
        json_obj = json.load(openfile)
        return json_obj

# english_words_dict = get_words_json()
# new_dict = {word : 0 for word in english_words_dict if len(word) < 8 and len(word) > 4}
# update_words_json(new_dict)

# alphabets=list(string.ascii_lowercase)
# for char in alphabets:
#     create_table(char.upper())

# dict = get_updated_words_json()

# for word in dict:
#     first_char = word[0].upper()
#     insert_word(first_char, word)

# conn= get_db_connection()
# res= conn.execute("SELECT * FROM A LIMIT 10").fetchall()
# for row in res:
#     print(row[0])
# conn.close()
