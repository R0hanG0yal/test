import os
import uuid
from database import get_db

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

def save_file(file, owner_id):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    stored_name = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, stored_name)
    file.save(path)

    db = get_db()
    db.execute(
        "INSERT INTO files (owner_id, filename, stored_name) VALUES (?, ?, ?)",
        (owner_id, file.filename, stored_name)
    )
    db.commit()

def get_user_files(user_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM files WHERE owner_id = ?", (user_id,)
    ).fetchall()

def get_file(file_id):
    db = get_db()
    return db.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()