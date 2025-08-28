from dataclasses import dataclass

@dataclass
class Job:
    funeral_branch: str
    case_number: str
    job_id: str
    selected_feature: str
    files: list
    status: str
    document_type: str
    

