from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Secret key for JWT
SECRET_KEY = "MostSecretof_keys!"
ALGORITHM = "HS256"
DATABASE_URL = "mysql+mysqlconnector://root:chlgustn0425!@localhost:3306/soft_project"

security = HTTPBearer()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()  # Declare base class for all models

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
        return payload["sub"]  # Assuming "sub" is where you stored the user email
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")