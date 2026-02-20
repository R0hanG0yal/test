import uuid
from datetime import datetime, timedelta
from database import get_db

def create_share(file_id, hours, one_time):
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(hours=hours)

    db = get_db()
    db.execute(
        "INSERT INTO shares (file_id, token, expires_at, one_time) VALUES (?, ?, ?, ?)",
        (file_id, token, expires.isoformat(), int(one_time))
    )
    db.commit()
    return token

def get_share(token):
    db = get_db()
    return db.execute(
        "SELECT * FROM shares WHERE token = ?", (token,)
    ).fetchone()

def increment_download(share):
    db = get_db()
    db.execute(
        "UPDATE shares SET downloads = downloads + 1 WHERE id = ?",
        (share["id"],)
    )
    if share["one_time"]:
        db.execute("DELETE FROM shares WHERE id = ?", (share["id"],))
    db.commit()

def request_access(file_id, email):
    db = get_db()
    db.execute(
        "INSERT INTO access_requests (file_id, email) VALUES (?, ?)",
        (file_id, email)
    )
    db.commit()

def get_requests(owner_id):
    db = get_db()
    return db.execute("""
        SELECT ar.*, f.filename FROM access_requests ar
        JOIN files f ON ar.file_id = f.id
        WHERE f.owner_id = ?
    """, (owner_id,)).fetchall()

def update_request(req_id, status):
    db = get_db()
    db.execute(
        "UPDATE access_requests SET status = ? WHERE id = ?",
        (status, req_id)
    )
    db.commit()