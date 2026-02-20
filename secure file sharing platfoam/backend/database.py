import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "secure_share.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        filename TEXT,
        stored_name TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        token TEXT UNIQUE,
        expires_at DATETIME,
        one_time INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0,
        FOREIGN KEY(file_id) REFERENCES files(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        email TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()