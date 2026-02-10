
import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    print("Starting Vikaspedia Transcription System...")
    print("Ensure you have set your GOOGLE_API_KEY in the .env file.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
