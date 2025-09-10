
from pydantic import BaseModel

class DocumentAuditResultSchema(BaseModel):
    issues: list[str]
    accuracy: int