# JobRate

Расширение для браузера, которое сравнивает вакансию на странице с вашим резюме
и показывает процент соответствия, а также какие навыки есть, а каких не хватает.

- **Backend**: Python (FastAPI + SQLAlchemy). Извлечение навыков из резюме и
  сравнение с вакансией делает Claude API (structured outputs через
  `client.messages.parse()` — модель понимает синонимы, контекст и смежные навыки,
  не просто ищет точные совпадения слов).
- **Extension**: чистый JS/HTML/CSS под Chrome/Edge (Manifest V3), без сборщиков —
  устанавливается как "распакованное расширение".

Нужен ключ Claude API (платный, но очень дёшево для этой задачи — см. ниже).

## 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # Windows; на macOS/Linux: cp .env.example .env
```

Откройте `backend/.env` и впишите свой ключ:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Ключ берётся на [console.anthropic.com](https://console.anthropic.com/) → API Keys
(там же пополняется баланс). По умолчанию используется `claude-sonnet-5` — хороший
баланс цены/качества для этой задачи; при желании можно переключить на `claude-opus-5`
в `ANTHROPIC_MODEL` (дороже, но точнее).

Запуск сервера:

```bash
uvicorn app.main:app --reload --port 8000
```

Проверка: [http://localhost:8000/health](http://localhost:8000/health) должен вернуть `{"status":"ok"}`.
При первом запуске автоматически создастся файл БД `backend/jobrate.db` (SQLite).

## 2. Extension

1. Откройте `chrome://extensions` в Chrome (или `edge://extensions` в Edge).
2. Включите режим разработчика ("Developer mode").
3. Нажмите "Загрузить распакованное расширение" ("Load unpacked").
4. Выберите папку `extension/`.

## 3. Использование

1. Откройте попап расширения (иконка в панели браузера) — загрузите PDF/DOCX/TXT резюме.
   Бэкенд через Claude извлечёт список навыков и покажет их в попапе; список можно
   редактировать вручную.
2. Откройте страницу вакансии (например, на hh.ru, LinkedIn, Indeed) — если страница
   похожа на вакансию, в правом нижнем углу появится виджет с процентом соответствия
   и списками "есть у вас" / "не хватает".

## Стоимость

Задача простая (структурированное извлечение по фиксированной JSON-схеме), так что
даже минимальное пополнение баланса ($5) хватит на многие сотни сравнений вакансий
на `claude-sonnet-5`. Резюме парсится один раз при загрузке; основная нагрузка —
`/api/match`, который дергается при каждом визите на страницу вакансии.

## Структура проекта

```
backend/
  app/
    routers/     # HTTP-эндпоинты: /api/cv, /api/profile, /api/match
    services/
      llm.py                  # вызовы Claude API (structured outputs, Pydantic-схемы)
      resume_parser.py         # парсинг PDF/DOCX/TXT в текст
    models.py      # SQLAlchemy-модели (Profile, Skill, MatchHistory)
    schemas.py      # Pydantic-схемы запросов/ответов
    main.py          # точка входа FastAPI
extension/
  manifest.json
  background.js   # service worker: HTTP-запросы к бэкенду
  content.js       # определяет страницу вакансии, показывает виджет
  popup.html/js/css # загрузка резюме, редактирование навыков
```

## Дальнейшие шаги (не реализовано в MVP)

- Сайт-специфичные экстракторы текста вакансии (hh.ru, LinkedIn, Indeed) вместо
  общей эвристики.
- Многопользовательский режим с аутентификацией (сейчас один профиль на инстанс backend).
- История откликов/совпадений в отдельном разделе попапа (таблица `MatchHistory` уже пишется).
- Сборка под Firefox.
- Кэширование одинаковых сравнений (по хэшу текста вакансии + версии профиля), чтобы не
  тратить токены повторно при возврате на ту же страницу.
