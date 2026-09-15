from anthropic import Anthropic

from ..config import settings

_client = Anthropic(api_key=settings.anthropic_api_key)

EXTRACT_SKILLS_TOOL = {
    "name": "extract_resume_data",
    "description": "Извлечь структурированный список навыков и краткое summary из текста резюме",
    "input_schema": {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "description": "Все технические и профессиональные навыки, упомянутые в резюме",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Название навыка, например 'Python' или 'управление командой'"},
                        "level": {
                            "type": "string",
                            "enum": ["junior", "middle", "senior", "expert", "unknown"],
                            "description": "Оценка уровня владения навыком, если её можно определить из контекста",
                        },
                    },
                    "required": ["name"],
                },
            },
            "summary": {
                "type": "string",
                "description": "Краткое summary опыта кандидата на русском, 1-2 предложения",
            },
        },
        "required": ["skills", "summary"],
    },
}

MATCH_TOOL = {
    "name": "match_job_to_profile",
    "description": "Сравнить навыки кандидата с требованиями вакансии и посчитать процент соответствия",
    "input_schema": {
        "type": "object",
        "properties": {
            "match_percent": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Итоговый процент соответствия кандидата вакансии",
            },
            "matched_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Навыки кандидата, которые требуются в вакансии",
            },
            "missing_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Навыки, требуемые вакансией, но отсутствующие у кандидата",
            },
            "nice_to_have": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Навыки, упомянутые как плюс/приветствуется, но не критичные",
            },
            "summary": {
                "type": "string",
                "description": "Краткая рекомендация кандидату на русском, 1-2 предложения",
            },
        },
        "required": ["match_percent", "matched_skills", "missing_skills", "summary"],
    },
}


def _call_tool(tool: dict, user_message: str) -> dict:
    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": user_message}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise RuntimeError("Модель не вернула ожидаемый структурированный ответ")


def extract_skills(resume_text: str) -> dict:
    message = (
        "Вот текст резюме кандидата. Извлеки список его навыков (технических и "
        "профессиональных) и краткое summary опыта.\n\n" + resume_text[:15000]
    )
    return _call_tool(EXTRACT_SKILLS_TOOL, message)


def match_job(profile_skills: list[str], job_text: str) -> dict:
    skills_str = ", ".join(profile_skills)
    message = (
        f"Навыки кандидата: {skills_str}\n\n"
        f"Текст вакансии:\n{job_text[:15000]}\n\n"
        "Оцени в процентах, насколько кандидат подходит под эту вакансию. "
        "Укажи, какие из его навыков совпадают с требованиями, каких навыков "
        "из вакансии ему не хватает, и какие требования упомянуты как желательные, но не обязательные."
    )
    return _call_tool(MATCH_TOOL, message)
