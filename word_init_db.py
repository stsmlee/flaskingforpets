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

def txt_to_json(filename):
    pass

def get_words_json(filename):
    with open(filename, 'r') as openfile:
        json_obj = json.load(openfile)
    return json_obj

def trim_words_json(dict):
    json_obj = json.dumps(dict, indent = 4)
    with open('word_dict.json', 'w') as outfile:
        outfile.write(json_obj)

def create_and_write_dict(start_dict):
    words_dict = get_words_json('word_dictionary.json')
    new_dict = {word : definition for word, definition in words_dict.items() if len(word) < 8 and len(word) > 4}
    trim_words_json(new_dict)

def create_alphabet_tables():
    alphabets=list(string.ascii_lowercase)
    for char in alphabets:
        create_table(char.upper())


# create_and_write_dict("INSERTDICT")

# dict = get_words_json('word_dict.json')

# for word in dict:
#     first_char = word[0].upper()
#     insert_word(first_char, word)



# conn = get_db_connection()
# res = conn.execute("SELECT * FROM A LIMIT 10").fetchall()
# for row in res:
#     print(row[0])

f = open('scrabble_words.txt', 'r')
# readf = f.readlines()
wordlist = [line.strip('\n') for line in f]
# print(wordlist)

def create_and_write_dict(start_dict):
    f = open('scrabble_words.txt', 'r')
    wordlist = [line.strip('\n') for line in f]
    words_dict = get_words_json('word_dictionary.json')
    new_dict = {word : definition for word, definition in words_dict.items() if len(word) < 8 and len(word) > 4}
    trim_words_json(new_dict)