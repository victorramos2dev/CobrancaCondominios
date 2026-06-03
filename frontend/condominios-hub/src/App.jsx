import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/shared/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage       from './pages/LoginPage'
import DashboardPage   from './pages/DashboardPage'
import CondominiosPage from './pages/CondominiosPage'
import UnidadesPage    from './pages/UnidadesPage'
import CobrancasPage   from './pages/CobrancasPage'
import InadimplenciaPage from './pages/InadimplenciaPage'
import AcordosPage     from './pages/AcordosPage'

function PrivatePage({ children, adminOnly }) {
  return (
    <ProtectedRoute adminOnly={adminOnly}>
      <AppLayout>{children}</AppLayout>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="/" element={
            <PrivatePage><DashboardPage /></PrivatePage>
          } />
          <Route path="/condominios" element={
            <PrivatePage><CondominiosPage /></PrivatePage>
          } />
          <Route path="/unidades" element={
            <PrivatePage><UnidadesPage /></PrivatePage>
          } />
          <Route path="/cobrancas" element={
            <PrivatePage><CobrancasPage /></PrivatePage>
          } />
          <Route path="/inadimplencia" element={
            <PrivatePage><InadimplenciaPage /></PrivatePage>
          } />
          <Route path="/acordos" element={
            <PrivatePage><AcordosPage /></PrivatePage>
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
