from app.routers import match as match_router


def test_match_requires_profile(client):
    res = client.post("/api/match", json={"job_text": "We need a Python developer"})
    assert res.status_code == 400


def test_match_requires_job_text(client):
    client.put("/api/profile", json={"skills": ["Python"]})
    res = client.post("/api/match", json={"job_text": "   "})
    assert res.status_code == 400


def test_match_success(client, monkeypatch):
    client.put("/api/profile", json={"skills": ["Python", "Docker"]})

    def fake_match_job(profile_skills, job_text):
        assert profile_skills == [
            {"name": "Python", "level": None},
            {"name": "Docker", "level": None},
        ]
        return {
            "match_percent": 50,
            "matched_skills": ["Python"],
            "missing_skills": ["Kubernetes"],
            "nice_to_have": [],
            "summary": "Good partial match.",
        }

    monkeypatch.setattr(match_router, "match_job", fake_match_job)

    res = client.post("/api/match", json={"job_text": "Need Python and Kubernetes"})
    assert res.status_code == 200
    data = res.json()
    assert data["match_percent"] == 50
    assert data["matched_skills"] == ["Python"]
    assert data["missing_skills"] == ["Kubernetes"]
