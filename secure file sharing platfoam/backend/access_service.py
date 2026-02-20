from flask import request, jsonify, session
from datetime import datetime
from database import get_connection


# ---------------- REQUEST ACCESS ----------------
def request_access(token):
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, owner_id FROM shares WHERE token=?", (token,))
    share = cursor.fetchone()

    if not share:
        conn.close()
        return jsonify({"error": "Invalid share"}), 404

    cursor.execute("""
        INSERT INTO access_requests
        (share_id, requester_email, requested_at)
        VALUES (?, ?, ?)
    """, (share["id"], email, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

    return jsonify({"message": "Access request sent"})


# ---------------- VIEW REQUESTS (OWNER) ----------------
def view_requests():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ar.id, ar.requester_email, ar.status, ar.requested_at, s.encrypted_name
        FROM access_requests ar
        JOIN shares s ON ar.share_id = s.id
        WHERE s.owner_id = ?
        ORDER BY ar.requested_at DESC
    """, (session["user_id"],))

    requests = cursor.fetchall()
    conn.close()

    return jsonify([
        dict(r) for r in requests
    ])


# ---------------- APPROVE REQUEST ----------------
def approve_request(request_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE access_requests
        SET status='approved', approved_at=?
        WHERE id=?
    """, (datetime.utcnow().isoformat(), request_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Access approved"})