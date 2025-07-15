from pydantic import BaseModel
from typing import Optional, List

class WorkEntry(BaseModel):
    date: str
    work: str
    rate_per_unit: float
    no_of_units: int
    amount: float
    deposit_or_due: Optional[float] = 0.0

class Employee(BaseModel):
    name: str
    title: str = "New Designation"
    earned: float = 0.0
    initials: Optional[str] = None
    image: Optional[str] = None
    work_entries: List[WorkEntry] = []  # New field added
