from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import StudentInformation, StudyGroup
from schemas import PostQuery

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@router.post("/students")
def search_students(query: PostQuery, db: Session = Depends(get_db)):
    students = db.query(StudentInformation).filter(
        StudentInformation.name.contains(query.query_str) |
        StudentInformation.email.contains(query.query_str)
    ).all()

    if not students:
        raise HTTPException(status_code=404, detail="No students found.")
    return students

@router.post("/study-groups")
def search_groups(query: PostQuery, db: Session = Depends(get_db)):
    groups = db.query(StudyGroup).filter(
        StudyGroup.name.contains(query.query_str)
    ).all()

    if not groups:
        raise HTTPException(status_code=404, detail="No study groups found.")
    return groups
