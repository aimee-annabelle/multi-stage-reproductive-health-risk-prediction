# Frontend - EveBloom ML Dashboard

This frontend is the user-facing layer of EveBloom. It presents ML predictions in clear, actionable language and provides workflow support for repeated assessments across infertility, pregnancy, and postpartum stages.

## Frontend Role in the ML Product

The UI is designed to make ML output usable by non-technical users.

- Collects structured inputs aligned to backend inference schemas
- Sends payloads to prediction APIs
- Renders risk scores, classes, and factor-level insights
- Presents user-friendly explanations and recommended next steps
- Displays follow-up timeline signals for ongoing monitoring

## Stack
- React 19
- TypeScript
- Vite
- React Router
- Zustand
- Lucide Icons

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Default URL: `http://localhost:5173`

## Build

```bash
npm run build
npm run preview
```

## Runtime Configuration

Frontend API base URL:
- `VITE_API_URL`

Default fallback if not set:
- `http://localhost:8000`

Example:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Routes

### Public
- `/` - Landing page
- `/sign-in` - Sign-in
- `/sign-up` - Account creation

### Protected
- `/dashboard` - Overview
- `/dashboard/infertility` - Infertility input + result interpretation
- `/dashboard/pregnancy` - Pregnancy monitor + follow-up
- `/dashboard/postpartum` - Postpartum dashboard

## Project Structure

```text
frontend/src/
├── App.tsx
├── main.tsx
├── components/dashboard/
├── pages/
│   ├── LandingPage.tsx
│   ├── SignInPage.tsx
│   ├── SignUpPage.tsx
│   └── dashboard/
├── services/
├── stores/
├── styles/
└── assets/
```

## Docker

Frontend production image uses multi-stage build + Nginx:
- `frontend/Dockerfile`
- `frontend/nginx.conf`

Run with compose:

```bash
docker compose up --build
```

Exposed at `http://localhost:5173`.
