from sqlalchemy.orm import Session

from .. import models


def get_or_create_profile(db: Session) -> models.Profile:
    """MVP работает без аутентификации — на инстанс всегда ровно один профиль."""
    profile = db.query(models.Profile).first()
    if not profile:
        profile = models.Profile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
