import sqlite3

conn = sqlite3.connect("bugs.db")
cursor = conn.cursor()

print("TABLE STRUCTURE:")
cursor.execute("PRAGMA table_info(bugs)")
print(cursor.fetchall())

print("\nBUGS DATA:")
cursor.execute("SELECT * FROM bugs")
print(cursor.fetchall())

conn.close()