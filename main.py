from fastapi import FastAPI, HTTPException, Depends, Query, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

DATABASE_URL = "mysql+mysqlconnector://root:password4swe@localhost:3306/soft_project"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

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

class EmailPartnerRequest(BaseModel):
    receiver_email: str

class PartnerResponse(BaseModel):
    partner_id: int
    action: str  # accept or decline

class PartnerInfo(BaseModel):
    id: int
    name: str
    email: str

class StudentInformation(Base):
    __tablename__ = "student_information"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyPartner(Base):
    __tablename__ = "study_partners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    status = Column(Enum("pending", "accepted", "declined"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "FastAPI running"}

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    db_user = StudentInformation(name=user.name, email=user.email, password_hash=hashed)
    db.add(db_user)
    db.commit()
    return {"message": "User created"}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == request.email).first()
    if not user or not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"message": "Login successful", "token": token}

@app.get("/students", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentInformation).all()
    return [StudentResponse(name=s.name, email=s.email) for s in students]

@app.post("/partners/request-by-email")
def send_request_by_email(req: EmailPartnerRequest, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    sender = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    receiver = db.query(StudentInformation).filter(StudentInformation.email == req.receiver_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    existing = db.query(StudyPartner).filter(
        StudyPartner.requester_id == sender.id,
        StudyPartner.receiver_id == receiver.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")

    new_request = StudyPartner(requester_id=sender.id, receiver_id=receiver.id)
    db.add(new_request)
    db.commit()
    return {"message": "Friend request sent"}

@app.get("/partners", response_model=List[PartnerInfo])
def get_friends(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    accepted = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) | (StudyPartner.receiver_id == user.id)),
        StudyPartner.status == "accepted"
    ).all()

    ids = [r.receiver_id if r.requester_id == user.id else r.requester_id for r in accepted]
    friends = db.query(StudentInformation).filter(StudentInformation.id.in_(ids)).all()
    return [PartnerInfo(id=f.id, name=f.name, email=f.email) for f in friends]

@app.get("/partners/pending", response_model=List[PartnerInfo])
def get_pending_requests(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    pending = db.query(StudyPartner).filter(
        StudyPartner.receiver_id == user.id,
        StudyPartner.status == "pending"
    ).all()

    sender_ids = [r.requester_id for r in pending]
    senders = db.query(StudentInformation).filter(StudentInformation.id.in_(sender_ids)).all()
    return [PartnerInfo(id=s.id, name=s.name, email=s.email) for s in senders]

@app.put("/partners/respond")
def respond_to_request(response: PartnerResponse, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    receiver = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    record = db.query(StudyPartner).filter(
        StudyPartner.id == response.partner_id,
        StudyPartner.receiver_id == receiver.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    if response.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    record.status = "accepted" if response.action == "accept" else "declined"
    db.commit()
    return {"message": f"Request {response.action}ed"}

@app.delete("/partners/{partner_id}")
def remove_friend(partner_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()

    record = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) & (StudyPartner.receiver_id == partner_id)) |
        ((StudyPartner.receiver_id == user.id) & (StudyPartner.requester_id == partner_id)),
        StudyPartner.status == "accepted"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
@app.get("/get_student_id")
def get_student_id(email: str, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": user.id}

    db.delete(record)
    db.commit()
    return {"message": "Friend removed"}
