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
├── components/dashboard/
│   ├── DashboardLayout.tsx
│   ├── DashboardRightRail.tsx
│   └── DashboardSidebar.tsx
├── pages/
│   ├── LandingPage.tsx
│   ├── SignInPage.tsx
│   ├── SignUpPage.tsx
│   └── dashboard/
│       ├── DashboardOverviewPage.tsx
│       ├── InfertilityDashboardPage.tsx
│       ├── PregnancyDashboardPage.tsx
│       └── PostpartumDashboardPage.tsx
├── services/
│   ├── authApi.ts
│   ├── apiClient.ts
│   ├── predictionApi.ts
│   └── pregnancyFollowUpApi.ts
├── stores/
│   └── authStore.ts
├── utils/
│   └── dashboardSnapshot.ts
├── styles/
│   ├── auth.css
│   └── landing.css
└── assets/
```

## Routing

- `/` landing page
- `/sign-in` sign-in page
- `/sign-up` sign-up page
- `/dashboard` protected overview route
- `/dashboard/infertility` protected infertility assessment
- `/dashboard/pregnancy` protected pregnancy follow-up assessment
- `/dashboard/postpartum` protected postpartum assessment

## Backend Integration

The frontend consumes backend endpoints from `backend/main.py`.

Typical local setup:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

Make sure backend CORS allows frontend origin (`CORS_ORIGINS`).
