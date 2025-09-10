from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from backend.src.Process.Job import Job
import threading
import queue
from flask import jsonify


class Jobs:
    def __init__(self, app, worker, worker_count=1):
        self.app = app
        self.queue = queue.Queue()
        self.entries = {}  # store job_id -> Job
        self.stop_event = threading.Event()
        self.worker = worker

        # Start worker threads
        for i in range(worker_count):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                job = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            if job.status != "queued":
                print("Job is not queued.")
                self.queue.task_done()
                continue

            job.status = "processing"
            try:
                self.worker.process_job(job)  # your function
                job.status = "finished"
            except Exception as e:
                print(str(e))
                job.status = "failed"
                job.error = str(e)
            finally:
                self.queue.task_done()

    def _fetch_job(self, job_id):
        return self.entries.get(job_id)

    def stop(self, job_id: str):
        job = self._fetch_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found."}), 400

        if job.status not in {"queued", "started"}:
            return jsonify({"error": f"Job {job_id} already {job.status}"}), 400

        # Mark job canceled
        job.status = "canceled"
        return jsonify({"message": f"Job {job_id} canceled successfully"})

    def add(self, request) -> Job:
        files = request.files.getlist("files")
        saved_files = []

        for file in files:
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            permanent_filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(permanent_filepath)
            saved_files.append(permanent_filepath)

        job_id = str(uuid.uuid4())
        job = Job(
            funeral_branch=request.form.get("branch"),
            case_number=request.form.get("case_number"),
            job_id=job_id,
            selected_feature=request.form.get("feature"),
            files=saved_files,
            status="queued",
            created_at=request.form.get("created_at") or datetime.now(),
        )

        self.entries[job_id] = job
        self.queue.put(job)
        print("Successfully add to queue.")
        return job

    def delete(self, job_id):
        job = self._fetch_job(job_id)
        if not job:
            return jsonify({"error": f"Job {job_id} not found."}), 400

        if job.status in {"finished", "canceled", "failed"}:
            del self.entries[job_id]
            return jsonify({"success": f"Job {job_id} deleted."})
        else:
            return jsonify({"error": f"Job {job_id} is still {job.status}, cannot delete"}), 400
