/**
 * Environment Configuration Handler
 * Supports: LOCAL, DEV, PROD
 * 
 * Reads configuration from environment variables (VITE_API_BASE_URL, VITE_APP_ENV)
 * 
 * Usage:
 *   import { config } from './config/env'
 *   const apiUrl = config.API_BASE_URL
 */

const APP_ENV = import.meta.env.VITE_APP_ENV || 'LOCAL'

// Get API base URL from environment variable, with fallbacks
const getApiBaseUrl = () => {
  // Always try to read from VITE_API_BASE_URL first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // Fallback based on environment
  const env = APP_ENV.toUpperCase()
  switch (env) {
    case 'LOCAL':
      return 'http://localhost:8000'
    case 'DEV':
      return 'http://localhost:8000' // Should be set in .env file
    case 'PROD':
      return 'https://chat-api.ldttechnology.in' // Production default
    default:
      return 'http://localhost:8000'
  }
}

// Get current environment config
const getConfig = () => {
  return {
    API_BASE_URL: getApiBaseUrl(),
    APP_ENV: APP_ENV.toUpperCase(),
  }
}

const config = getConfig()

// Helper functions
export const isLocal = () => config.APP_ENV === 'LOCAL'
export const isDev = () => config.APP_ENV === 'DEV'
export const isProd = () => config.APP_ENV === 'PROD'

// Export configuration
export default config

