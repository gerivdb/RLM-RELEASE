from flask import Flask, jsonify, request
import os
import re
from datetime import datetime, timezone

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 8799))
RELEASES: dict = {}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_version(version: str) -> tuple[int, int, int]:
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version or "0.0.0")
    if not match:
        return 0, 0, 0
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _bump_version(version: str, level: str) -> str:
    major, minor, patch = _parse_version(version)
    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def _analyze_commits(commits: list[str]) -> str:
    level = "patch"
    for commit in commits:
        if commit.startswith("feat!"):
            level = "major"
            break
        if commit.startswith("feat"):
            level = "minor"
    return level


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "rlm-release", "port": PORT}), 200


@app.get("/metrics")
def metrics():
    return jsonify({
        "service": "rlm-release",
        "port": PORT,
        "releases": len(RELEASES),
        "timestamp": _utcnow(),
    }), 200


@app.post("/vote")
def vote():
    data = request.get_json(silent=True) or {}
    choice = data.get("choice")
    if not choice:
        return jsonify({"error": "missing choice"}), 400
    return jsonify({"choice": choice, "count": 1}), 200


@app.post("/bump")
def bump():
    data = request.get_json(silent=True) or {}
    version = data.get("version", "0.0.0")
    level = data.get("level", "patch")
    if level not in {"major", "minor", "patch"}:
        return jsonify({"error": "invalid level"}), 400

    new_version = _bump_version(version, level)
    return jsonify({"version": new_version, "level": level}), 200


@app.post("/changelog")
def changelog():
    data = request.get_json(silent=True) or {}
    commits = data.get("commits", [])
    if not commits:
        return jsonify({"error": "missing commits"}), 400

    level = _analyze_commits(commits)
    entries = []
    for commit in commits:
        kind = "patch"
        if commit.startswith("feat!"):
            kind = "major"
        elif commit.startswith("feat"):
            kind = "minor"
        entries.append({"commit": commit, "kind": kind})

    return jsonify({
        "version_bump": level,
        "entries": entries,
        "timestamp": _utcnow(),
    }), 200


@app.post("/tag")
def tag():
    data = request.get_json(silent=True) or {}
    version = data.get("version")
    if not version:
        return jsonify({"error": "missing version"}), 400

    tag_name = f"v{version}"
    release_id = f"release-{len(RELEASES) + 1}"
    RELEASES[release_id] = {
        "version": version,
        "tag": tag_name,
        "status": "tagged",
        "timestamp": _utcnow(),
    }
    return jsonify({"id": release_id, "tag": tag_name, "status": "tagged"}), 201


@app.post("/release")
def release():
    data = request.get_json(silent=True) or {}
    version = data.get("version")
    if not version:
        return jsonify({"error": "missing version"}), 400

    release_id = f"release-{len(RELEASES) + 1}"
    RELEASES[release_id] = {
        "version": version,
        "tag": f"v{version}",
        "status": "published",
        "timestamp": _utcnow(),
    }
    return jsonify({"id": release_id, "version": version, "status": "published"}), 201


@app.get("/status")
def status():
    return jsonify({"service": "rlm-release", "port": PORT, "mode": "standby"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
