from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .pipeline import execute_pipeline

app = FastAPI(
    title="PII masking service",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: List[str]

@app.get("/")
async def text():
    return ("hello")

@app.post("/text")
async def process_text(request: TextRequest):
    response = execute_pipeline(request.text)
    return {"message": response}
