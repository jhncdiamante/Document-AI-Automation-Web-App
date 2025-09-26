import os
import uuid
import traceback
from flask import jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from rq import Queue

from src.Models import Job as JobModel, Upload, db

from src.Process.Worker import Worker
worker = Worker()

def process_job(job_id):
    """
    Global RQ-compatible function.
    """
    print("Starting the process_job function")
    worker.process_job(job_id)

class Jobs:
    def __init__(self, app, socketio, queue: Queue = None):
        self.app = app
        self.socketio = socketio
        self.queue = queue

        # SQLAlchemy session factory
        with app.app_context():
            self.SessionLocal = sessionmaker(bind=db.engine)

    @contextmanager
    def get_db_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add(self, request):
        """Add a new job and enqueue it in Redis"""
        try:
            files = request.files.getlist("files")
            branch = request.form.get("branch", "").strip()
            feature = request.form.get("feature", "").strip()

            if not branch or not feature:
                return jsonify({"error": "Missing branch or feature"}), 400
            if not files or not any(f.filename for f in files):
                return jsonify({"error": "No files provided"}), 400

            job_id = str(uuid.uuid4())
            uploaded_files = []

            with self.app.app_context():
                with self.get_db_session() as session:
                    job_record = JobModel(
                        id=job_id,
                        case_number=request.form.get("case_number", "").strip(),
                        branch=branch,
                        status="queued",
                        feature=feature,
                        user_id=current_user.id,
                        description=request.form.get("description", "").strip()
                    )
                    session.add(job_record)
                    session.flush()
                    created_at = job_record.created_at

                    # Save uploaded files
                    for file in files:
                        if file.filename:
                            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                            filepath = os.path.join(self.app.config["UPLOAD_FOLDER"], unique_filename)
                            file.save(os.path.normpath(filepath))
                            upload_record = Upload(
                                permanent_file_name=file.filename,
                                file_path=filepath,
                                job_id=job_id,
                                user_id=current_user.id
                            )
                            session.add(upload_record)
                            uploaded_files.append(file.filename)
                    session.commit()

            # Enqueue job into Redis Queue
            self.queue.enqueue(process_job, job_id, job_timeout=4000)
            print(f"[JobManager] Job {job_id} enqueued successfully in Redis")

            job_data = {
                "id": job_id,
                "status": "queued",
                "files": uploaded_files,
                "created_at": created_at.isoformat(),
                "case_number": request.form.get("case_number", ""),
                "branch": branch,
                "feature": feature,
                "user_id": current_user.id
            }
            self._emit_new_job(job_data)
            return jsonify({"success": "Job added successfully", "job_id": job_id}), 200

        except Exception as e:
            print(f"[JobManager] Error adding job: {e}")
            traceback.print_exc()
            return jsonify({"error": f"Failed to add job: {str(e)}"}), 500

    def stop(self, job_id: str):
        """Mark job as canceled in DB (Redis worker will respect this)"""
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    job = session.get(JobModel, job_id)
                    if not job:
                        return jsonify({"error": f"Job {job_id} not found."}), 400
                    if job.status not in {"queued", "processing"}:
                        return jsonify({"error": f"Job {job_id} is {job.status}, cannot cancel"}), 400
                    job.status = "canceled"
                    session.commit()
                    self._emit_job_update({"id": job_id, "status": "canceled", "user_id": job.user_id})
                    return jsonify({"success": f"Job {job_id} canceled successfully"})
        except Exception as e:
            return jsonify({"error": f"Failed to cancel job: {str(e)}"}), 500

    def delete(self, job_id: str):
        """Delete a completed/failed/canceled job"""
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    job = session.get(JobModel, job_id)
                    if not job:
                        return jsonify({"error": f"Job {job_id} not found."}), 400
                    if job.status not in {"completed", "failed", "canceled"}:
                        return jsonify({"error": f"Job {job_id} is still {job.status}, cannot delete"}), 400
                    file_paths = [u.file_path for u in job.uploads]
                    for fp in file_paths:
                        try:
                            os.remove(fp)
                        except:
                            pass
                    session.delete(job)
                    session.commit()
                    return jsonify({"success": f"Job {job_id} deleted successfully"})
        except Exception as e:
            return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500

    # --- SocketIO helpers ---
    def _emit_new_job(self, job_data):
        try:
            room = f"user_{job_data['user_id']}"
            self.socketio.emit("new_job", job_data, room=room)
        except Exception as e:
            print(f"[JobManager] Error emitting new_job: {e}")

    def _emit_job_update(self, update_data):
        try:
            room = f"user_{update_data['user_id']}"
            self.socketio.emit("job_update", update_data, room=room)
        except Exception as e:
            print(f"[JobManager] Error emitting job_update: {e}")

    def _emit_job_failed(self, job_id, user_id, error_msg):
        try:
            room = f"user_{user_id}"
            self.socketio.emit(
                "job_failed",
                {"id": job_id, "status": "failed", "error": error_msg, "user_id": user_id},
                room=room
            )
        except Exception as e:
            print(f"[JobManager] Error emitting job_failed: {e}")

    def get_all(self, user_id):
        """Fetch all jobs for a user"""
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    jobs_list = session.query(JobModel).filter_by(user_id=user_id).all()
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
            print(f"[JobManager] Error fetching jobs: {e}")
            return jsonify({"error": "Failed to fetch jobs"}), 500
