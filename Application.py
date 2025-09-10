
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from backend.src.Process.JobManager import Jobs
from backend.src.Process.Worker import Worker

from flask_socketio import SocketIO, emit
import threading, json


UPLOAD_FOLDER = 'userdata/uploads' 

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*")
worker = Worker(socketio=socketio)

jobs = Jobs(app, worker)




@app.route("/user/add_job", methods=["POST"])
def add_job():
    job = jobs.add(request)

    socketio.emit("new_job", 
        {
            "status": job.status,
            "case_number": job.case_number,
            "branch": job.funeral_branch,
            "feature": job.selected_feature,
            "description": "",
            "created_at": job.created_at,
            "files": job.files,
            "id": job.job_id,
        })

    return jsonify({"result":"Success"})



@app.route("/user/jobs/<job_id>/stop", methods=["POST"])
def stop_job(job_id):
   return jobs.stop(job_id)

@app.route("/user/jobs/<job_id>/delete", methods=["DELETE"])
def delete_job(job_id):
    return jobs.delete(job_id)



if __name__ == "__main__":

    socketio.run(app, debug=True, port=5000, use_reloader=False)
