def fix_id(emp):
    emp["id"] = str(emp["_id"])
    del emp["_id"]
    return emp
