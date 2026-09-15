from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import MatchRequest, MatchResult
from ..services.matcher import compute_match
from ..services.profile_service import get_or_create_profile

router = APIRouter(prefix="/api", tags=["match"])


@router.post("/match", response_model=MatchResult)
def match(payload: MatchRequest, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db)
    skill_names = [s.name for s in profile.skills]
    if not skill_names:
        raise HTTPException(status_code=400, detail="Сначала загрузите резюме в профиле")

    if not payload.job_text.strip():
        raise HTTPException(status_code=400, detail="Пустой текст вакансии")

    result = compute_match(skill_names, payload.job_text)

    history = models.MatchHistory(
        job_url=payload.job_url,
        job_title=payload.job_title,
        match_percent=result["match_percent"],
        matched_json=result,
    )
    db.add(history)
    db.commit()

    return MatchResult(**result)
