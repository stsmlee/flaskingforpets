import copy
import random
import sqlite3
import json

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

class Puzzle:
    def __init__(self, word, guess_words = [], guess_count = 0, evals = []):
        word = word.upper()
        self.word = word
        self.max_guesses = len(word)+1
        self.expected_letter_count = {}
        for letter in word:
            if letter not in self.expected_letter_count:
                self.expected_letter_count[letter] = 1
            else:
                self.expected_letter_count[letter] += 1
        self.guess_letter_count = copy.deepcopy(self.expected_letter_count)
        self.guess_count = guess_count
        self.guess_words = guess_words
        self.evals = evals

    def reset_letter_count(self):
        self.guess_letter_count = copy.deepcopy(self.expected_letter_count)

def check_guess(guess, puzzle):
    eval = []
    # guess = ''.join(guess)
    guess = guess.upper()
    if guess == puzzle.word:
        puzzle.guess_count += 1
        puzzle.guess_words.append(guess)
        puzzle.evals.append('win')
    else:
        for i in range(len(guess)):
            if guess[i] == puzzle.word[i]:
                puzzle.guess_letter_count[guess[i]] -= 1
                eval.append((guess[i], 2))
            elif guess[i] != puzzle.word[i] and guess[i] in puzzle.word and puzzle.guess_letter_count[guess[i]] > 0:
                puzzle.guess_letter_count[guess[i]] -= 1
                eval.append((guess[i], 1))
            else:
                eval.append((guess[i], 0))
        puzzle.guess_count += 1
        puzzle.guess_words.append(guess)
        puzzle.reset_letter_count()
        puzzle.evals.append(eval)
    print(puzzle.__dict__.items())
    return eval

def get_attrs(puzzle):
    # ['expected_letter_count', 'guess_count', 'guess_letter_count', 'guess_words', 'max_guesses', 'reset_letter_count', 'word']
    # attrs = [a for a in dir(puzzle) if not a.startswith('__')]
    return puzzle.__dict__.items()
    # return attrs

def add_placeholders(puzzle_form):
    puzzle_form.l0.render_kw['placeholder'] = puzzle_form.l0.data
    puzzle_form.l1.render_kw['placeholder'] = puzzle_form.l1.data
    puzzle_form.l2.render_kw['placeholder'] = puzzle_form.l2.data
    puzzle_form.l3.render_kw['placeholder'] = puzzle_form.l3.data
    puzzle_form.l4.render_kw['placeholder'] = puzzle_form.l4.data
    if puzzle_form.l5:
        puzzle_form.l5.render_kw['placeholder'] = puzzle_form.l5.data
    if puzzle_form.l6:
        puzzle_form.l6.render_kw['placeholder'] = puzzle_form.l6.data

def clear_placeholders(puzzle_form):
    puzzle_form.l0.render_kw['placeholder'] = ''
    puzzle_form.l1.render_kw['placeholder'] = ''
    puzzle_form.l2.render_kw['placeholder'] = ''
    puzzle_form.l3.render_kw['placeholder'] = ''
    puzzle_form.l4.render_kw['placeholder'] = ''
    if puzzle_form.l5:
        puzzle_form.l5.render_kw['placeholder'] = ''
    if puzzle_form.l6:
        puzzle_form.l6.render_kw['placeholder'] = ''

def build_word(form_data):
    guess = ''
    for fieldname,value in form_data.items():
        if 'csrf' not in fieldname:
            guess+=value
    guess = guess.upper()
    return guess

def valid_word(word):
    conn = get_db_connection()
    first_char = word[0]
    res = conn.execute(f'''SELECT * FROM {first_char} WHERE word = "{word.lower()}"''').fetchone()
    if res:
        return True

def trim_form(form, word):
    excess = 7-len(word)
    if excess > 0:
        del form.l6
    if excess > 1:
        del form.l5

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
    rows = curs.fetchall()
    if rows:
        cols = [description[0] for description in curs.description]
        entries = []
        for row in rows:
            entry = {}
            for col, val in zip(cols, row):
                entry[col] = val
            entries.append(entry)
        conn.close()
        return entries

def puzzle_instance(details):
    puzzle = Puzzle(details['word'], guess_count=details['guess_count'], guess_words=details['guess_words'], evals=details['evals'] )
    return puzzle

def get_puzzle_db(user_id=1, puzzle_id=1):   
    conn = get_db_connection()
    curs = conn.execute('SELECT word, puzzle_id, guess_count, guess_words, evals, complete, success FROM puzzlers JOIN puzzles ON puzzlers.puzzle_id = puzzles.id WHERE puzzlers.user_id = ? AND puzzles.id = ? ORDER BY word', (user_id,puzzle_id))
    row = curs.fetchone()
    if row:
        cols = [description[0] for description in curs.description]
        details = {}
        for col, val in zip(cols, row):
            if col == 'guess_words' and val:
                details[col] = json.loads(val)
                continue
            details[col] = val
            conn.close()
        return details
    conn.close()

def puzzle_loader(puzzle_id):
    puzzle_info = get_puzzle_db(puzzle_id=puzzle_id)
    if puzzle_info:
        print('puzzle_info', puzzle_info)
        puzzle = puzzle_instance(puzzle_info)
        # print(get_attrs(puzzle))
        # print(puzzle)


# choices = ['TREAT']
choices = [Puzzle('TREAT')]

