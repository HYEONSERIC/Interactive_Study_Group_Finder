from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db import get_db, SECRET_KEY, ALGORITHM
from models import StudentInformation, StudyPartner
from typing import List
import jwt
from schemas import StudentResponse, EmailPartnerRequest, PartnerResponse, PartnerInfo

router = APIRouter()
security = HTTPBearer()


#Get current user email for friends list
def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# FRIENDS LIST 

@router.get("/students", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentInformation).all()
    return [StudentResponse(name=s.name, email=s.email) for s in students]

@router.post("/partners/request-by-email")
def send_request_by_email(req: EmailPartnerRequest, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    sender = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    receiver = db.query(StudentInformation).filter(StudentInformation.email == req.receiver_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    existing = db.query(StudyPartner).filter(
        StudyPartner.requester_id == sender.id,
        StudyPartner.receiver_id == receiver.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already sent")

    new_request = StudyPartner(requester_id=sender.id, receiver_id=receiver.id)
    db.add(new_request)
    db.commit()
    return {"message": "Friend request sent"}

@router.get("/partners", response_model=List[PartnerInfo])
def get_friends(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    accepted = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) | (StudyPartner.receiver_id == user.id)),
        StudyPartner.status == "accepted"
    ).all()

    ids = [r.receiver_id if r.requester_id == user.id else r.requester_id for r in accepted]
    friends = db.query(StudentInformation).filter(StudentInformation.id.in_(ids)).all()
    return [PartnerInfo(id=f.id, name=f.name, email=f.email) for f in friends]

@router.get("/partners/pending", response_model=List[PartnerInfo])
def get_pending_requests(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()
    pending = db.query(StudyPartner).filter(
        StudyPartner.receiver_id == user.id,
        StudyPartner.status == "pending"
    ).all()

    sender_ids = [r.requester_id for r in pending]
    senders = db.query(StudentInformation).filter(StudentInformation.id.in_(sender_ids)).all()
    return [PartnerInfo(id=s.id, name=s.name, email=s.email) for s in senders]

@router.put("/partners/respond")
def respond_to_request(response: PartnerResponse, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    receiver = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()

    # Interpret the partner_id as the sender (requester) user ID
    record = db.query(StudyPartner).filter(
        StudyPartner.receiver_id == receiver.id,
        StudyPartner.requester_id == response.partner_id,
        StudyPartner.status == "pending"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Request not found")

    if response.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    record.status = "accepted" if response.action == "accept" else "declined"
    db.commit()
    return {"message": f"Request {response.action}ed"}

@router.delete("/partners/{partner_id}")
def remove_friend(partner_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(StudentInformation).filter(StudentInformation.email == current_user_email).first()

    record = db.query(StudyPartner).filter(
        ((StudyPartner.requester_id == user.id) & (StudyPartner.receiver_id == partner_id)) |
        ((StudyPartner.receiver_id == user.id) & (StudyPartner.requester_id == partner_id)),
        StudyPartner.status == "accepted"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    db.delete(record)
    db.commit()
    return {"message": "Friend removed"}
    
@router.get("/get_student_id")
def get_student_id(email: str, db: Session = Depends(get_db)):
    user = db.query(StudentInformation).filter(StudentInformation.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": user.id}

    db.delete(record)
    db.commit()
    return {"message": "Friend removed"}