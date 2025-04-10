from sqlalchemy import Column, Integer, String, ForeignKey, Time, Enum, DateTime
from datetime import datetime
from db import Base

class StudentInformation(Base):
    __tablename__ = "student_information"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class StudentAvailability(Base):
    __tablename__ = "student_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_information.id"), nullable=False) 
    day_of_week = Column(Enum("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", name="day_of_week_enum"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    timezone = Column(String(50), default="UTC")

class AvailableSubjects(Base):
    __tablename__ = "available_subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_name = Column(String(255), unique=True, nullable=False)

class StudentSubjects(Base):
    __tablename__ = "student_subjects"

    student_id = Column(Integer, ForeignKey("student_information.id"), primary_key=True)
    subject_id = Column(Integer, ForeignKey("available_subjects.id"), primary_key=True)

class StudyPartner(Base):
    __tablename__ = "study_partners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    status = Column(Enum("pending", "accepted", "declined", name="friend_status"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey("available_subjects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String(50), default="member")  # Optional: "admin", "member", etc.

class MeetingSchedule(Base):
    __tablename__ = "meeting_schedule"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("available_subjects.id"), nullable=True)  # ✅ add this
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    meeting_time = Column(DateTime, nullable=False)
    room_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)


class MeetingInvite(Base):
    __tablename__ = "meeting_invites"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meeting_schedule.id"), nullable=False)
    invitee_id = Column(Integer, ForeignKey("student_information.id"), nullable=False)
    invited_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("pending", "accepted", "declined", name="invite_status"), default="pending")