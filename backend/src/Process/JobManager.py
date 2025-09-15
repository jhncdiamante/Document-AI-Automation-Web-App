from werkzeug.utils import secure_filename
import os
import uuid
import threading
import queue
from flask import jsonify
from flask_login import current_user

from backend.src.Models import Job as JobModel, Upload, db


class Jobs:
    def __init__(self, app, worker, socketio, worker_count=1):
        self.app = app
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = worker
        self.socketio = socketio

        # Start worker threads
        for _ in range(worker_count):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                job_id = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.app.app_context():
                job_record = self._fetch_job(job_id)
                if not job_record:
                    self.queue.task_done()
                    continue

                if job_record.status != "queued":
                    self.queue.task_done()
                    continue

                job_record.status = "processing"
                db.session.commit()

                try:
                    self.worker.process_job(job_record)  
                    job_record.status = "completed"
                except Exception as e:
                    job_record.status = "failed"
                    job_record.error = str(e)
                finally:
                    db.session.commit()
                    self.queue.task_done()

    def _fetch_job(self, job_id):
        with self.app.app_context():
            return JobModel.query.get(job_id)

    def stop(self, job_id: str):
        with self.app.app_context():
            job_record = self._fetch_job(job_id)
            if not job_record:
                return jsonify({"error": f"Job {job_id} not found."}), 400

            if job_record.status not in {"queued", "processing"}:
                return jsonify({"error": f"Job {job_id} already {job_record.status}"}), 400

            job_record.status = "canceled"
            db.session.commit()

            return jsonify({"success": f"Job {job_id} canceled successfully"})
 

    def add(self, request):
        files = request.files.getlist("files")
        saved_files = []

        with self.app.app_context():
            job_id = str(uuid.uuid4())

            case_number = request.form.get("case_number", "")

            branch = request.form.get("branch", "")
            description = request.form.get("description", "")
            feature = request.form.get("feature", "")

            if not all([branch, description, feature]):
                return jsonify({"error": "Failed to add job, missing at least one attribute."}), 400

            job_record = JobModel(
                id=job_id,
                case_number=case_number,
                branch=branch,
                description=description,
                status="queued",
                feature=feature,
                user_id=current_user.id,
            )
            db.session.add(job_record)
            db.session.commit()

            for file in files:
                original_filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                permanent_filepath = os.path.join(
                    self.app.config["UPLOAD_FOLDER"], unique_filename
                )
                file.save(permanent_filepath)
                saved_files.append(permanent_filepath)

                upload_record = Upload(
                    permanent_file_name=original_filename,
                    file_path=permanent_filepath,
                    job_id=job_id,
                    user_id=job_record.user_id,
                )
                db.session.add(upload_record)

            db.session.commit()

            # enqueue DB job_id only
            self.queue.put(job_id)

            self.socketio.emit(
                "new_job",
                {
                    "status": job_record.status,
                    "case_number": job_record.case_number,
                    "branch": job_record.branch,
                    "feature": job_record.feature,
                    "description": job_record.description,
                    "created_at": job_record.created_at.isoformat(),
                    "id": job_record.id,
                    "files": [file.filename for file in files]
                },
                room=f"user_{job_record.user_id}",
            )

            return jsonify({"success": "Successfully added job."}), 
            
    def delete(self, job_id):
        with self.app.app_context():
            job_record = self._fetch_job(job_id)
            if not job_record:
                return jsonify({"error": f"Job {job_id} not found."}), 400

            if job_record.status not in {"completed", "canceled", "failed"}:
                return jsonify(
                    {"error": f"Job {job_id} is still {job_record.status}, cannot delete"}
                ), 400

            for upload in job_record.uploads:
                if upload.file_path and os.path.exists(upload.file_path):
                    os.remove(upload.file_path)


            db.session.delete(job_record) 
            db.session.commit()

            return jsonify({"success": f"Job {job_id} deleted."})
        
