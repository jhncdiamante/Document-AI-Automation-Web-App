import os
import logging
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_socketio import join_room
from flask_session import Session
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from src.flask_config import app
from src.Socket import socketio

from src.Models import db, User


CORS(app, supports_credentials=True)


# Extensions
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from src.Process.JobManager import Jobs

# --- Initialize Worker and Jobs ---
jobs = Jobs(app, socketio)

# --- App context ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="bestfuneralservices").first():
        hashed = bcrypt.generate_password_hash("bfsadmin").decode("utf-8")
        u = User(username="bestfuneralservices", password=hashed)
        db.session.add(u)
        db.session.commit()
        print("Default admin user created")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --- Auth routes ---
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user, remember=True)
        session.permanent = True
        return jsonify({"message": "Login successful", "username": user.username}), 200

    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Logged out successfully"}), 200


@app.route("/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return (
            jsonify(
                {
                    "username": current_user.username,
                    "user_id": current_user.id,
                    "status": "authenticated",
                }
            ),
            200,
        )
    return jsonify({"message": "Not logged in", "status": "unauthenticated"}), 401


# --- SocketIO ---
@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        print(f"User {current_user.id} connected")


# --- Job routes ---
@app.route("/user/add_job", methods=["POST"])
@login_required
def add_job():
    return jobs.add(request)


@app.route("/user/jobs/<job_id>/stop", methods=["POST"])
@login_required
def stop_job(job_id):
    return jobs.stop(job_id)


@app.route("/user/jobs/<job_id>/delete", methods=["DELETE"])
@login_required
def delete_job(job_id):
    return jobs.delete(job_id)


@app.route("/user/jobs", methods=["GET"])
@login_required
def get_jobs():
    return jobs.get_all(current_user.id)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


# --- Static ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    build_dir = os.path.join(os.path.dirname(__file__), "frontend", "build")
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    return send_from_directory(build_dir, "index.html")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting application...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
