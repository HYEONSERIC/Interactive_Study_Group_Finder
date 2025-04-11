from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db,  SECRET_KEY, ALGORITHM, get_current_user_email
from models import StudentInformation
from schemas import UserCreate, LoginRequest
from datetime import datetime, timedelta
import bcrypt
import jwt

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

@router.get("/me")
def get_current_user_data(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}