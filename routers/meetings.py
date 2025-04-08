from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from db import get_db
from models import StudentInformation
from datetime import datetime
from models import MeetingInvite, MeetingSchedule, AvailableSubjects
from schemas import MeetingCreateRequest, InviteUserRequest
from db import get_current_user_email     

router = APIRouter()

@router.post("/schedule-meeting")
def schedule_meeting(meeting: MeetingCreateRequest, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    host = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()

    # Normalize subject name (e.g., lowercase, remove dashes/underscores, strip spaces)
    normalized_name = meeting.subject_name.strip().lower().replace("-", " ").replace("_", " ")

    # Check if subject already exists (case-insensitive match)
    subject = db.query(AvailableSubjects).filter(AvailableSubjects.subject_name.ilike(normalized_name)).first()

    if not subject:
        subject = AvailableSubjects(subject_name=normalized_name)
        db.add(subject)
        db.commit()
        db.refresh(subject)

    new_meeting = MeetingSchedule(
        host_id=host.id,
        subject_id=subject.id,  # ✅ use subject.id now
        title=meeting.title,
        description=meeting.description,
        meeting_time=meeting.meeting_time,
        room_name=f"studybuddy-room-{host.id}-{int(datetime.utcnow().timestamp())}"
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return {"message": "Meeting scheduled", "meeting_id": new_meeting.id}

@router.post("/invite-to-meeting")
def invite_user(invite: InviteUserRequest, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    inviter = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    invitee = db.query(StudentInformation).filter(StudentInformation.email == invite.invitee_email).first()

    if not invitee:
        raise HTTPException(status_code=404, detail="Invitee not found")

    # Look up meeting by title instead of ID
    meeting = db.query(MeetingSchedule).filter(MeetingSchedule.title == invite.meeting_title).first()
    
    if not meeting or meeting.host_id != inviter.id:
        raise HTTPException(status_code=403, detail="Not authorized to invite or meeting not found")

    new_invite = MeetingInvite(meeting_id=meeting.id, invitee_id=invitee.id)
    db.add(new_invite)
    db.commit()
    return {"message": "User invited"}

@router.get("/my-meeting-invites")
def get_meeting_invites(
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()

    invites = db.query(MeetingInvite).join(MeetingSchedule).filter(MeetingInvite.invitee_id == user.id).all()

    result = []
    for invite in invites:
        meeting = db.query(MeetingSchedule).filter(MeetingSchedule.id == invite.meeting_id).first()
        result.append({
            "meeting_id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "meeting_time": str(meeting.meeting_time),
            "room_name": meeting.room_name
        })

    return result