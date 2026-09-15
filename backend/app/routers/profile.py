from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import ProfileOut, ProfileUpdate
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
    for name in payload.skills:
        name = name.strip()
        if name:
            profile.skills.append(models.Skill(name=name))
    db.commit()
    db.refresh(profile)
    return profile
