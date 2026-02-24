# Frontend

React + TypeScript frontend for the reproductive health prediction system.

## Tech Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- Zustand

## Setup

```bash
cd frontend
npm install
```

## Run

```bash
npm run dev
```

Default dev URL: `http://localhost:5173`

## Build

```bash
npm run build
npm run preview
```

## Current App Structure

```text
frontend/src/
├── App.tsx
├── main.tsx
├── pages/
│   ├── LandingPage.tsx
│   ├── SignInPage.tsx
│   ├── SignUpPage.tsx
│   └── DashboardPage.tsx
├── services/
│   ├── authApi.ts
│   └── infertilityApi.ts
├── stores/
│   ├── authStore.ts
│   └── dashboardStore.ts
├── styles/
│   ├── auth.css
│   ├── dashboard.css
│   └── landing.css
└── assets/
```

## Routing

- `/` landing page
- `/sign-in` sign-in page
- `/sign-up` sign-up page
- `/dashboard` protected route (requires auth state)

## Backend Integration

The frontend consumes backend endpoints from `backend/main.py`.

Typical local setup:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

Make sure backend CORS allows frontend origin (`CORS_ORIGINS`).
