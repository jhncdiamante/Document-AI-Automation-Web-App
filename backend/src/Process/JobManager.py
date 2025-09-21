import os
import uuid
import eventlet
eventlet.monkey_patch()

from flask import jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.Models import Job as JobModel, Upload, db

class Jobs:
    def __init__(self, app, worker, socketio, worker_count=2):
        self.app = app
        self.worker = worker
        self.socketio = socketio
        self.queue = eventlet.queue.LightQueue()
        
        with app.app_context():
            self.SessionLocal = sessionmaker(bind=db.engine)

        # Spawn lightweight worker greenlets
        for i in range(worker_count):
            eventlet.spawn(self._worker_loop, f"worker-{i}")

    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _worker_loop(self, worker_name):
        """
        Ultra-lightweight worker loop that just dispatches to the thread pool
        """
        print(f"[JobManager] {worker_name} started")
        
        while True:
            try:
                # Get job ID from queue (this blocks but doesn't block other greenlets)
                job_id = self.queue.get()
                print(f"[JobManager] {worker_name} picked up job {job_id}")
                
                # Immediately dispatch to worker thread pool (non-blocking)
                eventlet.spawn_n(self._dispatch_job, job_id, worker_name)
                
                # Small yield to let other greenlets run
                eventlet.sleep(0.01)
                
            except Exception as e:
                print(f"[JobManager] {worker_name} error: {e}")
                eventlet.sleep(1)  # Wait before retrying

    def _dispatch_job(self, job_id, worker_name):
        """
        Lightweight job dispatcher - just gets job record and hands off to worker
        """
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_record = session.get(JobModel, job_id)
                    
                    if not job_record:
                        print(f"[JobManager] {worker_name}: Job {job_id} not found")
                        return
                        
                    if job_record.status != "queued":
                        print(f"[JobManager] {worker_name}: Job {job_id} status is {job_record.status}, skipping")
                        return
                    
                    print(f"[JobManager] {worker_name}: Dispatching job {job_id} to worker thread pool")
                    
                    # Hand off to worker thread pool (completely non-blocking)
                    self.worker.process_job(job_record)
                    
        except Exception as e:
            print(f"[JobManager] {worker_name}: Error dispatching job {job_id}: {e}")
            
            # Try to mark job as failed
            try:
                with self.app.app_context():
                    with self.get_db_session() as session:
                        job = session.get(JobModel, job_id)
                        if job:
                            job.status = "failed"
                            job.error = f"Dispatch error: {str(e)}"
                            session.commit()
                            
                            # Emit failure
                            eventlet.spawn_n(self._emit_job_failed, job.id, job.user_id, str(e))
            except Exception as cleanup_error:
                print(f"[JobManager] {worker_name}: Error during cleanup: {cleanup_error}")

    def _emit_job_failed(self, job_id, user_id, error_msg):
        """Emit job failure in a separate greenlet"""
        try:
            self.socketio.emit(
                "job_failed",
                {
                    "id": job_id,
                    "status": "failed",
                    "error": error_msg,
                    "user_id": user_id
                },
                room=f"user_{user_id}"
            )
        except Exception as e:
            print(f"[JobManager] Error emitting job failure: {e}")

    def add(self, request):
        """
        Add a new job - keep this as lightweight as possible
        """
        try:
            files = request.files.getlist("files")
            
            # Validate required fields immediately
            branch = request.form.get("branch", "").strip()
            feature = request.form.get("feature", "").strip()
            
            if not branch or not feature:
                return jsonify({"error": "Missing branch or feature"}), 400

            # Quick file validation
            if not files or not any(f.filename for f in files):
                return jsonify({"error": "No files provided"}), 400

            job_id = str(uuid.uuid4())
            
            with self.app.app_context():
                with self.get_db_session() as session:
                    # Create job record
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
                    session.flush()  # Get the created_at timestamp
                    created_at = job_record.created_at

                    # Handle file uploads
                    uploaded_files = []
                    for file in files:
                        if file.filename:
                            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                            filepath = os.path.join(self.app.config["UPLOAD_FOLDER"], unique_filename)
                            filepath = os.path.normpath(filepath)
                            
                            # Save file
                            file.save(filepath)
                            
                            upload_record = Upload(
                                permanent_file_name=file.filename,
                                file_path=filepath,
                                job_id=job_id,
                                user_id=current_user.id
                            )
                            session.add(upload_record)
                            uploaded_files.append(file.filename)

                    session.commit()

            # Add to queue for processing
            self.queue.put(job_id)
            print(f"[JobManager] Job {job_id} queued successfully")

            # Emit to frontend (non-blocking)
            eventlet.spawn_n(self._emit_new_job, {
                "id": job_id,
                "status": "queued",
                "files": uploaded_files,
                "created_at": created_at.isoformat(),
                "case_number": request.form.get("case_number", ""),
                "branch": branch,
                "feature": feature,
                "user_id": current_user.id
            })

            return jsonify({
                "success": "Job added successfully",
                "job_id": job_id
            }), 200

        except Exception as e:
            print(f"[JobManager] Error adding job: {e}")
            return jsonify({"error": f"Failed to add job: {str(e)}"}), 500

    def _emit_new_job(self, job_data):
        """Emit new job event in separate greenlet"""
        try:
            self.socketio.emit(
                "new_job",
                job_data,
                room=f"user_{job_data['user_id']}"
            )
        except Exception as e:
            print(f"[JobManager] Error emitting new job: {e}")

    def stop(self, job_id: str):
        """Cancel a job - keep lightweight"""
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_record = session.get(JobModel, job_id)
                    
                    if not job_record:
                        return jsonify({"error": f"Job {job_id} not found."}), 400
                        
                    if job_record.status not in {"queued", "processing"}:
                        return jsonify({
                            "error": f"Job {job_id} is {job_record.status}, cannot cancel"
                        }), 400
                    
                    job_record.status = "canceled"
                    session.commit()
                    
                    # Emit cancellation (non-blocking)
                    eventlet.spawn_n(self._emit_job_update, {
                        "id": job_id,
                        "status": "canceled",
                        "user_id": job_record.user_id
                    })
                    
                    return jsonify({"success": f"Job {job_id} canceled successfully"})
                    
        except Exception as e:
            print(f"[JobManager] Error canceling job {job_id}: {e}")
            return jsonify({"error": f"Failed to cancel job: {str(e)}"}), 500

    def _emit_job_update(self, update_data):
        """Emit job update in separate greenlet"""
        try:
            self.socketio.emit(
                "job_update",
                update_data,
                room=f"user_{update_data['user_id']}"
            )
        except Exception as e:
            print(f"[JobManager] Error emitting job update: {e}")

    def delete(self, job_id):
        """Delete a completed/failed job"""
        try:
            with self.app.app_context():
                with self.get_db_session() as session:
                    job_record = session.get(JobModel, job_id)
                    
                    if not job_record:
                        return jsonify({"error": f"Job {job_id} not found."}), 400
                        
                    if job_record.status not in {"completed", "canceled", "failed"}:
                        return jsonify({
                            "error": f"Job {job_id} is still {job_record.status}, cannot delete"
                        }), 400
                    
                    # Delete associated files (in background)
                    file_paths = [upload.file_path for upload in job_record.uploads]
                    eventlet.spawn_n(self._cleanup_files, file_paths)
                    
                    session.delete(job_record)
                    session.commit()
                    
                    return jsonify({"success": f"Job {job_id} deleted successfully"})
                    
        except Exception as e:
            print(f"[JobManager] Error deleting job {job_id}: {e}")
            return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500

    def _cleanup_files(self, file_paths):
        """Clean up files in background"""
        for filepath in file_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"[JobManager] Deleted file: {filepath}")
            except Exception as e:
                print(f"[JobManager] Warning: Could not delete file {filepath}: {e}")

    def shutdown(self):
        """Shutdown the job manager"""
        print("[JobManager] Shutting down...")
        self.worker.shutdown()