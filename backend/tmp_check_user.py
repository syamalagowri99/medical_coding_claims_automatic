import sqlite3

conn = sqlite3.connect('medical_coding.db')
cur = conn.cursor()
cur.execute("SELECT id, username, email, hashed_password, is_active FROM users WHERE username='newuser'")
print(cur.fetchone())
conn.close()
