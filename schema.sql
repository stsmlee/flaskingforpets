-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS saves;
-- DROP TABLE IF EXISTS session_table;
-- DROP TABLE IF EXISTS puzzles;

CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT,
    -- timezone TEXT DEFAULT 'US/Eastern',
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
        -- ON CONFLICT REPLACE,
        -- if you replace it will log out their other sessions on other devices/browsers
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS puzzle_users(
    user_id = INTEGER PRIMARY KEY,
    word = TEXT NOT NULL,
    guess_count = INTEGER NOT NULL DEFAULT 0,
    guess_words = TEXT,
    complete = INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (word) REFERENCES puzzles(word)
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

CREATE TABLE IF NOT EXISTS puzzles(
    creator_id INTEGER,
    word TEXT PRIMARY KEY ON CONFLICT IGNORE,
    FOREIGN KEY (creator_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
)