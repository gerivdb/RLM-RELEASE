# RLM-RELEASE

Release management service for the RLM ecosystem.

- Port: `8799`
- Role: semantic versioning, changelog, tagging, GitHub release
- Stack: Flask + SQLite (future state persistence)

## Endpoints

| Method | Path       | Purpose                       |
|--------|------------|-------------------------------|
| GET    | /health    | Liveness check                |
| GET    | /metrics   | Release counts                |
| POST   | /vote      | Record a vote                 |
| POST   | /bump      | Compute next version          |
| POST   | /changelog | Derive bump from commits      |
| POST   | /tag       | Create release tag            |
| POST   | /release   | Publish release               |
| GET    | /status    | Service status                |

## Run

```powershell
python src/app.py
```

## Test

```powershell
pytest tests/test_app.py -q
```

## Archi notes

- MVP: in-memory bump/changelog/tag/release
- Next: git log parsing, GitHub release creation, artifact publishing
