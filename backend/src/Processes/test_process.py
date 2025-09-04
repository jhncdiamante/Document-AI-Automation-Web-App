
from backend.src.Data.Redis import redis_conn
from datetime import datetime
import json

def test_process_job(job_id, job_data):
    
    import time
    time.sleep(10)

    redis_conn.publish("job_in_progress", json.dumps({
        "id": job_id,
        "status": "processing"
    }))

    import time
    time.sleep(20)
    result = {
        "id": job_id,
        "status": "completed",
        "accuracy": "90%",
        "issues": [],
        "completed_at": str(datetime.now().strftime("%Y-%m-%d %I:%M %p %z"))
    }
    print(result)
    redis_conn.publish("job_updates", json.dumps(result))