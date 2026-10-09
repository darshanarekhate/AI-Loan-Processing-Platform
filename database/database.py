import sqlite3

from config import DATABASE_PATH


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)

    conn.row_factory = sqlite3.Row

    # SQLite ignores FOREIGN KEY / ON DELETE CASCADE unless enabled
    # per connection.
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
