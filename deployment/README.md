# Deployment

This directory is intended for production deployment configuration and Infrastructure-as-Code assets.

## Current State

For local and development deployments, use the root `docker-compose.yml` which brings up the full stack (backend, frontend, PostgreSQL).

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Planned Contents

This folder will hold production deployment assets as the project matures. Expected additions:

- **Kubernetes manifests** — Deployment, Service, Ingress, and ConfigMap YAMLs for a cloud-hosted environment
- **Helm chart** — Parameterised chart for reproducible deployments across environments
- **CI/CD pipeline config** — GitHub Actions or similar workflow definitions for automated build, test, and deploy
- **Environment-specific compose overrides** — `docker-compose.prod.yml` with appropriate environment variable handling

## Environment Variables for Production

When deploying to a hosted environment, at minimum override:

| Variable       | Description                                        |
| -------------- | -------------------------------------------------- |
| `DATABASE_URL` | Full PostgreSQL connection string with credentials |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins   |
| `ENVIRONMENT`  | Set to `production`                                |
| `DEBUG`        | Set to `False`                                     |
| `VITE_API_URL` | Backend public URL, set at frontend build time     |

Refer to `backend/.env.example` for the full list of backend environment variables.

## Docker Images

- Backend: `backend/Dockerfile` — Python 3.12, FastAPI, uvicorn
- Frontend: `frontend/Dockerfile` — multi-stage Node build + Nginx static serve
