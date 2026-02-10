
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Vikaspedia Automated Transcription"
    VERSION = "1.0.0"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vikaspedia.db")
    UPLOAD_DIR = os.path.join(os.getcwd(), "storage", "uploads")
    AUDIO_DIR = os.path.join(os.getcwd(), "storage", "audio")

    def __init__(self):
        if not os.path.exists(self.UPLOAD_DIR):
            os.makedirs(self.UPLOAD_DIR)
        if not os.path.exists(self.AUDIO_DIR):
            os.makedirs(self.AUDIO_DIR)

settings = Settings()
