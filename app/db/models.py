
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.db.database import Base

class TranscriptionTask(Base):
    __tablename__ = "transcription_tasks"

    id = Column(Integer, primary_key=True, index=True)
    video_source = Column(String) # 'upload' or 'youtube'
    video_title = Column(String, nullable=True)
    video_url = Column(String, nullable=True) # For embedded videos
    file_path = Column(String, nullable=True) # For uploaded files
    language = Column(String, default="en")
    status = Column(String, default="pending") # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Stores the structured transcript JSON: [{"start": 0.0, "end": 2.5, "text": "...", "speaker": "Speaker 1"}]
    transcript_json = Column(JSON, nullable=True) 
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
