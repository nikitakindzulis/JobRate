from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import ProfileOut
from ..services.matcher import extract_skills_from_resume
from ..services.profile_service import get_or_create_profile
from ..services.resume_parser import extract_text

router = APIRouter(prefix="/api", tags=["cv"])


@router.post("/cv", response_model=ProfileOut)
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    try:
        text = extract_text(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")

    extracted = extract_skills_from_resume(text)

    profile = get_or_create_profile(db)
    profile.raw_resume = text
    profile.summary = extracted.get("summary")
    profile.skills.clear()
    for skill in extracted.get("skills", []):
        profile.skills.append(models.Skill(name=skill["name"], level=skill.get("level")))

    db.commit()
    db.refresh(profile)
    return profile
