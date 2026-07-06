import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Labels from './pages/Labels';
import Folders from './pages/Folders';
import Rules from './pages/Rules';
import EmailLogs from './pages/EmailLogs';
import Profile from './pages/Profile';
import Users from './pages/Users';
import Settings from './pages/Settings';
import Help from './pages/Help';
import DropboxCallback from './pages/DropboxCallback';

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="flex h-screen items-center justify-center text-gray-500">Cargando…</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dropbox/callback" element={<DropboxCallback />} />

          {/* Protegidas (con layout) */}
          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/labels" element={<Labels />} />
            <Route path="/folders" element={<Folders />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/emails" element={<EmailLogs />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/users" element={<Users />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/help" element={<Help />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
