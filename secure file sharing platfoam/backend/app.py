from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
from database import init_db
from auth import register_user, authenticate_user, login_required
from file_service import save_file, get_user_files, get_file, UPLOAD_FOLDER
from share_service import *

app = Flask(__name__,
            template_folder="../frontend",
            static_folder="../static")

app.secret_key = "super-secure-secret"

init_db()

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = authenticate_user(request.form["email"], request.form["password"])
        if user:
            session["user_id"] = user["id"]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if register_user(request.form["email"], request.form["password"]):
            return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
@login_required
def dashboard():
    files = get_user_files(session["user_id"])
    return render_template("dashboard.html", files=files)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        save_file(request.files["file"], session["user_id"])
        return redirect("/dashboard")
    return render_template("upload.html")

@app.route("/share/<int:file_id>", methods=["POST"])
@login_required
def share(file_id):
    token = create_share(
        file_id,
        int(request.form["hours"]),
        "one_time" in request.form
    )
    return f"Share link: http://localhost:5000/download/{token}"

@app.route("/download/<token>")
def download(token):
    share = get_share(token)
    if not share:
        return "Invalid or expired link"

    file = get_file(share["file_id"])
    increment_download(share)

    return send_from_directory(
        UPLOAD_FOLDER,
        file["stored_name"],
        as_attachment=True,
        download_name=file["filename"]
    )

@app.route("/access_requests", methods=["GET", "POST"])
@login_required
def access_requests():
    if request.method == "POST":
        update_request(request.form["id"], request.form["status"])
    requests = get_requests(session["user_id"])
    return render_template("access_requests.html", requests=requests)

if __name__ == "__main__":
    app.run(debug=True)