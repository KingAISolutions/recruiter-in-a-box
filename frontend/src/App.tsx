import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { Layout, AuthLayout } from '@/components/layout'
import {
  LoginPage,
  SignupPage,
  DashboardPage,
  CandidatesPage,
  JobsPage,
  TemplatesPage,
  OutreachPage,
  AnalyticsPage,
  SettingsPage,
} from '@/pages'
import LandingPage from '@/pages/Landing'
import PricingPage from '@/pages/Pricing'
import TeamPage from '@/pages/Team'
import InterviewsPage from '@/pages/Interviews'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public pages */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/pricing" element={<PricingPage />} />

        {/* Auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/join" element={<LoginPage />} /> {/* Team invite acceptance */}
        </Route>

        {/* Protected routes */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/candidates/:id" element={<CandidatesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/outreach" element={<OutreachPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/team" element={<TeamPage />} />
          <Route path="/interviews" element={<InterviewsPage />} />
        </Route>

        {/* Default redirects */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
