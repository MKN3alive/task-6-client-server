from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import math
import uuid
import json
import os

app = FastAPI(title="Function Inference Server")

STORAGE_FILE = "functions.json"

# ---------- Models ----------

class FunctionCreate(BaseModel):
    name: str
    expression: str
    params: Dict[str, float]


class Function(FunctionCreate):
    id: str


class ComputeRequest(BaseModel):
    x: float


class ComputeResponse(BaseModel):
    y: float


# ---------- Storage (in-memory) ----------

functions: Dict[str, Function] = {}      # id -> Function
functions_by_name: Dict[str, str] = {}   # name -> id

SAFE_GLOBALS = {
    "__builtins__": {},
    "math": math
}

# ---------- Persistence ----------

def save_to_disk():
    data = [func.dict() for func in functions.values()]
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_from_disk():
    if not os.path.exists(STORAGE_FILE):
        return

    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        func = Function(**item)
        functions[func.id] = func
        functions_by_name[func.name] = func.id


# ---------- Startup ----------

@app.on_event("startup")
async def startup_event():
    load_from_disk()


# ---------- CRUD ----------

@app.post("/functions", response_model=Function)
async def create_function(f: FunctionCreate):
    if f.name in functions_by_name:
        raise HTTPException(status_code=400, detail="Function name already exists")

    fid = str(uuid.uuid4())
    func = Function(id=fid, **f.dict())

    functions[fid] = func
    functions_by_name[f.name] = fid
    save_to_disk()

    return func


@app.get("/functions", response_model=List[Function])
async def list_functions():
    return list(functions.values())


@app.get("/functions/{fid}")
async def get_function(fid: str):
    if fid not in functions:
        raise HTTPException(status_code=404, detail="Function not found")
    func = functions[fid]
    return {
        "id": func.id,
        "name": func.name,
        "expression": func.expression,
        "params": func.params,
        "inputs": ["x"],
        "outputs": ["y"]
    }

@app.get("/functions/by-name/{name}")
async def get_function_by_name(name: str):
    if name not in functions_by_name:
        raise HTTPException(status_code=404, detail="Function not found")
    fid = functions_by_name[name]
    func = functions[fid]
    return {
        "id": func.id,
        "name": func.name,
        "expression": func.expression,
        "params": func.params,
        "inputs": ["x"],
        "outputs": ["y"]
    }



@app.delete("/functions/{fid}")
async def delete_function(fid: str):
    if fid not in functions:
        raise HTTPException(status_code=404, detail="Function not found")

    name = functions[fid].name
    del functions[fid]
    del functions_by_name[name]
    save_to_disk()

    return {"status": "deleted"}


@app.delete("/functions/by-name/{name}")
async def delete_function_by_name(name: str):
    if name not in functions_by_name:
        raise HTTPException(status_code=404, detail="Function not found")

    fid = functions_by_name[name]
    del functions_by_name[name]
    del functions[fid]
    save_to_disk()

    return {"status": "deleted"}

# ---------- Compute ----------

@app.post("/functions/{fid}/compute", response_model=ComputeResponse)
async def compute(fid: str, req: ComputeRequest):
    if fid not in functions:
        raise HTTPException(status_code=404, detail="Function not found")

    func = functions[fid]
    local_env = {"x": req.x, **func.params}

    try:
        y = eval(func.expression, SAFE_GLOBALS, local_env)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ComputeResponse(y=y)


@app.post("/functions/by-name/{name}/compute", response_model=ComputeResponse)
async def compute_by_name(name: str, req: ComputeRequest):
    if name not in functions_by_name:
        raise HTTPException(status_code=404, detail="Function not found")

    fid = functions_by_name[name]
    func = functions[fid]
    local_env = {"x": req.x, **func.params}

    try:
        y = eval(func.expression, SAFE_GLOBALS, local_env)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ComputeResponse(y=y)
