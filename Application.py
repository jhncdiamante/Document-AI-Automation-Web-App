import eventlet
eventlet.monkey_patch()
from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import timedelta
import os
import eventlet.wsgi

from flask import send_from_directory


from flask_socketio import join_room

from backend.src.Models import db
from backend.src.Models import User, Upload, AuditResult
from backend.src.Process.JobManager import Jobs
from backend.src.Process.Worker import Worker

from backend.src.Models import Job as JobModel
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///users.db"
app.config['UPLOAD_FOLDER'] = 'userdata/uploads' 


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# Session settings
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_COOKIE_SECURE'] = False  # True if HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Init extensions
bcrypt = Bcrypt(app)
db.init_app(app)
Session(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True, async_mode="eventlet")
worker = Worker(socketio=socketio)
jobs = Jobs(app, worker, socketio)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



with app.app_context():
    db.create_all()

    # Only create admin if it doesn't exist
    if not User.query.filter_by(username="bestfuneralservices").first():
        hashed = bcrypt.generate_password_hash("bfsadmin").decode("utf-8")
        u = User(username="bestfuneralservices", password=hashed)
        db.session.add(u)
        db.session.commit()
        print("Created admin user:", u.username)    
    else:
        print("Admin user already exists")

# --- Flask-Login user loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user, remember=True)  # ensures Flask-Login remembers user
        session.permanent = True         # ensures Flask-Session persists the session
        return jsonify({"message": "Login successful", "username": user.username}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "Logged out"})

@app.route("/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify({
            "username": current_user.username
        }), 200
    return jsonify({"message": "Not logged in"}), 401


@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")


# --- Job routes (protected) ---
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
    with app.app_context():
        jobs = JobModel.query.filter_by(user_id=current_user.id).all()
        return jsonify([
        {
            "id": j.id,
            "case_number": j.case_number,
            "branch": j.branch,
            "status": j.status,
            "created_at": j.created_at,
            "files": [
                {
                    "permanent_file_name": u.permanent_file_name,
                }
                for u in j.uploads
            ],
            "feature": j.feature,
            "completed_at": j.audit_result.completed_at.isoformat() if j.audit_result and j.audit_result.completed_at else None,
            "accuracy": j.audit_result.accuracy if j.audit_result else None,
            "issues": j.audit_result.issues if j.audit_result else [],
            "error": j.audit_result.error if j.audit_result else None,
        }
        for j in jobs
    ])

    return jsonify({"error": "No Jobs found with the user ID."})



@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    # __file__ is application.py in root
    build_dir = os.path.join(os.path.dirname(__file__), "frontend", "build")
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    else:
        return send_from_directory(build_dir, "index.html")



if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)  
        
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)



