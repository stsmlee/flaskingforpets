import copy
import random

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
        return 'win'
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

choices = [Puzzle('Treat')]

def get_random_puzzle():
    pick = random.randint(0, len(choices)-1)
    return(pick)

