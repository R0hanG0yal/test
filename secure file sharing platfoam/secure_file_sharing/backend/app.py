import os
import sys

# Ensure backend can be imported when running script directly from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mimetypes
mimetypes.add_type('text/css', '.css')

from flask import Flask, redirect, url_for
from backend.database import init_db
from backend.auth import auth_bp
from backend.file_service import file_bp
from backend.share_service import share_bp

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'frontend')
    static_dir = os.path.join(base_dir, 'static')
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'super-secret-key-change-in-prod'
    app.config['UPLOAD_FOLDER'] = upload_dir
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max limit

    os.makedirs(upload_dir, exist_ok=True)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(share_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.errorhandler(404)
    def not_found(e):
        return "Page not found.", 404

    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Secure File Sharing Platform on http://127.0.0.1:5000")
    app.run(debug=True)
