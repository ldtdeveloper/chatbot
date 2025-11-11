# Environment Configuration Guide

This project supports three environments: **LOCAL**, **DEV**, and **PROD**.

## Quick Setup

### Backend

1. **Copy the appropriate .env.example file:**
   ```bash
   # For local development
   cp .env.local.example .env
   
   # For development server
   cp .env.dev.example .env.dev
   
   # For production
   cp .env.prod.example .env.prod
   ```

2. **Set the environment variable:**
   ```bash
   # Local development (default)
   export APP_ENV=LOCAL
   
   # Development server
   export APP_ENV=DEV
   
   # Production
   export APP_ENV=PROD
   ```

3. **Update the .env file with your values**

### Frontend

1. **Copy the appropriate .env.example file:**
   ```bash
   # For local development
   cp .env.local.example .env
   
   # For development server
   cp .env.dev.example .env
   
   # For production builds
   cp .env.prod.example .env.production
   ```

2. **Set the environment variable in .env:**
   ```env
   VITE_APP_ENV=DEV  # or LOCAL, PROD
   ```

3. **For production builds:**
   ```bash
   VITE_APP_ENV=PROD npm run build
   ```

## Environment Details

### LOCAL (Default)
- **Backend:** Runs on `0.0.0.0:8000`, DEBUG=True
- **Frontend:** API URL: `http://localhost:8000`
- **CORS:** `http://localhost:3000`, `http://localhost:5173`
- **Use case:** Local development on your machine

### DEV
- **Backend:** Runs on `127.0.0.1:8000`, DEBUG=True
- **Frontend:** API URL: Set via `VITE_API_BASE_URL` in .env
- **CORS:** Configured in backend .env file
- **Use case:** Development server deployment

### PROD
- **Backend:** Runs on `127.0.0.1:8000`, DEBUG=False
- **Frontend:** API URL: `https://chat-api.ldttechnology.in`
- **CORS:** 
  - `https://chat.ldttechnology.in`
  - `https://chat-api.ldttechnology.in`
- **Use case:** Production deployment on subdomains

## Subdomain Configuration

### Production Subdomains
- **Frontend:** `https://chat.ldttechnology.in`
- **Backend API:** `https://chat-api.ldttechnology.in`

## Usage Examples

### Backend

```python
from app.config import settings

# Check current environment
if settings.is_prod:
    print("Running in production")
elif settings.is_dev:
    print("Running in development")
else:
    print("Running locally")

# Access configuration
print(f"Database: {settings.database_url}")
print(f"Debug mode: {settings.debug}")
print(f"CORS origins: {settings.cors_origins}")
```

### Frontend

```javascript
import config, { isLocal, isDev, isProd } from './config/env'

// Check current environment
if (isProd()) {
  console.log('Running in production')
}

// Access configuration
console.log('API URL:', config.API_BASE_URL)
```

## File Structure

```
backend/
├── .env.local.example    # Local development environment template
├── .env.dev.example      # Development server environment template
├── .env.prod.example     # Production environment template
└── app/
    └── config.py         # Environment-aware configuration

frontend/
├── .env.local.example    # Local development environment template
├── .env.dev.example      # Development server environment template
├── .env.prod.example     # Production environment template
└── src/
    └── config/
        └── env.js        # Environment-aware configuration
```

## Switching Environments

### Backend
Change the `APP_ENV` environment variable:
```bash
export APP_ENV=PROD
python main.py
```

Or set it in your .env file:
```env
APP_ENV=PROD
```

### Frontend
Change `VITE_APP_ENV` in your .env file:
```env
VITE_APP_ENV=PROD
```

Then rebuild:
```bash
npm run build
```

## Notes

- The backend automatically loads `.env.prod` when `APP_ENV=PROD`
- The backend automatically loads `.env.dev` when `APP_ENV=DEV`
- The backend uses `.env` for `APP_ENV=LOCAL` (default)
- If environment-specific .env files don't exist, it falls back to `.env`
- Production CORS origins are automatically set for the subdomains
- Frontend config uses the environment variable to determine API URL

## Environment File Templates

All environment example files are available:
- **Backend:** `.env.local.example`, `.env.dev.example`, `.env.prod.example`
- **Frontend:** `.env.local.example`, `.env.dev.example`, `.env.prod.example`

Copy the appropriate template based on your deployment environment.

