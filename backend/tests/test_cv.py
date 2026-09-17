import io

from app.routers import cv as cv_router


def test_upload_cv(client, monkeypatch):
    def fake_extract_skills(text):
        assert "Python" in text
        return {
            "skills": [{"name": "Python", "level": None}, {"name": "SQL", "level": None}],
            "summary": "Experienced backend developer.",
        }

    monkeypatch.setattr(cv_router, "extract_skills", fake_extract_skills)

    res = client.post(
        "/api/cv",
        files={"file": ("resume.txt", io.BytesIO(b"Python, SQL developer, 3 years"), "text/plain")},
    )
    assert res.status_code == 200
    data = res.json()
    assert {s["name"] for s in data["skills"]} == {"Python", "SQL"}
    assert data["summary"] == "Experienced backend developer."


def test_upload_cv_unsupported_format(client):
    res = client.post(
        "/api/cv",
        files={"file": ("resume.xyz", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert res.status_code == 400
