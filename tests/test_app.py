import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "rlm-release"


def test_metrics(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "rlm-release"


def test_vote_success(client):
    resp = client.post("/vote", json={"choice": "yes"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["choice"] == "yes"


def test_vote_missing_choice(client):
    resp = client.post("/vote", json={})
    assert resp.status_code == 400


def test_bump_patch(client):
    resp = client.post("/bump", json={"version": "1.2.3", "level": "patch"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version"] == "1.2.4"


def test_bump_minor(client):
    resp = client.post("/bump", json={"version": "1.2.3", "level": "minor"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version"] == "1.3.0"


def test_bump_major(client):
    resp = client.post("/bump", json={"version": "1.2.3", "level": "major"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version"] == "2.0.0"


def test_bump_invalid_level(client):
    resp = client.post("/bump", json={"version": "1.0.0", "level": "bad"})
    assert resp.status_code == 400


def test_changelog_feat_minor(client):
    resp = client.post("/changelog", json={"commits": ["feat: add auth", "fix: typo"]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version_bump"] == "minor"


def test_changelog_breaking_major(client):
    resp = client.post("/changelog", json={"commits": ["feat!: breaking change"]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version_bump"] == "major"


def test_changelog_missing_commits(client):
    resp = client.post("/changelog", json={})
    assert resp.status_code == 400


def test_tag_missing_version(client):
    resp = client.post("/tag", json={})
    assert resp.status_code == 400


def test_release_missing_version(client):
    resp = client.post("/release", json={})
    assert resp.status_code == 400


def test_status(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "rlm-release"
