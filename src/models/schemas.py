from pydantic import BaseModel
from typing import Optional, List

class JobDescription(BaseModel):
    url: str

class Rating(BaseModel):
    score: float
    markdown_response: str
