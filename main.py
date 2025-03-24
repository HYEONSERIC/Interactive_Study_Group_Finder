from fastapi import FastAPI, HTTPException, Depends, Query, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Enum, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
import mysql.connector
import bcrypt
import jwt
import os

SECRET_KEY = "MostSecretof_keys!"
ALGORITHM = "HS256"

# Database Configuration
DATABASE_URL = "mysql+mysqlconnector://root:password4swe@localhost:3306/soft_project"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# FastAPI Instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class StudentUpdateRequest(BaseModel):
    name: str
    email: str

class StudentResponse(BaseModel):
    name: str
    email: str

class PartnerRequest(BaseModel):
    receiver_id: int

class PartnerResponse(BaseModel):
    partner_id: int
    action: str  # "accept" or "decline"

class PartnerInfo(BaseModel):
    id: int
    name: str
    email: str

# Tables
class StudentInformation(Base):
    __tablename__ = "student_information"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class StudyPartner(Base):
    __tablename__ = "study_partners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    status = Column(Enum("pending", "accepted", "declined"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running and connected to MySQL"}

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    password_hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db_user = StudentInformation(name=user.name, email=user.email, password_hash=password_hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == request.email).first()
    if not user or not bcrypt.checkpw(request.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token_payload = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "message": "Login successful"}

@app.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(AvailableSubjects).all()

@app.post("/subjects")
def add_subject(subject_name: str, db: Session = Depends(get_db)):
    new_subject = AvailableSubjects(subject_name=subject_name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@app.get("/students", response_model=List[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(StudentInformation).all()
    return [StudentResponse(name=s.name, email=s.email) for s in students]

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

@app.get("/student_info/{student_id}", response_class=HTMLResponse)
def get_student_info_page(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("student_info.html", {"request": request, "student": student})

# Friend Management Endpoints#

@app.post("/partners/request")
def send_friend_request(request: PartnerRequest, db: Session = Depends(get_db), current_user_email: str = Depends(lambda: "test@example.com")):
    sender = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(StudyPartner).filter(
        StudyPartner.requester_id == sender.id,
        StudyPartner.receiver_id == request.receiver_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already exists")

    new_request = StudyPartner(requester_id=sender.id, receiver_id=request.receiver_id)
    db.add(new_request)
    db.commit()
    return {"message": "Partner request sent"}

@app.put("/partners/respond")
def respond_to_request(response: PartnerResponse, db: Session = Depends(get_db), current_user_email: str = Depends(lambda: "test@example.com")):
    receiver = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    partner_record = db.query(StudyPartner).filter(
        StudyPartner.id == response.partner_id,
        StudyPartner.receiver_id == receiver.id
    ).first()
    if not partner_record:
        raise HTTPException(status_code=404, detail="Request not found")

    if response.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    partner_record.status = "accepted" if response.action == "accept" else "declined"
    db.commit()
    return {"message": f"Request {response.action}ed"}

@app.get("/partners", response_model=List[PartnerInfo])
def get_friends(db: Session = Depends(get_db), current_user_email: str = Depends(lambda: "test@example.com")):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accepted = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) | (StudyPartner.receiver_id == user.id)),
        StudyPartner.status == "accepted"
    ).all()

    friend_ids = [r.receiver_id if r.requester_id == user.id else r.requester_id for r in accepted]
    friends = db.query(StudentInformation).filter(StudentInformation.id.in_(friend_ids)).all()
    return [PartnerInfo(id=f.id, name=f.name, email=f.email) for f in friends]

@app.delete("/partners/{partner_id}")
def remove_friend(partner_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(lambda: "test@example.com")):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) & (StudyPartner.receiver_id == partner_id)) |
        ((StudyPartner.receiver_id == user.id) & (StudyPartner.requester_id == partner_id)),
        StudyPartner.status == "accepted"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Friend relationship not found")

    db.delete(record)
    db.commit()
    return {"message": "Friend removed"}
