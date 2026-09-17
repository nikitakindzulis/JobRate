def test_profile_empty_by_default(client):
    res = client.get("/api/profile")
    assert res.status_code == 200
    assert res.json()["skills"] == []


def test_update_profile_skills(client):
    res = client.put("/api/profile", json={"skills": ["Python", "FastAPI", ""]})
    assert res.status_code == 200
    names = [s["name"] for s in res.json()["skills"]]
    assert names == ["Python", "FastAPI"]  # blank entries are dropped

    res = client.get("/api/profile")
    names = [s["name"] for s in res.json()["skills"]]
    assert names == ["Python", "FastAPI"]


def test_update_profile_replaces_previous_skills(client):
    client.put("/api/profile", json={"skills": ["Python"]})
    res = client.put("/api/profile", json={"skills": ["Docker"]})
    names = [s["name"] for s in res.json()["skills"]]
    assert names == ["Docker"]
