from pydantic import BaseModel
from typing import Optional

class FileObject(BaseModel):
    id: str
    bytes: int
    created_at: int
    filename: str
    object: str
    purpose: str
    status: str
    status_details: Optional[str] = None
    
    class Config:
        # Allow extra fields in case the API returns more data that isn't defined here
        extra = "allow"

