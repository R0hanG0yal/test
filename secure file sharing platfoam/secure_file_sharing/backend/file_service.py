import os
import uuid
from flask import Blueprint, request, render_template, redirect, url_for, session, flash, send_from_directory, current_app
from backend.database import get_db
from backend.auth import login_required

file_bp = Blueprint('file_service', __name__)

@file_bp.route('/dashboard')
@login_required
def dashboard():
    with get_db() as conn:
        files = conn.execute("SELECT * FROM files WHERE owner_id = ? ORDER BY upload_date DESC", (session['user_id'],)).fetchall()
    return render_template('dashboard.html', files=files)

@file_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)
            
        original_name = file.filename
        ext = os.path.splitext(original_name)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        with get_db() as conn:
            conn.execute("INSERT INTO files (owner_id, filename, original_name) VALUES (?, ?, ?)", 
                         (session['user_id'], unique_filename, original_name))
        flash("File uploaded successfully", "success")
        return redirect(url_for('file_service.dashboard'))
    return render_template('upload.html')

@file_bp.route('/download/<int:file_id>')
@login_required
def download(file_id):
    with get_db() as conn:
        file_record = conn.execute("SELECT * FROM files WHERE id = ? AND owner_id = ?", (file_id, session['user_id'])).fetchone()
        
    if not file_record:
        flash("File not found or unauthorized.", "error")
        return redirect(url_for('file_service.dashboard'))
        
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], file_record['filename'], as_attachment=True, download_name=file_record['original_name'])
