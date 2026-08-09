from database.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
DELETE FROM documents
WHERE document_id IN (13,14,15,16)
""")

conn.commit()
conn.close()

print("Duplicate documents removed successfully.")