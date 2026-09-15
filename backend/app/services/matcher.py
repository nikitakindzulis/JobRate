"""
Бесплатное сопоставление резюме и вакансии без внешних API —
на основе локального словаря навыков (skills_dictionary.py).
"""

from . import skills_dictionary as sd


def extract_skills_from_resume(resume_text: str) -> dict:
    """Аналог прежнего llm.extract_skills(), но без вызова какого-либо API."""
    found = sd.extract_skills_from_text(resume_text)
    skills = [{"name": name, "level": None} for name in found]
    summary = (
        f"В резюме автоматически найдено {len(found)} навыков из словаря. "
        "Список можно отредактировать вручную."
        if found
        else "Не удалось автоматически найти навыки из словаря в резюме — добавьте их вручную."
    )
    return {"skills": skills, "summary": summary}


def compute_match(profile_skills: list[str], job_text: str) -> dict:
    """Аналог прежнего llm.match_job(), но локально и бесплатно."""
    job_skills = sd.extract_skills_from_text(job_text)
    profile_set = {s.lower() for s in profile_skills}

    matched = [s for s in job_skills if s.lower() in profile_set]
    missing = [s for s in job_skills if s.lower() not in profile_set]
    total = len(job_skills)
    percent = round(len(matched) / total * 100) if total else 0

    if total == 0:
        summary = (
            "Не удалось найти конкретные требования к навыкам в тексте вакансии "
            "по словарю — попробуйте расширить словарь skills_dictionary.py."
        )
    elif percent >= 80:
        summary = f"Отличное соответствие: у вас есть {len(matched)} из {total} требуемых навыков."
    elif percent >= 50:
        summary = (
            f"Неплохое соответствие ({len(matched)} из {total}). "
            f"Стоит подтянуть: {', '.join(missing[:5])}."
        )
    else:
        summary = (
            f"Соответствие низкое ({len(matched)} из {total}). "
            f"Не хватает: {', '.join(missing[:5])}."
        )

    return {
        "match_percent": percent,
        "matched_skills": matched,
        "missing_skills": missing,
        "nice_to_have": [],
        "summary": summary,
    }
