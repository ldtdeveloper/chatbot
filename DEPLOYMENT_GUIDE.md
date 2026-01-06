# Voice Assistant Platform - Complete Deployment Guide with Nginx

This guide provides step-by-step instructions for deploying the Voice Assistant Platform on a production server using Nginx as a reverse proxy.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Nginx Configuration](#nginx-configuration)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Database Setup](#database-setup)
8. [Environment Configuration](#environment-configuration)
9. [Service Management](#service-management)
10. [Security Hardening](#security-hardening)
11. [Monitoring & Logging](#monitoring--logging)
12. [Troubleshooting](#troubleshooting)
13. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or later (or similar Linux distribution)
- Minimum 2 CPU cores, 4GB RAM, 20GB disk space
- Root or sudo access
- Domain name(s) configured (optional but recommended)

### Software Requirements
- Python 3.10 or higher
- Node.js 18.x or higher
- Nginx
- PostgreSQL or SQLite (for production, PostgreSQL is recommended)
- Git

### Domain Setup (Recommended)
- `yourdomain.com` - Frontend application
- `api.yourdomain.com` - Backend API
- DNS A records pointing to your server IP

---

## Server Setup

### 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Software

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install -y nginx

# Install PostgreSQL (optional, for production)
sudo apt install -y postgresql postgresql-contrib

# Install Git
sudo apt install -y git

# Install build essentials (for compiling Python packages)
sudo apt install -y build-essential libssl-dev libffi-dev

# Install Certbot for SSL certificates
sudo apt install -y certbot python3-certbot-nginx
```

### 3. Create Application User

```bash
# Create a dedicated user for the application
sudo useradd -m -s /bin/bash voiceassistant
sudo usermod -aG www-data voiceassistant
```

### 4. Create Application Directory

```bash
# Create directory structure
sudo mkdir -p /var/www/voice-assistant
sudo chown voiceassistant:www-data /var/www/voice-assistant
```

---

## Backend Deployment

### 1. Clone Repository

```bash
cd /var/www/voice-assistant
sudo -u voiceassistant git clone <your-repository-url> .
# Or if you already have the code:
# sudo -u voiceassistant cp -r /path/to/your/code/* .
```

### 2. Set Up Python Virtual Environment

```bash
cd /var/www/voice-assistant/mvp/backend
sudo -u voiceassistant python3 -m venv venv
sudo -u voiceassistant source venv/bin/activate
sudo -u voiceassistant pip install --upgrade pip
sudo -u voiceassistant pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cd /var/www/voice-assistant/mvp/backend
sudo -u voiceassistant nano .env
```

**Example `.env` file:**

```env
# Environment
APP_ENV=PROD
DEBUG=False

# Database
DATABASE_URL=postgresql://voiceassistant:your_password@localhost:5432/voiceassistant_db
# Or for SQLite:
# DATABASE_URL=sqlite:///./chatbot.db

# Security
SECRET_KEY=your-super-secret-key-here-generate-with-python-secrets-module

# Server Configuration
HOST=127.0.0.1
PORT=8081

# CORS Origins (comma-separated or JSON array)
CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]

# API Base URL
API_BASE_URL=https://api.yourdomain.com

# OpenAI Configuration
OPENAI_API_BASE=https://api.openai.com/v1

# Email Configuration (for sending emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Razorpay Configuration (if using payment gateway)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Initialize Database

```bash
cd /var/www/voice-assistant/mvp/backend
sudo -u voiceassistant source venv/bin/activate

# For SQLite (creates database automatically)
python3 -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# For PostgreSQL, create database first:
# sudo -u postgres psql
# CREATE DATABASE voiceassistant_db;
# CREATE USER voiceassistant WITH PASSWORD 'your_password';
# GRANT ALL PRIVILEGES ON DATABASE voiceassistant_db TO voiceassistant;
# \q

# Seed database with superadmin
python3 seed_db.py
```

### 5. Test Backend

```bash
cd /var/www/voice-assistant/mvp/backend
sudo -u voiceassistant source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8081
```

Visit `http://your-server-ip:8081/docs` to verify the API is working.

---

## Frontend Deployment

### 1. Install Dependencies

```bash
cd /var/www/voice-assistant/mvp/frontend
sudo -u voiceassistant npm install
```

### 2. Configure Environment

```bash
cd /var/www/voice-assistant/mvp/frontend
sudo -u voiceassistant nano .env.production
```

**Example `.env.production` file:**

```env
VITE_APP_ENV=PROD
VITE_API_BASE_URL=https://api.yourdomain.com
```

### 3. Update Vite Configuration

```bash
cd /var/www/voice-assistant/mvp/frontend
sudo -u voiceassistant nano vite.config.js
```

**Production `vite.config.js`:**

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
      },
    },
  },
})
```

### 4. Build Frontend

```bash
cd /var/www/voice-assistant/mvp/frontend
sudo -u voiceassistant npm run build
```

This creates the `dist` directory with production-ready files.

### 5. Set Permissions

```bash
sudo chown -R voiceassistant:www-data /var/www/voice-assistant
sudo chmod -R 755 /var/www/voice-assistant
sudo chmod -R 775 /var/www/voice-assistant/mvp/backend/venv
```

---

## Nginx Configuration

### 1. Create Nginx Configuration File

```bash
sudo nano /etc/nginx/sites-available/voice-assistant
```

### 2. Frontend Configuration (Main Domain)

```nginx
# Upstream backend server
upstream voice_assistant_backend {
    server 127.0.0.1:8081;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Frontend Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (will be updated by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Root directory for frontend
    root /var/www/voice-assistant/mvp/frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript 
               text/xml application/xml application/xml+rss text/javascript 
               application/x-javascript text/x-js;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Serve frontend SPA
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Disable buffering for streaming responses
        proxy_buffering off;
    }

    # WebSocket support for real-time features
    location /api/widget/ws {
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
        
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 3. Backend API Configuration (Subdomain)

```bash
sudo nano /etc/nginx/sites-available/voice-assistant-api
```

```nginx
# Upstream backend server
upstream voice_assistant_backend {
    server 127.0.0.1:8081;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS API Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Client body size limit
    client_max_body_size 10M;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Health check endpoint
    location /health {
        proxy_pass http://voice_assistant_backend;
        access_log off;
        proxy_set_header Host $host;
    }

    # WebSocket endpoint
    location /api/widget/ws {
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
        
        proxy_buffering off;
        proxy_cache off;
    }

    # Widget static files
    location /api/widget/widget.css {
        proxy_pass http://voice_assistant_backend;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=3600";
    }

    location /api/widget/widget.js {
        proxy_pass http://voice_assistant_backend;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=3600";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        proxy_buffering off;
    }

    # Root location
    location / {
        proxy_pass http://voice_assistant_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Enable Nginx Sites

```bash
# Enable frontend site
sudo ln -s /etc/nginx/sites-available/voice-assistant /etc/nginx/sites-enabled/

# Enable API site (if using subdomain)
sudo ln -s /etc/nginx/sites-available/voice-assistant-api /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

---

## SSL/HTTPS Setup

### 1. Obtain SSL Certificates with Let's Encrypt

```bash
# For frontend domain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# For API subdomain
sudo certbot --nginx -d api.yourdomain.com
```

### 2. Auto-Renewal Setup

Certbot automatically sets up a cron job for renewal. Verify:

```bash
sudo certbot renew --dry-run
```

### 3. Update Nginx Config After Certbot

Certbot automatically updates your Nginx configuration. Verify the SSL paths are correct in your config files.

---

## Database Setup

### Option 1: SQLite (Development/Simple Setup)

SQLite is already configured. The database file will be created at:
```
/var/www/voice-assistant/mvp/backend/chatbot.db
```

### Option 2: PostgreSQL (Production Recommended)

```bash
# Install PostgreSQL (if not already installed)
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE voiceassistant_db;
CREATE USER voiceassistant WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE voiceassistant_db TO voiceassistant;
\q

# Update DATABASE_URL in backend .env file
# DATABASE_URL=postgresql://voiceassistant:your_secure_password@localhost:5432/voiceassistant_db
```

---

## Environment Configuration

### Backend Environment Variables

Key variables to configure in `/var/www/voice-assistant/mvp/backend/.env`:

- `APP_ENV=PROD` - Production environment
- `DEBUG=False` - Disable debug mode
- `SECRET_KEY` - Strong secret key for JWT
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed origins (JSON array)
- `API_BASE_URL` - Full API URL (https://api.yourdomain.com)

### Frontend Environment Variables

Key variables in `/var/www/voice-assistant/mvp/frontend/.env.production`:

- `VITE_APP_ENV=PROD`
- `VITE_API_BASE_URL=https://api.yourdomain.com`

---

## Service Management

### 1. Create Systemd Service for Backend

```bash
sudo nano /etc/systemd/system/voice-assistant-backend.service
```

```ini
[Unit]
Description=Voice Assistant Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=voiceassistant
Group=www-data
WorkingDirectory=/var/www/voice-assistant/mvp/backend
Environment="PATH=/var/www/voice-assistant/mvp/backend/venv/bin"
EnvironmentFile=/var/www/voice-assistant/mvp/backend/.env
ExecStart=/var/www/voice-assistant/mvp/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8081 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant-backend.service
sudo systemctl start voice-assistant-backend.service
sudo systemctl status voice-assistant-backend.service
```

### 3. Service Management Commands

```bash
# Start service
sudo systemctl start voice-assistant-backend.service

# Stop service
sudo systemctl stop voice-assistant-backend.service

# Restart service
sudo systemctl restart voice-assistant-backend.service

# View logs
sudo journalctl -u voice-assistant-backend.service -f

# View status
sudo systemctl status voice-assistant-backend.service
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Install UFW if not installed
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 2. Fail2Ban Setup (Optional)

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. File Permissions

```bash
# Set proper ownership
sudo chown -R voiceassistant:www-data /var/www/voice-assistant

# Set directory permissions
sudo find /var/www/voice-assistant -type d -exec chmod 755 {} \;

# Set file permissions
sudo find /var/www/voice-assistant -type f -exec chmod 644 {} \;

# Make scripts executable
sudo find /var/www/voice-assistant -name "*.sh" -exec chmod +x {} \;

# Protect sensitive files
sudo chmod 600 /var/www/voice-assistant/mvp/backend/.env
```

### 4. Disable Directory Listing

Already configured in Nginx, but verify:

```nginx
# In Nginx config
location / {
    autoindex off;
}
```

---

## Monitoring & Logging

### 1. Backend Logs

```bash
# View real-time logs
sudo journalctl -u voice-assistant-backend.service -f

# View last 100 lines
sudo journalctl -u voice-assistant-backend.service -n 100

# View logs from today
sudo journalctl -u voice-assistant-backend.service --since today
```

### 2. Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log

# Combined logs
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

### 3. System Monitoring

```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep -E "uvicorn|nginx|node"
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check service status
sudo systemctl status voice-assistant-backend.service

# Check logs
sudo journalctl -u voice-assistant-backend.service -n 50

# Test manually
cd /var/www/voice-assistant/mvp/backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8081

# Check if port is in use
sudo netstat -tlnp | grep 8081
```

### Nginx 502 Bad Gateway

```bash
# Verify backend is running
sudo systemctl status voice-assistant-backend.service

# Check backend is listening
curl http://127.0.0.1:8081/health

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify upstream configuration
sudo nginx -t
```

### Frontend Not Loading

```bash
# Check if dist directory exists
ls -la /var/www/voice-assistant/mvp/frontend/dist

# Rebuild frontend
cd /var/www/voice-assistant/mvp/frontend
npm run build

# Check Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/voice-assistant/mvp/frontend/dist
```

### CORS Errors

1. Verify `CORS_ORIGINS` in backend `.env` includes your domain
2. Check frontend `.env.production` has correct `VITE_API_BASE_URL`
3. Verify Nginx proxy headers are set correctly

### Database Connection Issues

```bash
# For PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Test connection
psql -U voiceassistant -d voiceassistant_db -h localhost

# Check database exists
sudo -u postgres psql -l | grep voiceassistant
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## Maintenance

### 1. Update Application

```bash
# Navigate to application directory
cd /var/www/voice-assistant

# Pull latest changes
sudo -u voiceassistant git pull origin main

# Update backend dependencies
cd mvp/backend
sudo -u voiceassistant source venv/bin/activate
sudo -u voiceassistant pip install -r requirements.txt --upgrade

# Restart backend
sudo systemctl restart voice-assistant-backend.service

# Update frontend dependencies
cd ../frontend
sudo -u voiceassistant npm install

# Rebuild frontend
sudo -u voiceassistant npm run build

# Reload Nginx
sudo systemctl reload nginx
```

### 2. Backup Database

```bash
# For SQLite
sudo cp /var/www/voice-assistant/mvp/backend/chatbot.db /backup/chatbot-$(date +%Y%m%d).db

# For PostgreSQL
sudo -u postgres pg_dump voiceassistant_db > /backup/voiceassistant-$(date +%Y%m%d).sql
```

### 3. Backup Application Files

```bash
# Create backup directory
sudo mkdir -p /backup/voice-assistant

# Backup application
sudo tar -czf /backup/voice-assistant/app-$(date +%Y%m%d).tar.gz /var/www/voice-assistant

# Backup environment files
sudo cp /var/www/voice-assistant/mvp/backend/.env /backup/voice-assistant/.env.backup
```

### 4. Regular Maintenance Tasks

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean old logs
sudo journalctl --vacuum-time=30d

# Check disk space
df -h

# Monitor application
sudo systemctl status voice-assistant-backend.service
```

---

## Quick Reference

### Important Paths

- Application: `/var/www/voice-assistant`
- Backend: `/var/www/voice-assistant/mvp/backend`
- Frontend: `/var/www/voice-assistant/mvp/frontend`
- Frontend Build: `/var/www/voice-assistant/mvp/frontend/dist`
- Backend Config: `/var/www/voice-assistant/mvp/backend/.env`
- Nginx Config: `/etc/nginx/sites-available/voice-assistant`
- Service Config: `/etc/systemd/system/voice-assistant-backend.service`

### Important Commands

```bash
# Backend
sudo systemctl restart voice-assistant-backend.service
sudo journalctl -u voice-assistant-backend.service -f

# Nginx
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl restart nginx

# SSL
sudo certbot renew
sudo certbot certificates

# Frontend
cd /var/www/voice-assistant/mvp/frontend && npm run build
```

### Access URLs

- Frontend: `https://yourdomain.com`
- API: `https://api.yourdomain.com` or `https://yourdomain.com/api`
- API Docs: `https://api.yourdomain.com/docs`
- Health Check: `https://api.yourdomain.com/health`

---

## Additional Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u voice-assistant-backend.service -f`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify configuration: `sudo nginx -t`
4. Test backend: `curl http://127.0.0.1:8081/health`

---

**Last Updated:** $(date +%Y-%m-%d)
**Version:** 1.0.0

