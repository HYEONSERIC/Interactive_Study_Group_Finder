from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Secret key for JWT
SECRET_KEY = "MostSecretof_keys!"
ALGORITHM = "HS256"
DATABASE_URL = "mysql+mysqlconnector://root:pass4sql@localhost:3306/soft_project"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()  # Declare base class for all models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()