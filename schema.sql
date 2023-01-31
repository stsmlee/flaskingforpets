-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS saves;
-- DROP TABLE IF EXISTS session_table;
-- DROP TABLE IF EXISTS puzzlers;
-- DROP TABLE IF EXISTS puzzles;

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saves(
   savename TEXT NOT NULL,
   params TEXT NOT NULL,
   results TEXT,
   user_id INTEGER NOT NULL,
   PRIMARY KEY (savename, user_id),
   FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_table(
    user_token TEXT UNIQUE PRIMARY KEY,
    user_id INTEGER NOT NULL,
    age TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS puzzlers(
    user_id INTEGER,
    puzzle_id INTEGER NOT NULL,
    guess_count INTEGER NOT NULL DEFAULT 0,
    guess_words TEXT NOT NULL DEFAULT '[]',
    complete INTEGER NOT NULL DEFAULT 0,
    date_of_completion TIMESTAMP,
    success INTEGER NOT NULL DEFAULT 0,
    inbox INTEGER NOT NULL DEFAULT 0,
    evals TEXT NOT NULL DEFAULT '[]',
    PRIMARY KEY (user_id, puzzle_id) ON CONFLICT IGNORE,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (puzzle_id) REFERENCES puzzles(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS puzzles(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER,
    date_of_creation TIMESTAMP,
    word TEXT UNIQUE
        ON CONFLICT IGNORE,
    plays INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (creator_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);