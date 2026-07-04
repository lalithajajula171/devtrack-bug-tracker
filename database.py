import sqlite3

conn = sqlite3.connect("bugs.db")
cursor = conn.cursor()

# Bugs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bugs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    priority TEXT,
    status TEXT
)
""")

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")