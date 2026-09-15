from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import ProfileOut, ProfileUpdate
from ..services import skills_dictionary as sd
from ..services.profile_service import get_or_create_profile

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
def read_profile(db: Session = Depends(get_db)):
    return get_or_create_profile(db)


@router.put("/profile", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db)
    profile.skills.clear()
    db.flush()
    for raw_name in payload.skills:
        raw_name = raw_name.strip()
        if raw_name:
            canonical = sd.match_canonical(raw_name) or raw_name
            profile.skills.append(models.Skill(name=canonical))
    db.commit()
    db.refresh(profile)
    return profile
