import datetime
import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship

from .database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=gen_id)
    raw_resume = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    skills = relationship(
        "Skill", back_populates="profile", cascade="all, delete-orphan"
    )


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    level = Column(String, nullable=True)
    profile_id = Column(String, ForeignKey("profiles.id"))

    profile = relationship("Profile", back_populates="skills")


class MatchHistory(Base):
    __tablename__ = "match_history"

    id = Column(String, primary_key=True, default=gen_id)
    job_url = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    match_percent = Column(Integer, nullable=False)
    matched_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
