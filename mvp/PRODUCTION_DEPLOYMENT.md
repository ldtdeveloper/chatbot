# Voice Assistant MVP - Deployment Guide

Deployment guide for preview server with static IP, accessible via subfolder.

**Replace `YOUR_STATIC_IP` with actual server IP throughout this guide.**

## Backend Setup

### 1. Install Dependencies

```bash
cd /var/www/html/voice-assistant/mvp/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify installation:**
```bash
# Check installed packages
pip list

# Verify all dependencies are available
python3 -c "import fastapi, uvicorn, sqlalchemy, pydantic, jose, passlib, httpx, openai, cryptography; print('All dependencies installed')"
```

**Note:** `bcrypt` is included via `passlib[bcrypt]`, so no separate installation needed.

### 2. Configure Environment

Copy the appropriate environment file based on your deployment:

```bash
# For development/preview server
cp .env.dev.example .env

# For production (if needed)
cp .env.prod.example .env.prod
```

Edit the `.env` file with your values:

```env
# Environment (LOCAL, DEV, PROD)
APP_ENV=DEV

# Database Configuration
DATABASE_URL=sqlite:///./chatbot.db

# Security - Generate a strong secret key
SECRET_KEY=<generate-with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=True

# CORS Origins (JSON array format)
CORS_ORIGINS=["http://YOUR_STATIC_IP","http://YOUR_STATIC_IP/voice-assistant"]

# OpenAI API Configuration
OPENAI_API_BASE=https://api.openai.com/v1
```

**Note:** Replace `YOUR_STATIC_IP` with your actual server IP address.

### 3. Initialize Database and Seed Superadmin

```bash
source venv/bin/activate
python3 seed_db.py
```

This will:
- Create all database tables
- Create/update superadmin user (email: `superadmin@yopmail.com`, password: `123456`)

### 4. Create Systemd Service

Create `/etc/systemd/system/voice-assistant-backend.service`:

```ini
[Unit]
Description=Voice Assistant Backend API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/voice-assistant/mvp/backend
Environment="PATH=/var/www/html/voice-assistant/mvp/backend/venv/bin"
Environment="APP_ENV=DEV"
ExecStart=/var/www/html/voice-assistant/mvp/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** Set `APP_ENV=DEV` for development/preview server, or `APP_ENV=PROD` for production.

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant-backend.service
sudo systemctl start voice-assistant-backend.service
```

## Frontend Setup

### 1. Configure Vite

Update `/var/www/html/voice-assistant/mvp/frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/voice-assistant/',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 2. Set Environment Configuration

Copy the appropriate environment file:

```bash
# For development/preview server
cp .env.dev.example .env

# For production builds
cp .env.prod.example .env.production
```

Edit the `.env` file:

```env
# Environment (LOCAL, DEV, PROD)
VITE_APP_ENV=DEV

# API Base URL
VITE_API_BASE_URL=http://YOUR_STATIC_IP/voice-assistant/api
```

**Note:** Replace `YOUR_STATIC_IP` with your actual server IP address.

### 3. Build Frontend

```bash
cd /var/www/html/voice-assistant/mvp/frontend
npm install
npm run build
```

## Nginx Configuration

Add to existing server block or create new one in `/etc/nginx/sites-available/default`:

```nginx
upstream voice_assistant_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name YOUR_STATIC_IP _;

    root /var/www/html;
    index index.html;

    location /voice-assistant {
        alias /var/www/html/voice-assistant/mvp/frontend/dist;
        try_files $uri $uri/ /voice-assistant/index.html;
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    }

    location /voice-assistant/api {
        rewrite ^/voice-assistant/api/(.*) /api/$1 break;
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /voice-assistant/health {
        proxy_pass http://voice_assistant_backend/health;
        access_log off;
    }
}
```

Test and reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Permissions

```bash
sudo chown -R www-data:www-data /var/www/html/voice-assistant/mvp
sudo chmod -R 755 /var/www/html/voice-assistant/mvp
sudo chmod -R 775 /var/www/html/voice-assistant/mvp/backend/venv
sudo chmod 664 /var/www/html/voice-assistant/mvp/backend/chatbot.db
```

## Access URLs

- Frontend: `http://YOUR_STATIC_IP/voice-assistant`
- API: `http://YOUR_STATIC_IP/voice-assistant/api`
- Health: `http://YOUR_STATIC_IP/voice-assistant/health`

## Maintenance

### Restart Backend
```bash
sudo systemctl restart voice-assistant-backend.service
```

### Update Application
```bash
cd /var/www/html/voice-assistant
git pull origin main

# Backend
cd mvp/backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart voice-assistant-backend.service

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

### View Logs
```bash
# Backend
sudo journalctl -u voice-assistant-backend.service -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

**Backend not starting:**
```bash
sudo systemctl status voice-assistant-backend.service
sudo journalctl -u voice-assistant-backend.service -n 50
```

**Nginx 502:**
- Verify backend running: `sudo systemctl status voice-assistant-backend.service`
- Check backend listening: `sudo netstat -tlnp | grep 8000`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

**CORS errors:**
- Verify CORS_ORIGINS in backend .env includes server IP
- Check frontend .env.production has correct API URL

**Frontend 404:**
- Verify `base` in vite.config.js matches Nginx location path
- Rebuild frontend after changing base path
- Check Nginx alias path points to correct dist directory
