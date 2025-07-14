from fastapi import APIRouter, HTTPException
from app.models import Employee
from app.database import db
from app.utils import fix_id
from bson import ObjectId

router = APIRouter()

@router.post("/employees")
async def add_employee(employee: Employee):
    emp_dict = employee.dict()
    emp_dict["initials"] = "".join([w[0].upper() for w in emp_dict["name"].split()])[:2]
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
