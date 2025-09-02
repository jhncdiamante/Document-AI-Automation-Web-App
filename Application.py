
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from backend.src.Processes.JobManager import JobManager
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import uuid
from backend.src.Data.SQLDatabase import SQLDatabase
from backend.src.Data.Redis import redis_conn
import threading, json
UPLOAD_FOLDER = 'userdata/uploads' 



app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*")

job_manager = JobManager()
database = SQLDatabase("test.db")




@app.route("/start_audit", methods=["POST"])
def start_audit():
    files_to_upload = request.files.getlist("files")

    permanent_filepaths = []
    permanent_filenames = []

    for file in files_to_upload:
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

        permanent_filenames.append(unique_filename)
        
        permanent_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file to your permanent 'uploads' directory
        file.save(permanent_filepath) 
        
        permanent_filepaths.append(permanent_filepath)

    user_uploaded_data = {
        "status": "queued",
        "case_number": request.form.get("case_number"),
        "branch": request.form.get("branch"),
        "feature": request.form.get("feature"),
        "description": request.form.get("description"),
        "created_at": request.form.get("created_at"),
        "files": [file.filename for file in files_to_upload],
    }

    job_id = job_manager.create_job(user_uploaded_data)

    user_uploaded_data["id"] = job_id

    job_manager.push_job(job_id)

    socketio.emit("new_job", user_uploaded_data)

    #database.save_job(user_uploaded_data, "1")
    #database.save_file_paths(permanent_filenames, permanent_filepaths, job_id, "1")

    return jsonify(user_uploaded_data)

def redis_listener():
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("job_updates", "job_in_progress")

    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"].decode("utf-8"))
            except Exception:
                data = {"raw": message["data"].decode("utf-8")}

            channel = message["channel"].decode("utf-8")
            
            if channel == "job_updates":
                socketio.emit("job_update", data)
            elif channel == "job_in_progress":
                socketio.emit("job_progress", data)


if __name__ == "__main__":
    threading.Thread(target=redis_listener, daemon=True).start()

    socketio.run(app, debug=True, port=5000)
