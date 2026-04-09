# Diagrams and Screenshots

This folder is intended to store architecture visuals and UI screenshots for EveBloom documentation.

## Available Assets

- `system_architecture.puml` — editable PlantUML source for the layered architecture diagram
- `system-architecture.png` — exported architecture image used in documentation
- `erd-diagram.png` — database entity-relationship diagram (users, sessions, assessments)
- `class-diagram.png` — class diagram image used in report documentation
- `api-screenshot.png` — Swagger UI screenshot from `http://localhost:8000/docs`

## Source of Truth

When updating diagrams, the authoritative references are:

- `backend/main.py` — active route registrations
- `backend/models/request.py` and `backend/models/response.py` — request/response schemas
- `docs/API_DOCUMENTATION.md` — full API reference
- `backend/db/models.py` — database schema
- `backend/services/model_service.py` — runtime artifact loading and model lineage

## Current Functional Areas

- Authentication (`/auth/*`)
- Infertility prediction (`/predict/infertility`)
- Pregnancy prediction (`/predict/pregnancy`)
- Postpartum prediction (`/predict/postpartum`)
- Pregnancy follow-up tracking (`/pregnancy/follow-up/*`)
- Postpartum follow-up tracking (`/postpartum/follow-up/*`)
