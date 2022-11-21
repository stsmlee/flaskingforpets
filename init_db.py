import sqlite3

connection = sqlite3.connect('database.db')

# connection.execute("PRAGMA foreign_keys = ON")

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()