from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db import get_db
from models import AvailableSubjects, StudentSubjects
from schemas import SubjectCreate, UserIDQuery

router = APIRouter()

# SUBJECTS
# API Endpoint - all subjects in available_subjects
@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(AvailableSubjects).all()
    return subjects

@router.put("/subjects")
def get_subjects(id: UserIDQuery, db: Session = Depends(get_db)):
    mysubjects = db.query(StudentSubjects).filter(StudentSubjects.student_id == id.id).all()
    return mysubjects

# API Endpoint - add subject
@router.post("/subjects")
def add_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    new_subject = AvailableSubjects(subject_name=subject.subject_name)
    db.add(new_subject)
    try:
        db.commit()
        db.refresh(new_subject)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Subject already exists")
    return new_subject