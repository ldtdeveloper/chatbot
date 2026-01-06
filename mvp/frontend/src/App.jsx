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
import { Toaster } from "sonner";
import ResetPassword from './pages/ResetPassword'

const queryClient = new QueryClient()

function PrivateRoute({ children }) {
  const { token, refreshAuth } = useAuthStore()
  
  // Refresh auth on mount to ensure token is loaded from localStorage
  useEffect(() => {
    if (!token) {
      refreshAuth()
    }
  }, [token, refreshAuth])
  
  return token ? children : <Navigate to="/login" />
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
          </Route>
          <Route path ="reset-password" element={<ResetPassword />} />
        </Routes>
        <Toaster position="top-center" richColors />
      </Router>
    </QueryClientProvider>
  )
}

export default App
