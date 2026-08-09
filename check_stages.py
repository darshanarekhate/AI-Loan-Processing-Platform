from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM application_stages")

rows = cursor.fetchall()

print(f"Total Rows: {len(rows)}")

for row in rows:
    print(dict(row))

conn.close()