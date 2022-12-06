import copy
import random
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

class Puzzle:
    def __init__(self, word):
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
        self.guess_count = 0
        self.guess_words = []
        self.evals = []

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

choices = [Puzzle('Treat')]

def get_random_puzzle():
    pick = random.randint(0, len(choices)-1)
    return(pick)


