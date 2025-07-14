from pydantic import BaseModel

class RunJobRequest(BaseModel):
    wsi_id: str
    tool_name: str

class JobStatusResponse(BaseModel):
    wsi_id: str
    tool_name: str
    status: str
