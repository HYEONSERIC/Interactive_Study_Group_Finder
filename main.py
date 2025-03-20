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
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List

# Secret key for JWT
SECRET_KEY = "MostSecretof_keys!"
ALGORITHM = "HS256"

# Database Configuration
DATABASE_URL = "mysql+mysqlconnector://root:chlgustn0425!@localhost:3306/soft_project"
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
    token_payload = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)}
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
