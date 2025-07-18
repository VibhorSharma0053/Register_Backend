# app/routes/employees.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from app.database import db
from fastapi.responses import FileResponse
import os
from datetime import datetime
from fpdf import FPDF
from app.models import Employee, WorkEntry
from app.utils import fix_id

router = APIRouter()

# Helper for ObjectId
def fix_id(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

# Request model for updating entries
class UpdateEntriesModel(BaseModel):
    work_entries: List[WorkEntry]
    earned: float

@router.post("/employees")
async def add_employee(employee: Employee):
    emp_dict = employee.dict()
    emp_dict["initials"] = "".join([w[0].upper() for w in emp_dict["name"].split()])[:2]
    emp_dict["work_entries"] = []
    emp_dict["earned"] = 0
    res = await db.employees.insert_one(emp_dict)
    new_emp = await db.employees.find_one({"_id": res.inserted_id})
    return fix_id(new_emp)

@router.get("/employees")
async def get_employees():
    employees = await db.employees.find().to_list(100)
    return [fix_id(emp) for emp in employees]

@router.get("/employees/{id}")
async def get_employees_by_id(id: str):
    employee = await db.employees.find_one({"_id": ObjectId(id)})
    return fix_id(employee)

@router.delete("/employees/{id}")
async def delete_employee(id: str):
    res = await db.employees.delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"status": "deleted"}

# ✅ Save entries to employee by ID
@router.put("/employees/{employee_id}")
async def update_employee_entries(employee_id: str, update: UpdateEntriesModel):
    result = await db.employees.update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": {"work_entries": [e.dict() for e in update.work_entries], "earned": update.earned}},
    )
    if result.modified_count:
        return {"msg": "Entries updated"}
    raise HTTPException(status_code=404, detail="Employee not found")

# 📄 Generate PDF Summary
@router.get("/employees/{employee_id}/download")
async def download_employee_pdf(employee_id: str):
    employee = await db.employees.find_one({"_id": ObjectId(employee_id)})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    name = employee.get("name", "Unknown")
    entries = employee.get("work_entries", [])
    total_earned = employee.get("earned", 0.0)

    pdf = FPDF()
    pdf.add_page()
    # pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    
    # Register a Unicode-capable font (DejaVuSans.ttf should be in your project folder)
    # font_path = "DejaVuSans.ttf"  # download if not present
    # pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(200, 10, txt=f"Work Summary - {name}", ln=1, align='C')
    pdf.ln(5)

    for i, e in enumerate(entries, 1):
        rate = e.get("rate_per_unit", 0)
        units = e.get("no_of_units", 0)
        amount = rate * units
        deposited = e.get("deposit_or_due", 0)

        entry_text = (
            f"{i}. Date: {e.get('date')}\n"
            f"   Work: {e.get('work')}\n"
            f"   Rate: Rs. {rate}/unit | Units: {units}\n"
            f"   Amount: Rs. {amount} | Deposited/Due: Rs.{deposited}\n"
        )
        pdf.multi_cell(0, 8, txt=entry_text)
        pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=f"Total Earned: Rs.{total_earned:.2f}", ln=1)

    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{employee_id}_summary.pdf"
    pdf.output(file_path)

    return FileResponse(file_path, filename=f"{name}_summary.pdf")
