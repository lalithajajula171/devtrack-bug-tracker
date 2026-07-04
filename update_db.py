import sqlite3

conn = sqlite3.connect("bugs.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE bugs ADD COLUMN created_at TEXT")
    conn.commit()
    print("created_at column added successfully!")
except:
    print("created_at column already exists!")

conn.close()