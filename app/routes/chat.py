from fastapi import APIRouter
from app.ai.prompt.model import models
from app.ai.prompt.falltry import fallback
from fastapi import UploadFile
from app.ai.prompt.file import file_ops

router = APIRouter()

@router.post("/llm")
async def llm_chat(prompt: str):

    return await fallback(prompt = prompt)
    
@router.post("/file")
async def upload_file(file: UploadFile):
    
    return await file_ops.prompt_extract(file)
