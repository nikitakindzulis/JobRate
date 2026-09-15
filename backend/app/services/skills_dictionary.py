"""
Локальный словарь навыков: канонические названия + алиасы/синонимы.
Используется для бесплатного (без внешних API) извлечения навыков из
текста резюме и вакансии — через regex-поиск по границам слов, без ML.

Чтобы улучшить точность, просто дополняй SKILLS новыми записями.
"""

import re

SKILLS: dict[str, list[str]] = {
    # Языки программирования
    "Python": [],
    "JavaScript": ["js"],
    "TypeScript": ["ts"],
    "Java": [],
    "C++": ["cpp"],
    "C#": ["csharp", "c sharp"],
    "C": [],
    "Go": ["golang"],
    "Rust": [],
    "PHP": [],
    "Ruby": [],
    "Kotlin": [],
    "Swift": [],
    "Scala": [],
    "R": [],
    "MATLAB": [],
    "Perl": [],
    "Objective-C": [],
    "Dart": [],
    "SQL": [],
    "Bash": ["shell", "shell scripting", "shell-скрипты"],
    "PowerShell": [],
    "Lua": [],

    # Frontend
    "HTML": ["html5"],
    "CSS": ["css3"],
    "React": ["react.js", "reactjs"],
    "React Native": [],
    "Vue.js": ["vue", "vuejs"],
    "Angular": ["angularjs"],
    "Next.js": ["nextjs"],
    "Nuxt.js": ["nuxtjs", "nuxt"],
    "Svelte": [],
    "Redux": [],
    "Webpack": [],
    "Vite": [],
    "Tailwind CSS": ["tailwind"],
    "Sass": ["scss"],
    "jQuery": [],

    # Backend / фреймворки
    "Node.js": ["node", "nodejs"],
    "Express.js": ["express"],
    "Django": [],
    "Flask": [],
    "FastAPI": [],
    "Spring": ["spring boot", "spring framework"],
    "ASP.NET": [".net", "dotnet", "asp.net core"],
    "Ruby on Rails": ["rails"],
    "Laravel": [],
    "NestJS": [],
    "GraphQL": [],
    "REST API": ["rest", "restful", "rest api"],
    "gRPC": [],
    "Microservices": ["микросервисы", "микросервисная архитектура"],

    # Базы данных
    "PostgreSQL": ["postgres", "psql"],
    "MySQL": [],
    "SQLite": [],
    "MongoDB": ["mongo"],
    "Redis": [],
    "Elasticsearch": [],
    "Oracle Database": ["oracle db"],
    "Microsoft SQL Server": ["mssql", "sql server"],
    "Cassandra": [],
    "DynamoDB": [],
    "ClickHouse": [],

    # DevOps / Cloud
    "Docker": [],
    "Kubernetes": ["k8s"],
    "AWS": ["amazon web services"],
    "Azure": ["microsoft azure"],
    "Google Cloud Platform": ["gcp", "google cloud"],
    "Terraform": [],
    "Ansible": [],
    "Jenkins": [],
    "CI/CD": ["continuous integration", "continuous deployment"],
    "Git": [],
    "GitHub Actions": [],
    "GitLab CI": [],
    "Linux": [],
    "Nginx": [],
    "Prometheus": [],
    "Grafana": [],

    # Data / ML
    "Pandas": [],
    "NumPy": [],
    "TensorFlow": [],
    "PyTorch": [],
    "scikit-learn": ["sklearn"],
    "Keras": [],
    "Machine Learning": ["ml", "машинное обучение"],
    "Deep Learning": ["глубокое обучение"],
    "NLP": ["natural language processing", "обработка естественного языка"],
    "Computer Vision": ["компьютерное зрение"],
    "Apache Spark": ["spark"],
    "Hadoop": [],
    "Airflow": [],
    "Power BI": ["powerbi"],
    "Tableau": [],
    "Excel": ["microsoft excel"],
    "ETL": [],
    "Data Analysis": ["анализ данных"],
    "A/B Testing": ["ab testing", "а/б тестирование"],

    # Mobile
    "Flutter": [],
    "Android": [],
    "iOS": [],
    "SwiftUI": [],

    # Дизайн
    "Figma": [],
    "Adobe Photoshop": ["photoshop"],
    "Adobe Illustrator": ["illustrator"],
    "UI/UX Design": ["ui/ux", "user experience", "user interface design"],
    "Sketch": [],

    # QA / тестирование
    "Selenium": [],
    "Cypress": [],
    "Jest": [],
    "Pytest": [],
    "Manual Testing": ["ручное тестирование"],
    "Automated Testing": ["автотестирование", "автоматизированное тестирование"],

    # Методологии / менеджмент
    "Agile": [],
    "Scrum": [],
    "Kanban": [],
    "Project Management": ["управление проектами"],
    "Product Management": ["управление продуктом"],
    "Jira": [],
    "Confluence": [],

    # Soft skills
    "Team Leadership": ["управление командой", "лидерство"],
    "Communication Skills": ["коммуникативные навыки", "коммуникация"],
    "Time Management": ["тайм-менеджмент"],
    "Problem Solving": ["решение проблем"],
    "Negotiation": ["переговоры"],
    "Public Speaking": ["публичные выступления"],
    "Teamwork": ["работа в команде"],
    "Mentoring": ["наставничество"],

    # Языки (человеческие)
    "English": ["английский язык", "английский"],
    "German": ["немецкий язык", "немецкий"],
    "Russian": ["русский язык", "русский"],
    "Spanish": ["испанский язык", "испанский"],
}

# Символы, которые считаем частью "слова" при проверке границ совпадения.
# Специально НЕ включают +, #, ., - — иначе "C++"/"C#"/"Node.js" не находились бы.
_BOUNDARY_CHARS = r"a-zA-Zа-яА-ЯёЁ0-9_"


def _build_pattern(term: str) -> re.Pattern:
    escaped = re.escape(term.lower())
    return re.compile(rf"(?<![{_BOUNDARY_CHARS}]){escaped}(?![{_BOUNDARY_CHARS}])")


_COMPILED: dict[str, list[re.Pattern]] = {
    canonical: [_build_pattern(t) for t in [canonical] + aliases]
    for canonical, aliases in SKILLS.items()
}

_ALL_TERMS_LOWER: dict[str, str] = {}
for _canonical, _aliases in SKILLS.items():
    for _term in [_canonical] + _aliases:
        _ALL_TERMS_LOWER[_term.lower()] = _canonical


def extract_skills_from_text(text: str) -> list[str]:
    """Возвращает список канонических названий навыков, найденных в тексте."""
    text_lower = text.lower()
    found = []
    for canonical, patterns in _COMPILED.items():
        if any(p.search(text_lower) for p in patterns):
            found.append(canonical)
    return found


def match_canonical(term: str) -> str | None:
    """Если term совпадает с известным навыком/алиасом целиком — вернуть каноническое имя."""
    return _ALL_TERMS_LOWER.get(term.strip().lower())
