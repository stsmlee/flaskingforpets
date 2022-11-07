DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS saves;

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
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
