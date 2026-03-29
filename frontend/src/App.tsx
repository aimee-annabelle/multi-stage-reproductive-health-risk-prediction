import { lazy, Suspense } from 'react'
import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import './App.css'
import LandingPage from './pages/LandingPage'
import LegalPage from './pages/LegalPage'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import { useAuthStore } from './stores/authStore'

const DashboardOverviewPage = lazy(() => import('./pages/dashboard/DashboardOverviewPage'))
const InfertilityDashboardPage = lazy(() => import('./pages/dashboard/InfertilityDashboardPage'))
const PregnancyDashboardPage = lazy(() => import('./pages/dashboard/PregnancyDashboardPage'))
const PostpartumDashboardPage = lazy(() => import('./pages/dashboard/PostpartumDashboardPage'))
const PostpartumPredictionPage = lazy(() => import('./pages/dashboard/PostpartumPredictionPage'))

function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <Outlet /> : <Navigate to="/sign-in" replace />
}

function PublicOnlyRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />
}

function DashboardRouteFallback() {
  return <div className="route-loading">Loading dashboard...</div>
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/privacy-policy" element={<LegalPage focus="privacy" />} />
      <Route path="/terms-of-service" element={<LegalPage focus="terms" />} />

      <Route element={<PublicOnlyRoute />}>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route
          path="/dashboard"
          element={
            <Suspense fallback={<DashboardRouteFallback />}>
              <DashboardOverviewPage />
            </Suspense>
          }
        />
        <Route
          path="/dashboard/infertility"
          element={
            <Suspense fallback={<DashboardRouteFallback />}>
              <InfertilityDashboardPage />
            </Suspense>
          }
        />
        <Route
          path="/dashboard/pregnancy"
          element={
            <Suspense fallback={<DashboardRouteFallback />}>
              <PregnancyDashboardPage />
            </Suspense>
          }
        />
        <Route
          path="/dashboard/postpartum"
          element={
            <Suspense fallback={<DashboardRouteFallback />}>
              <PostpartumDashboardPage />
            </Suspense>
          }
        />
        <Route
          path="/dashboard/postpartum/predict"
          element={
            <Suspense fallback={<DashboardRouteFallback />}>
              <PostpartumPredictionPage />
            </Suspense>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
