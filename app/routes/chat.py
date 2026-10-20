from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
from app.ai.model import models
from app.ai.falltry import fallback, fallback_stream
from app.ai.file import file_ops

router = APIRouter()

@router.post("/llm")
async def llm_chat(prompt: str):
    return await fallback(prompt=prompt)

@router.post("/stream")
async def stream_chat(prompt: str):
    return StreamingResponse(fallback_stream(prompt), media_type="text/plain")

@router.post("/file")
async def upload_file(file: UploadFile):
    return await file_ops.prompt_extract(file)
