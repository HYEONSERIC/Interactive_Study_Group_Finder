from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db, get_current_user_email
from models import StudyGroup, GroupMember, StudentInformation, MeetingSchedule
from schemas import GroupCreate, GroupResponse, MeetingResponse
from datetime import datetime

router = APIRouter()

@router.post("/groups", response_model=GroupResponse)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    creator = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    new_group = StudyGroup(name=group.name, created_at=datetime.utcnow())  # ✅ subject_id 제거
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    membership = GroupMember(group_id=new_group.id, student_id=creator.id, role="admin")
    db.add(membership)
    db.commit()

    return new_group

@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    current_user = db.query(StudentInformation).filter_by(email=current_user_email).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    group = db.query(StudyGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    admin_membership = db.query(GroupMember).filter_by(
        group_id=group_id, student_id=current_user.id, role="admin"
    ).first()

    if not admin_membership:
        raise HTTPException(status_code=403, detail="Only group admin can delete the group")

    db.query(GroupMember).filter_by(group_id=group_id).delete()
    db.query(MeetingSchedule).filter_by(group_id=group_id).delete()
    db.delete(group)
    db.commit()

@router.get("/groups/{group_id}/members")
def get_group_members(group_id: int, db: Session = Depends(get_db)):
    members = (
        db.query(StudentInformation)
        .join(GroupMember, GroupMember.student_id == StudentInformation.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    return [{"name": m.name, "email": m.email, "role": db.query(GroupMember).filter_by(group_id=group_id, student_id=m.id).first().role} for m in members]

@router.get("/groups/my", response_model=list[GroupResponse])
def get_my_groups(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    me = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    if not me:
        raise HTTPException(status_code=404, detail="User not found")

    groups = db.query(StudyGroup).join(GroupMember).filter(GroupMember.student_id == me.id).all()
    return groups

@router.get("/groups/{group_id}/schedule", response_model=list[MeetingResponse])
def get_group_schedule(group_id: int, db: Session = Depends(get_db)):
    meetings = db.query(MeetingSchedule).filter(MeetingSchedule.group_id == group_id).all()
    return meetings

@router.get("/all_groups", response_model=list[GroupResponse])
def all_groups(db: Session = Depends(get_db)):
    return db.query(StudyGroup).all()

@router.post("/join_group/{group_id}")
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    student = db.query(StudentInformation).filter_by(email=current_user_email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    already = db.query(GroupMember).filter_by(group_id=group_id, student_id=student.id).first()
    if already:
        raise HTTPException(status_code=400, detail="Already joined this group.")

    membership = GroupMember(group_id=group_id, student_id=student.id, role="member")
    db.add(membership)
    db.commit()

    return {"message": "Joined group successfully"}

@router.post("/leave_group/{group_id}")
def leave_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    student = db.query(StudentInformation).filter_by(email=current_user_email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    membership = db.query(GroupMember).filter_by(group_id=group_id, student_id=student.id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Not a group member")

    if membership.role == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot leave the group. You must delete it.")

    db.delete(membership)
    db.commit()

    return {"message": "Left the group successfully"}