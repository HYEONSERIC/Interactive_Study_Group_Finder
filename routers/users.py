from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.orm import Session
from db import get_db
from models import StudentInformation
from schemas import UserCreate, LoginRequest
from datetime import datetime, timedelta
from pydantic import BaseModel
import bcrypt
import jwt
from db import SECRET_KEY, ALGORITHM

router = APIRouter()

#USER INFORMATION
# API Endpoint - Get Users
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(StudentInformation).all()
    return users

# API Endpoint - Create User
@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    password_hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = StudentInformation(name=user.name, email=user.email, password_hash=password_hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

#LOGIN
# API Endpoint - Login verification
@router.post("/login") 
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == request.email).first()
    if not user or not bcrypt.checkpw(request.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT token
    token_payload = {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"token": token, "message": "Login successful"}