import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print('\n'.join([row[0] for row in tables]))
conn.close()
