import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "./context/AuthContext"
import { ProtectedRoute, CandidateRoute, ExaminerRoute } from "./components/ProtectedRoute"
import Landing from "./pages/Landing"
import CandidateDashboard from "./pages/CandidateDashboard"
import ExaminerDashboard from "./pages/ExaminerDashboard"
import ExamRoom from "./pages/ExamRoom"



// ── Root redirect based on role ───────────────────────────────────────────────
function RootRedirect() {
  const { user } = useAuth()
  if (!user) return <Landing />
  if (user.role === "candidate") return <Navigate to="/dashboard" replace />
  return <Navigate to="/examiner/dashboard" replace />
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/" element={<RootRedirect />} />

          {/* Candidate routes — wrap element, not Route */}
          <Route path="/dashboard" element={
            <CandidateRoute><CandidateDashboard /></CandidateRoute>
          } />

          <Route path="/exam/:examId" element={
            <CandidateRoute><ExamRoom /></CandidateRoute>
          } />

          <Route path="/examiner/dashboard" element={
            <ExaminerRoute><ExaminerDashboard /></ExaminerRoute>
          } />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}