from pydantic import BaseModel
from typing import Optional

class Employee(BaseModel):
    name: str
    title: str = "New Designation"
    earned: float = 0.0
    image: Optional[str] = None
    initials: Optional[str] = None
