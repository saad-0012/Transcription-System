import mimetypes
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db.database import engine, Base
from app.api.router import router
import os

# --- FIX FOR WINDOWS JS MIME TYPE ---
mimetypes.init()
mimetypes.add_type('application/javascript', '.js')
# ------------------------------------

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vikaspedia Transcription System")

# Mount Static Files
# We use absolute paths to be safe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include API Router
app.include_router(router, prefix="/api")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})