from typing import Optional

import anthropic
from pydantic import BaseModel

from ..config import settings

# Если ключ не задан в .env — падаем на стандартное разрешение SDK
# (ANTHROPIC_API_KEY из окружения, либо профиль `ant auth login`).
_client = (
    anthropic.Anthropic(api_key=settings.anthropic_api_key)
    if settings.anthropic_api_key
    else anthropic.Anthropic()
)


class ExtractedSkill(BaseModel):
    name: str
    level: Optional[str] = None  # junior / middle / senior / expert / unknown


class ResumeExtraction(BaseModel):
    skills: list[ExtractedSkill]
    summary: str


class JobMatch(BaseModel):
    match_percent: int
    matched_skills: list[str]
    missing_skills: list[str]
    nice_to_have: list[str] = []
    summary: str


def extract_skills(resume_text: str) -> dict:
    response = _client.messages.parse(
        model=settings.anthropic_model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "Вот текст резюме кандидата. Извлеки ПОЛНЫЙ список его навыков: "
                    "технические (языки программирования, инструменты, технологии), "
                    "профессиональные/soft skills, и ОБЯЗАТЕЛЬНО разговорные/иностранные "
                    "языки (например, английский, латышский, русский), если они указаны "
                    "в резюме — для каждого языка укажи уровень владения в поле level "
                    "(например, 'C1', 'upper-intermediate', 'родной'), если он есть в "
                    "тексте. Не пропускай ни одного навыка или языка, упомянутого в "
                    "резюме. Также напиши краткое summary опыта на русском, "
                    "1-2 предложения.\n\n" + resume_text[:15000]
                ),
            }
        ],
        output_format=ResumeExtraction,
    )
    result = response.parsed_output
    return {
        "skills": [{"name": s.name, "level": s.level} for s in result.skills],
        "summary": result.summary,
    }


def match_job(profile_skills: list[dict], job_text: str) -> dict:
    skills_str = ", ".join(
        f"{s['name']} (уровень: {s['level']})" if s.get("level") else s["name"]
        for s in profile_skills
    )
    response = _client.messages.parse(
        model=settings.anthropic_model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Навыки кандидата (в скобках — заявленный уровень владения, "
                    f"если известен): {skills_str}\n\n"
                    f"Текст вакансии:\n{job_text[:15000]}\n\n"
                    "Оцени в процентах, насколько кандидат подходит под эту вакансию, "
                    "основываясь ТОЛЬКО на профессиональных и технических навыках "
                    "(языки программирования, инструменты, технологии, разговорные "
                    "языки, профессиональные компетенции). НЕ учитывай при подсчёте "
                    "процента и не включай в matched_skills/missing_skills требования, "
                    "которые не являются навыками кандидата: формат работы "
                    "(офис/удалёнка/гибрид), локацию, готовность к релокации, визу, "
                    "график работы, зарплату, тип занятости и т.п. — это условия "
                    "работы, а не навыки, их не нужно упоминать вообще.\n"
                    "Если у кандидата указан уровень владения навыком или языком "
                    "(например, C1, upper-intermediate, senior) — сопоставляй его с "
                    "требуемым уровнем из вакансии по смыслу (например, C1 или "
                    "upper-intermediate удовлетворяет требованию 'fluent' / 'свободное "
                    "владение'), а не только по названию навыка.\n"
                    "Укажи, какие из его навыков совпадают с требованиями, каких "
                    "навыков из вакансии ему не хватает, и какие требования упомянуты "
                    "как желательные, но не обязательные. Ответ пиши на русском."
                ),
            }
        ],
        output_format=JobMatch,
    )
    result = response.parsed_output.model_dump()

    # match_percent модель генерирует отдельно от списков matched/missing —
    # это может давать нелогичные расхождения (например, 95% при пустом
    # missing_skills). Пересчитываем процент напрямую из списков, которые
    # модель уже составила, чтобы цифра всегда была с ними согласована.
    matched_count = len(result["matched_skills"])
    missing_count = len(result["missing_skills"])
    total = matched_count + missing_count
    if total > 0:
        result["match_percent"] = round(matched_count / total * 100)

    return result
