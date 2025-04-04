from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from study_buddy_api.db import engine, Base 
from study_buddy_api.routers import studentinfo, friendslist, subjects, users, meetings  # Import your routers
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI()

# Enable CORS (for frontend access, like your HTML pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template directory (only needed if you're using Jinja2 templates)
templates = Jinja2Templates(directory="templates")

# Mount routers with optional prefixes
app.include_router(studentinfo.router)
app.include_router(friendslist.router)
app.include_router(subjects.router)
app.include_router(users.router)
app.include_router(meetings.router)

# Optional root test endpoint
@app.get("/")
def root():
    return {"message": "Study Buddy API is running"}