import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import OpenAIKeys from './pages/OpenAIKeys'
import Prompts from './pages/Prompts'
import AssistantConfig from './pages/AssistantConfig'
import WidgetGenerator from './pages/WidgetGenerator'
import { useAuthStore } from './context/authStore'
import Layout from './components/Layout'

const queryClient = new QueryClient()

function PrivateRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="openai-keys" element={<OpenAIKeys />} />
            <Route path="prompts" element={<Prompts />} />
            <Route path="assistant-config" element={<AssistantConfig />} />
            <Route path="widget-generator" element={<WidgetGenerator />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App

