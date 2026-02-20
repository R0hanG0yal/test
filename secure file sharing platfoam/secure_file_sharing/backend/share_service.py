from flask import Blueprint, request, render_template, redirect, url_for, session, flash, send_from_directory, current_app
from backend.database import get_db
from backend.auth import login_required
import uuid
from datetime import datetime, timedelta

share_bp = Blueprint('share_service', __name__)

@share_bp.route('/share/<int:file_id>', methods=['POST'])
@login_required
def create_share(file_id):
    hours = int(request.form.get('hours', 24))
    one_time = 1 if request.form.get('one_time') else 0
    token = uuid.uuid4().hex
    expires_at = (datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    
    with get_db() as conn:
        file_record = conn.execute("SELECT * FROM files WHERE id = ? AND owner_id = ?", (file_id, session['user_id'])).fetchone()
        if not file_record:
            flash("Unauthorized", "error")
            return redirect(url_for('file_service.dashboard'))
            
        conn.execute("INSERT INTO shares (file_id, token, expires_at, one_time) VALUES (?, ?, ?, ?)",
                     (file_id, token, expires_at, one_time))
    
    share_link = url_for('share_service.view_share', token=token, _external=True)
    flash(f"Share link created: {share_link}", "success")
    return redirect(url_for('file_service.dashboard'))

@share_bp.route('/s/<token>', methods=['GET', 'POST'])
def view_share(token):
    with get_db() as conn:
        share = conn.execute("SELECT * FROM shares WHERE token = ?", (token,)).fetchone()
        if not share:
            return "Invalid share link", 404
            
        if datetime.now().strftime('%Y-%m-%d %H:%M:%S') > share['expires_at']:
            return "Share link expired", 403
            
        if share['one_time'] and share['is_used']:
            return "This one-time link has already been used.", 403
            
        file_record = conn.execute("SELECT * FROM files WHERE id = ?", (share['file_id'],)).fetchone()
        
        # If owner is viewing their own link, allow direct download unconditionally
        if session.get('user_id') == file_record['owner_id']:
             return send_from_directory(current_app.config['UPLOAD_FOLDER'], file_record['filename'], as_attachment=True, download_name=file_record['original_name'])

        if request.method == 'POST':
            email = request.form.get('email')
            req = conn.execute("SELECT * FROM access_requests WHERE file_id = ? AND requester_email = ?", (share['file_id'], email)).fetchone()
            
            if req and req['status'] == 'approved':
                if share['one_time']:
                    conn.execute("UPDATE shares SET is_used = 1 WHERE id = ?", (share['id'],))
                return send_from_directory(current_app.config['UPLOAD_FOLDER'], file_record['filename'], as_attachment=True, download_name=file_record['original_name'])
            elif req and req['status'] == 'pending':
                flash("Your access request is still pending approval.", "info")
            elif req and req['status'] == 'denied':
                flash("Your access to this file has been denied.", "error")
            else:
                conn.execute("INSERT INTO access_requests (file_id, requester_email) VALUES (?, ?)", (share['file_id'], email))
                flash("Access requested. Please wait for the owner to approve.", "success")
                
    return render_template('shared_file.html', file=file_record, token=token)

@share_bp.route('/requests')
@login_required
def access_requests():
    with get_db() as conn:
        requests = conn.execute("""
            SELECT ar.id, ar.requester_email, ar.status, ar.request_date, f.original_name 
            FROM access_requests ar
            JOIN files f ON ar.file_id = f.id
            WHERE f.owner_id = ?
            ORDER BY ar.request_date DESC
        """, (session['user_id'],)).fetchall()
    return render_template('access_requests.html', requests=requests)

@share_bp.route('/requests/<int:req_id>/<action>', methods=['POST'])
@login_required
def handle_request(req_id, action):
    if action not in ['approve', 'deny']:
        return "Invalid action", 400
        
    status = 'approved' if action == 'approve' else 'denied'
    with get_db() as conn:
        # Verify ownership
        req = conn.execute("""
            SELECT ar.id FROM access_requests ar
            JOIN files f ON ar.file_id = f.id
            WHERE ar.id = ? AND f.owner_id = ?
        """, (req_id, session['user_id'])).fetchone()
        
        if req:
            conn.execute("UPDATE access_requests SET status = ? WHERE id = ?", (status, req_id))
            flash(f"Request {status} successfully.", "success")
        else:
            flash("Unauthorized", "error")
            
    return redirect(url_for('share_service.access_requests'))
