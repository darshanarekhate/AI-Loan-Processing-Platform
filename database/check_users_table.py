from database.database import get_connection


conn = get_connection()

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("DATABASE TABLES:")

for table in tables:
    print("-", table["name"])

users_table = conn.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type='table' AND name='users'"
).fetchone()

print()

if users_table:
    print("✅ users table exists")
else:
    print("❌ users table does NOT exist")

conn.close()