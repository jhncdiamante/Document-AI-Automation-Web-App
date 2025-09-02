from redis import Redis
from rq import Queue
import uuid
from datetime import datetime
from backend.src.Processes.Job import Job
from typing import Dict
from flask_socketio import SocketIO, emit
from backend.src.Processes.test_process import test_process_job

class JobManager:
    def __init__(self):
        redis_conn = Redis(host="localhost", port=6379)
        self.queue = Queue(connection=redis_conn)
        self.active_jobs: Dict[str, Job] = {}

    def create_job(self, job_data: dict) -> str:
        job_id = str(uuid.uuid4())
        job = Job(
            funeral_branch=job_data.get("branch"),
            case_number=job_data.get("case_number"),
            job_id=job_id,
            selected_feature=job_data.get("feature"),
            files=job_data.get("files_saved"),
            status="queued",
            created_at=job_data.get("created_at"),

        )
        self.active_jobs[job_id] = job
        return job_id

    def push_job(self, job_id: str):
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self.active_jobs[job_id]
        if job.status != "queued":
            raise ValueError(f"Job {job_id} already started or finished")

        rq_job = self.queue.enqueue(test_process_job, job_id, job)
        return rq_job.id

    