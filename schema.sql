DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS saves;
DROP TABLE IF EXISTS session_table;

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT,
    password TEXT NOT NULL
);

CREATE TABLE saves(
   savename TEXT NOT NULL,
   params TEXT NOT NULL,
   results TEXT,
   user_id INTEGER NOT NULL,
   PRIMARY KEY (savename, user_id),
   FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE session_table(
    user_token TEXT UNIQUE PRIMARY KEY,
    user_id INTEGER NOT NULL,
        -- ON CONFLICT REPLACE,
        -- if you replace it will log out their other sessions on other devices/browsers
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
