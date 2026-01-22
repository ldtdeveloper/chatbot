import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import EditProfile from './pages/EditProfile'
import Users from './pages/Users'
import UserProfile from './pages/UserProfile'
import OpenAIKeys from './pages/OpenAIKeys'
import Agents from './pages/Agents'
import Assistants from './pages/Assistants'
import WidgetGenerator from './pages/WidgetGenerator'
import { useAuthStore } from './context/authStore'
import Layout from './components/Layout'
import ResetPassword from './pages/ResetPassword'
import { bootstrapAuth } from './auth/bootstrapAuth'
import {Toaster} from "sonner";
import Plans from './pages/Plans'
const queryClient = new QueryClient()

function PrivateRoute({ children }) {
  const { token, refreshAuth } = useAuthStore()
  
  // Refresh auth on mount to ensure token is loaded from localStorage
  useEffect(() => {
    if (!token) {
      refreshAuth()
    }
  }, [token, refreshAuth])
    const { setAuth } = useAuthStore()

  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === 'token') {
        window.location.reload();
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  useEffect(() => {
    bootstrapAuth(setAuth)
  }, [])
  // Fallback check — prevents redirect before effects have a chance to run
  const isAuthenticated = !!token || !!localStorage.getItem('token')

  return isAuthenticated ? children : <Navigate to="/login" replace />
  // return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
        
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="users" element={<Users />} />
            <Route path="users/:userId/profile" element={<UserProfile />} />
            <Route path="users/:userId/profile-update" element={<EditProfile />} />
            <Route path="openai-keys" element={<OpenAIKeys />} />
            <Route path="agents" element={<Agents />} />
            <Route path="assistants" element={<Assistants />} />
            <Route path="widget-generator" element={<WidgetGenerator />} />
            <Route path ="plans" element={<Plans/>}/>

          </Route>
          <Route path ="password" element={<ResetPassword />} />
        </Routes>
        <Toaster richColors position="top-right" />
      </Router>
    </QueryClientProvider>
  )
}

export default App
