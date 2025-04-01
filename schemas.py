from pydantic import BaseModel
from datetime import datetime

# User Model #
#this is where each table from the database is defined. these will be wonky and throw errors and may
#need definition added like the UserCreate(BaseModel). The javascript to sql conversion gets confused
#so that was added to get uniformity when creating a user. 

#login/registration
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

#friend requests
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

#search
class StudentName(BaseModel):
    name: str

#student info
class StudentResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class MeetingCreateRequest(BaseModel):
    title: str
    description: str
    meeting_time: datetime  # Format: "2025-04-03T15:30:00"

class InviteUserRequest(BaseModel):
    meeting_id: int
    invitee_email: str