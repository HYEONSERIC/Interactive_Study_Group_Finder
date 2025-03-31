from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Enum, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pydantic import BaseModel
import mysql.connector
import bcrypt
import jwt
import os
from fastapi import Query
from typing import List
from fastapi import Form
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# Secret key for JWT
SECRET_KEY = "MostSecretof_keys!"
ALGORITHM = "HS256"

# Database Configuration
DATABASE_URL = "mysql+mysqlconnector://root:Iondragonfly23!@localhost:3306/soft_project"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# FastAPI Instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any domain (for testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Model #
#this is where each table from the database is defined. these will be wonky and throw errors and may
#need definition added like the UserCreate(BaseModel). The javascript to sql conversion gets confused
#so that was added to get uniformity when creating a user. 

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class StudentInformation(Base):
    __tablename__ = "student_information"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
class StudyGroups(Base):
    __tablename__ = "study_groups"

    group_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_name = Column(String(255), nullable=False)
    subject_id = Column(String(255), ForeignKey("available_subjects.id"))
    level_of_study = Column(String(255))
    group_owner_id = Column(String(255),ForeignKey("student_information.id"))

class StudentAvailability(Base):
    __tablename__ = "student_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_information.id"), nullable=False) 
    day_of_week = Column(Enum("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    timezone = Column(String(50), default="UTC")

class AvailableSubjects(Base):
    __tablename__ = "available_subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_name = Column(String(255), unique=True, nullable=False)
class StudentUpdateRequest(BaseModel):
    name: str
    email: str

class StudentResponse(BaseModel):
    name: str
    email: str

class PostQuery(BaseModel):
    query_str: str


# Create Tables (If a table gets deleted this will create them as long there is a connection to the DB.)
Base.metadata.create_all(bind=engine)

#               #
# API ENDPOINTS #
#               #

# TESTING
# API Endpoint - Test Connection
@app.get("/")
def read_root():
    return {"message": "FastAPI is running and connected to MySQL"}

#USER INFORMATION
# API Endpoint - Get Users
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(StudentInformation).all()
    return users

# API Endpoint - Create User
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    password_hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = StudentInformation(name=user.name, email=user.email, password_hash=password_hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

#LOGIN
# API Endpoint - Login verification
@app.post("/login") 
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == request.email).first()
    if not user or not bcrypt.checkpw(request.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT token
    token_payload = {"sub": user.email,"username": user.name, "exp": datetime.now() + timedelta(hours=1)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"token": token, "message": "Login successful"}


# SUBJECTS
# API Endpoint - all subjects in available_subjects
@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(AvailableSubjects).all()
    return subjects

# API Endpoint - add subject
@app.post("/subjects")
def add_subject(subject_name: str, db: Session = Depends(get_db)):
    new_subject = AvailableSubjects(subject_name=subject_name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject



# student_information
@app.get("/students", response_model=List[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(StudentInformation).all()
    if not students:
        raise HTTPException(status_code=404, detail="No students found")

    return [StudentResponse(name=student.name, email=student.email) for student in students]

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdateRequest, db: Session = Depends(get_db)):
    db_student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db_student.name = student.name
    db_student.email = student.email
    db.commit()
    return db_student

@app.post("/students/{student_id}")
def update_student_profile(student_id: int, name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.name = name
    student.email = email
    db.commit()
    return {"message": "Profile updated successfully"}

templates = Jinja2Templates(directory="templates")  

@app.get("/student_info/{student_id}", response_class=HTMLResponse)
def get_student_info_page(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("student_info.html", {"request": request, "student": student}) 

@app.get("/get_student_id")
def get_student_id(email: str, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id}

@app.get("/view-profile/{username}}", response_class=HTMLResponse)
def get_view_profile_page(username: str, request: Request, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.name == username).first()
    if not student:
        raise HTTPException(status_code=406, detail="Student not found")
    return templates.TemplateResponse("view-profile.html", {"request": request, "student": student}) 

@app.post("/view-profile")
def get_profile_info(student: PostQuery, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.name == student.query_str).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found") 
    return student

@app.post("/study-groups")
def get_profile_info(query: PostQuery, db: Session = Depends(get_db)):
    groups = db.query(StudyGroups).filter(StudyGroups.group_name.contains(query.query_str)).all()
    if not groups:
        return {"error": "No study groups found matching criteria."}
    response = {}
    x=0
    for group in groups:
        response[f'{x}'] = group
        x+=1
    return response