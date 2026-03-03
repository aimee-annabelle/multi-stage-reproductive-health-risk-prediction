# Diagrams and Screenshots

This folder stores architecture visuals and UI screenshots for EveBloom documentation.

## Files

- `system-architecture.png`
- `erd-diagram.png`
- `class-diagram.png`
- `api-screenshot.png`

## Notes

Some images may represent earlier development snapshots.

Current implementation source of truth:
- `backend/main.py` (active endpoints)
- `backend/models/request.py` and `backend/models/response.py` (schemas)
- `docs/API_DOCUMENTATION.md` (reference docs)

## Current Functional Areas

- Authentication (`/auth/*`)
- Infertility prediction (`/predict/infertility`)
- Pregnancy prediction (`/predict/pregnancy`)
- Postpartum prediction (`/predict/postpartum`)
- Pregnancy follow-up tracking (`/pregnancy/follow-up/*`)
- Postpartum follow-up tracking (`/postpartum/follow-up/*`)
