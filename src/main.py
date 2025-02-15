from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tasks import TaskExecutor
from pathlib import Path


app = FastAPI()
executor = TaskExecutor()

class TaskRequest(BaseModel):
    task: str

@app.post("/run")
async def run_task(request: TaskRequest):
    try:
        await executor.install_and_run_datagen_task("tamaghna.saha@gramener.com")
        result = await executor.execute_task(request.task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    try:
        if not path.startswith("/data/"):
            raise HTTPException(status_code=400, detail="Can only access files in /data directory")
        file_path = Path(path)
        if not file_path.exists():
            raise HTTPException(status_code=404)
        with open(file_path) as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))