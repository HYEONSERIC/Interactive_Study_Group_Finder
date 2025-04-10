from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from db import engine, Base 
from routers import studentinfo, friendslist, subjects, users, meetings, groups, search  # Import your routers

# Template directory (only needed if you're using Jinja2 templates)
templates = Jinja2Templates(directory="templates")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI()

# ✅ Enable CORS for Live Server (port 5500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Live Server 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(studentinfo.router)
app.include_router(friendslist.router)
app.include_router(subjects.router)
app.include_router(users.router)
app.include_router(meetings.router)
app.include_router(groups.router)
app.include_router(search.router)
# Optional root test endpoint
@app.get("/")
def root():
    return {"message": "Study Buddy API is running"}
