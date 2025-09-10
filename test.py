# test_job.py - run this as a separate script
from backend.src.Data.Redis import redis_conn
from rq import Queue
from x import simple_process_job

# Test with direct function
queue = Queue(connection=redis_conn)
from backend.src.Process.Job import Job

job_ref = Job(
            funeral_branch="1",
            case_number="123",
            job_id="2131231",
            selected_feature="General",
            files=[],
            status="queued",
            created_at="sadad",

        )
job = queue.enqueue(simple_process_job, job_ref)
print(f"Enqueued job: {job.id}")
print(f"Job func_name: {job.func_name}")