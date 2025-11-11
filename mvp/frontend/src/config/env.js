/**
 * Environment Configuration Handler
 * Supports: LOCAL, DEV, PROD
 * 
 * Usage:
 *   import { config } from './config/env'
 *   const apiUrl = config.API_BASE_URL
 */

const APP_ENV = import.meta.env.VITE_APP_ENV || 'LOCAL'

// Environment-specific configurations
const environments = {
  LOCAL: {
    API_BASE_URL: 'http://localhost:8000',
    APP_ENV: 'LOCAL',
  },
  DEV: {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    APP_ENV: 'DEV',
  },
  PROD: {
    API_BASE_URL: 'https://chat-api.ldttechnology.in',
    APP_ENV: 'PROD',
  },
}

// Get current environment config
const getConfig = () => {
  const env = APP_ENV.toUpperCase()
  
  switch (env) {
    case 'LOCAL':
      return environments.LOCAL
    case 'DEV':
      return environments.DEV
    case 'PROD':
      return environments.PROD
    default:
      console.warn(`Unknown environment: ${env}, defaulting to LOCAL`)
      return environments.LOCAL
  }
}

const config = getConfig()

// Helper functions
export const isLocal = () => config.APP_ENV === 'LOCAL'
export const isDev = () => config.APP_ENV === 'DEV'
export const isProd = () => config.APP_ENV === 'PROD'

// Export configuration
export default config

