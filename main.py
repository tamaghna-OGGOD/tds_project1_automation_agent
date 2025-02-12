from fastapi import FastAPI, HTTPException
from typing import Optional
import os
import json
from pathlib import Path
import requests
import subprocess
import aiohttp
import asyncio

app = FastAPI()

class TaskExecutor:
    def __init__(self):
        self.ai_proxy_token = os.environ.get("AIPROXY_TOKEN")
        if not self.ai_proxy_token:
            raise ValueError("AIPROXY_TOKEN environment variable not set")
        
    async def execute_task(self, task_description: str):
        # First, use LLM to understand the task
        task_type = await self.classify_task(task_description)
        
        try:
            if task_type == "format_markdown":
                await self.format_markdown_task(task_description)
            elif task_type == "count_weekdays":
                await self.count_weekdays_task(task_description)
            # Add more task types here
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def classify_task(self, task_description: str):
        # Call GPT-4o-Mini to classify the task
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.aiproxy.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.ai_proxy_token}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Classify the task into one of these categories: format_markdown, count_weekdays, sort_contacts, etc."},
                        {"role": "user", "content": task_description}
                    ]
                }
            ) as response:
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

executor = TaskExecutor()

@app.post("/run")
async def run_task(task: str):
    try:
        result = await executor.execute_task(task)
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