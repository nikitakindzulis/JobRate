from typing import Optional

from pydantic import BaseModel, ConfigDict


class SkillOut(BaseModel):
    id: str
    name: str
    level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileOut(BaseModel):
    id: str
    summary: Optional[str] = None
    skills: list[SkillOut]

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    skills: list[str]


class MatchRequest(BaseModel):
    job_text: str
    job_url: Optional[str] = None
    job_title: Optional[str] = None


class MatchResult(BaseModel):
    match_percent: int
    matched_skills: list[str]
    missing_skills: list[str]
    nice_to_have: list[str] = []
    summary: str
