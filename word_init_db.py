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

def get_words_json(filename):
    with open(filename, 'r') as openfile:
        json_obj = json.load(openfile)
    return json_obj

def create_and_write_dict(txtfile):
    f = open(txtfile, 'r')
    wordlist = [line.strip('\n') for line in f]
    words_dict = {word : 0 for word in wordlist if len(word) < 8 and len(word) > 4}
    json_obj = json.dumps(words_dict, indent=4)
    with open('words_dict.json', 'w') as outfile:
        outfile.write(json_obj) 

def create_alphabet_tables():
    alphabets=list(string.ascii_lowercase)
    for char in alphabets:
        create_table(char.upper())
    dict = get_words_json('words_dict.json')
    for word in dict:
        first_char = word[0].upper()
        insert_word(first_char, word)


# create_and_write_dict('scrabble_words.txt')
# create_alphabet_tables()


# conn = get_db_connection()
# res = conn.execute("SELECT * FROM A LIMIT 10").fetchall()
# for row in res:
#     print(row[0])
