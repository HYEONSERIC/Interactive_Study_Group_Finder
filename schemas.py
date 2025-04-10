from pydantic import BaseModel
from datetime import datetime

# login/registration
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# friend requests
class StudentUpdateRequest(BaseModel):
    name: str
    email: str


class EmailPartnerRequest(BaseModel):
    receiver_email: str

class PartnerResponse(BaseModel):
    partner_id: int
    action: str  # accept or decline

class PartnerInfo(BaseModel):
    id: int
    name: str
    email: str

# search
class StudentName(BaseModel):
    name: str

# student info
class StudentResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

# meetings
class MeetingCreateRequest(BaseModel):
    title: str
    description: str
    meeting_time: datetime
    subject_name: str

class InviteUserRequest(BaseModel):
    meeting_title: str
    invitee_email: str

class MeetingResponse(BaseModel):
    id: int
    title: str
    description: str
    meeting_time: datetime
    room_name: str

    class Config:
        orm_mode = True

# group
class GroupCreate(BaseModel):
    name: str  

class GroupResponse(BaseModel):
    id: int
    name: str 

    class Config:
        orm_mode = True

class SubjectCreate(BaseModel):
    subject_name: str
    
class PostQuery(BaseModel):
    query_str: str