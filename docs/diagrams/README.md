# Diagrams and Screenshots

This folder contains architecture and API screenshots for documentation.

## Files

- `class-diagram.png`
- `erd-diagram.png`
- `system-architecture.png`
- `api-screenshot.png`

## Important Note

Some diagram images were created earlier in development and may not include all current endpoints.

Current source of truth for implementation is:

- `backend/main.py` (active API routes)
- `backend/models/request.py` and `backend/models/response.py` (schemas)
- `docs/API_DOCUMENTATION.md` (written API reference)

## Current Implemented API Areas

- Authentication (`/auth/*`)
- Infertility prediction (`/predict/infertility`)
- Pregnancy prediction (`/predict/pregnancy`)
- Pregnancy follow-up tracking:
  - `/pregnancy/follow-up/assess`
  - `/pregnancy/follow-up/history`
  - `/pregnancy/follow-up/compare/latest`
  - `/pregnancy/follow-up/timeline/summary`
