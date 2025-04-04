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

class StudentResponse(BaseModel):
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
        orm_mode = True

# meetings
class MeetingCreateRequest(BaseModel):
    title: str
    description: str
    meeting_time: datetime
    group_id: int

class InviteUserRequest(BaseModel):
    meeting_id: int
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
    name: str  # ✅ subject_id 제거

class GroupResponse(BaseModel):
    id: int
    name: str  # ✅ subject_id 제거

    class Config:
        orm_mode = True
