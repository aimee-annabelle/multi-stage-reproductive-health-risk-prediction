# Diagrams and Screenshots

This folder is intended to store architecture visuals and UI screenshots for EveBloom documentation.

## Planned / In Progress

The following diagrams are planned for this folder:

- `system-architecture.png` — end-to-end component diagram (frontend → backend → ML artifacts → database)
- `erd-diagram.png` — database entity-relationship diagram (users, sessions, assessments)
- `api-screenshot.png` — Swagger UI screenshot from `http://localhost:8000/docs`

## Source of Truth

Until diagrams are added, the authoritative references are:

- `backend/main.py` — active route registrations
- `backend/models/request.py` and `backend/models/response.py` — request/response schemas
- `docs/API_DOCUMENTATION.md` — full API reference
- `db/models.py` — database schema

## Current Functional Areas

- Authentication (`/auth/*`)
- Infertility prediction (`/predict/infertility`)
- Pregnancy prediction (`/predict/pregnancy`)
- Postpartum prediction (`/predict/postpartum`)
- Pregnancy follow-up tracking (`/pregnancy/follow-up/*`)
- Postpartum follow-up tracking (`/postpartum/follow-up/*`)
