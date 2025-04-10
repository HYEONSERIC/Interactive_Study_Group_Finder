from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db import get_db
from models import StudentInformation
from schemas import StudentResponse, StudentUpdateRequest, StudentName
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# student_information
@router.get("/students", response_model=List[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(StudentInformation).all()
    if not students:
        raise HTTPException(status_code=404, detail="No students found")

    return [StudentResponse(id=student.id, name=student.name, email=student.email) for student in students]


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdateRequest, db: Session = Depends(get_db)):
    db_student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db_student.name = student.name
    db_student.email = student.email
    db.commit()
    return db_student

@router.post("/students/{student_id}")
def update_student_profile(student_id: int, name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.name = name
    student.email = email
    db.commit()
    return {"message": "Profile updated successfully"}

@router.get("/student_info/{student_id}", response_class=HTMLResponse)
def get_student_info_page(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse("student_info.html", {"request": request, "student": student}) 

@router.get("/get_student_id")
def get_student_id(email: str, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id}

@router.get("/view-profile/{username}", response_class=HTMLResponse)
def get_view_profile_page(username: str, request: Request, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.name == username).first()
    if not student:
        raise HTTPException(status_code=406, detail="Student not found")
    return templates.TemplateResponse("view-profile.html", {"request": request, "student": student}) 

@router.post("/view-profile")
def get_profile_info(student: StudentName, db: Session = Depends(get_db)):
    student = db.query(StudentInformation).filter(StudentInformation.name == student.name).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    name = student.name
    email = student.email   
    return student