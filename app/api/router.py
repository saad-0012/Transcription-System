
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import TranscriptionTask
from app.services.audio_processor import download_youtube_audio, extract_audio_from_file
from app.services.gemini_engine import transcribe_with_gemini
import shutil
import os
import uuid
from app.core.config import settings

router = APIRouter()

def process_transcription(task_id: int, db: Session):
    """Background task to handle heavy processing"""
    task = db.query(TranscriptionTask).filter(TranscriptionTask.id == task_id).first()
    if not task:
        return

    try:
        task.status = "processing"
        db.commit()

        audio_path = ""
        video_title = "Uploaded Video"

        # 1. Get Audio
        if task.video_source == "youtube":
            audio_path, video_title = download_youtube_audio(task.video_url, str(task_id))
        elif task.video_source == "upload":
            audio_path = extract_audio_from_file(task.file_path, str(task_id))
        
        task.video_title = video_title
        db.commit()

        # 2. Transcribe (Gemini)
        result = transcribe_with_gemini(audio_path, task.language)
        
        # 3. Save Results
        task.transcript_json = result["segments"]
        task.summary = result["summary"]
        task.raw_text = result["raw_text"]
        task.status = "completed"
        db.commit()
        
        # Cleanup audio
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        print(f"Task Failed: {e}")
        task.status = "failed"
        task.raw_text = str(e)
        db.commit()

@router.post("/transcribe/youtube")
async def transcribe_youtube(
    url: str = Form(...), 
    language: str = Form("en"), 
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    task = TranscriptionTask(
        video_source="youtube",
        video_url=url,
        language=language
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(process_transcription, task.id, db)
    return {"task_id": task.id, "status": "pending"}

@router.post("/transcribe/upload")
async def transcribe_upload(
    file: UploadFile = File(...), 
    language: str = Form("en"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    # Save file temporarily
    file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    task = TranscriptionTask(
        video_source="upload",
        file_path=file_path,
        video_title=file.filename,
        language=language
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(process_transcription, task.id, db)
    return {"task_id": task.id, "status": "pending"}

@router.get("/status/{task_id}")
def get_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TranscriptionTask).filter(TranscriptionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id, 
        "status": task.status, 
        "video_title": task.video_title,
        "transcript": task.transcript_json,
        "summary": task.summary
    }

@router.post("/update/{task_id}")
async def update_transcript(task_id: int, payload: dict, db: Session = Depends(get_db)):
    task = db.query(TranscriptionTask).filter(TranscriptionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Payload expected: {"segments": [...]}
    if "segments" in payload:
        task.transcript_json = payload["segments"]
        db.commit()
        return {"status": "success"}
    return {"status": "no change"}
