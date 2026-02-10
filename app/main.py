
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db.database import engine, Base
from app.api.router import router
import os

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vikaspedia Transcription System")

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API Router
app.include_router(router, prefix="/api")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
