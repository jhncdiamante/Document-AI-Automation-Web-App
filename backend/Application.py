import eventlet
eventlet.monkey_patch()
import os
import atexit
import signal

import logging
from datetime import timedelta
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from src.Models import db, User, Job as JobModel
from src.Process.JobManager import Jobs
from src.Process.Worker import Worker

# --- Flask App ---
app = Flask(__name__)
CORS(app, supports_credentials=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config['UPLOAD_FOLDER'] = 'userdata/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'check_same_thread': False,
        'timeout': 5  # 5 second timeout for database operations
    }
}

# Session config
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_COOKIE_SECURE'] = False
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

# Lightweight SocketIO config
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode="eventlet", 
    manage_session=False,  # Disable session management for performance
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

worker = Worker(app, socketio=socketio)
jobs = Jobs(app, worker, socketio)

def initialize_workers():
    """Initialize worker and job manager"""
    global worker, jobs
    worker = Worker(app, socketio=socketio, max_workers=1)  # Single worker to prevent resource issues
    jobs = Jobs(app, worker, socketio, worker_count=1)  # Single queue worker
    return worker, jobs

def cleanup_workers():
    """Clean shutdown of workers"""
    global worker, jobs
    if jobs:
        jobs.shutdown()
    if worker:
        worker.shutdown()

# Register cleanup handlers
atexit.register(cleanup_workers)
signal.signal(signal.SIGTERM, lambda s, f: cleanup_workers())

# Initialize database
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
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

# --- Ultra-fast auth routes ---
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({"message": "Username and password required"}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            session.permanent = True
            return jsonify({
                "message": "Login successful", 
                "username": user.username
            }), 200
            
        return jsonify({"message": "Invalid credentials"}), 401
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"message": "Login failed"}), 500

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"msg": "Logged out successfully"}), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({"msg": "Logout failed"}), 500

@app.route("/me", methods=["GET"])
def me():
    try:
        # Use minimal database operations
        if current_user.is_authenticated:
            return jsonify({
                "username": current_user.username,
                "user_id": current_user.id,
                "status": "authenticated"
            }), 200
        return jsonify({"message": "Not logged in", "status": "unauthenticated"}), 401
    except Exception as e:
        print(f"Session check error: {e}")
        # Return unauthenticated on any error to prevent hanging
        return jsonify({"message": "Session check failed", "status": "error"}), 500

# --- SocketIO events (minimal) ---
@socketio.on("connect")
def handle_connect():
    try:
        if current_user.is_authenticated:
            join_room(f"user_{current_user.id}")
            print(f"User {current_user.id} connected")
        return True  # Accept connection
    except Exception as e:
        print(f"Socket connect error: {e}")
        return False  # Reject connection

# --- Job routes ---
@app.route("/user/add_job", methods=["POST"])
@login_required
def add_job():
    try:
        return jobs.add(request)
    except Exception as e:
        print(f"Add job error: {e}")
        return jsonify({"error": "Failed to add job"}), 500

@app.route("/user/jobs/<job_id>/stop", methods=["POST"])
@login_required
def stop_job(job_id):
    try:
        return jobs.stop(job_id)
    except Exception as e:
        print(f"Stop job error: {e}")
        return jsonify({"error": "Failed to stop job"}), 500

@app.route("/user/jobs/<job_id>/delete", methods=["DELETE"])
@login_required
def delete_job(job_id):
    try:
        return jobs.delete(job_id)
    except Exception as e:
        print(f"Delete job error: {e}")
        return jsonify({"error": "Failed to delete job"}), 500

@app.route("/user/jobs", methods=["GET"])
@login_required
def get_jobs():
    """
    Get all jobs for current user - should be fast
    """
    try:
        jobs_list = JobModel.query.filter_by(user_id=current_user.id).all()
        return jsonify([
            {
                "id": j.id,
                "case_number": j.case_number,
                "branch": j.branch,
                "status": j.status,
                "created_at": j.created_at.isoformat(),
                "files": [{"permanent_file_name": u.permanent_file_name} for u in j.uploads],
                "feature": j.feature,
                "description": j.description,
                "completed_at": j.audit_result.completed_at.isoformat() if j.audit_result and j.audit_result.completed_at else None,
                "accuracy": j.audit_result.accuracy if j.audit_result else None,
                "issues": j.audit_result.issues if j.audit_result else [],
                "error": j.error if hasattr(j, 'error') and j.error else (j.audit_result.error if j.audit_result and hasattr(j.audit_result, 'error') else None)
            } for j in jobs_list
        ])
    except Exception as e:
        print(f"Get jobs error: {e}")
        return jsonify({"error": "Failed to fetch jobs"}), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": str(db.func.current_timestamp())}), 200

# --- Static file serving ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    try:
        build_dir = os.path.join(os.path.dirname(__file__), "frontend", "build")
        if path != "" and os.path.exists(os.path.join(build_dir, path)):
            return send_from_directory(build_dir, path)
        return send_from_directory(build_dir, "index.html")
    except Exception as e:
        print(f"Static file serving error: {e}")
        return "File not found", 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Starting application...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Run with eventlet
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=True, 
        use_reloader=False,  
        log_output=False  # Reduce log noise
    )