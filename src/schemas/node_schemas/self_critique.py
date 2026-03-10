from pydantic import BaseModel, Field

class CritiqueOutput(BaseModel):
    status: str = Field(description="Must be strictly 'verified' or 'conflict'")
    feedback: str = Field(description="Feedback details or 'Approved'")