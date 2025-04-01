from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import AvailableSubjects

router = APIRouter()

# SUBJECTS
# API Endpoint - all subjects in available_subjects
@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(AvailableSubjects).all()
    return subjects

# API Endpoint - add subject
@router.post("/subjects")
def add_subject(subject_name: str, db: Session = Depends(get_db)):
    new_subject = AvailableSubjects(subject_name=subject_name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject