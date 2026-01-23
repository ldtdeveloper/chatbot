# Deployment Guide - VoiceQuik Chatbot

## Server Information

- **IP Address**: 13.234.149.62
- **Login Username**: ubuntu
- **Product User**: voicequik
- **Product User Password**: V0Ic3Qu1kl94
- **PEM File**: live-saas.pem

---

## Deployment Strategy

### Frontend Deployment
- **Pre-built Approach**: The frontend build files (`dist/`) are included in the repository
- **Deployment**: Simply pull the latest code from the repository - no build needed on server
- **Benefits**: Faster deployments, no Node.js build dependencies on production server
- **When to Rebuild**: Only rebuild if you need to change environment variables (API URL, etc.)

### Backend Deployment
- **Source Code**: Backend code is deployed and run directly on the server
- **Dependencies**: Installed via pip in virtual environment
- **Process Management**: Managed by PM2

---

## Prerequisites

### Local Machine Requirements
- SSH access to the server
- Git installed
- PEM file (`live-saas.pem`) with proper permissions

### Server Requirements
- Ubuntu 20.04/22.04 LTS
- Python 3.12+
- Node.js 18+ and npm (optional - only needed if rebuilding frontend on server)
- PostgreSQL 14+
- Redis
- Nginx
- PM2 (for process management)
- Certbot (for SSL certificates)

---

## Initial Server Setup

### 1. Connect to Server

```bash
# Set proper permissions for PEM file
chmod 400 live-saas.pem

# Connect to server
ssh -i live-saas.pem ubuntu@13.234.149.62
```

### 2. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Required Software

```bash
# Install Python and pip
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y

# Install PM2 globally
sudo npm install -g pm2

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 4. Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE chatbot;
CREATE USER voicequik WITH PASSWORD 'V0Ic3Qu1kl94';
ALTER ROLE voicequik SET client_encoding TO 'utf8';
ALTER ROLE voicequik SET default_transaction_isolation TO 'read committed';
ALTER ROLE voicequik SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE chatbot TO voicequik;
\q
```

### 5. Configure Redis

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Set bind to localhost only (for security)
bind 127.0.0.1

# Save and restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

---

## Application Deployment

### 1. Create Application Directory

```bash
# Create directory for application
sudo mkdir -p /home/voicequik/app
sudo chown -R voicequik:voicequik /home/voicequik/app

# Switch to voicequik user
sudo su - voicequik
cd /home/voicequik/app
```

### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/ldtdeveloper/chatbot.git
cd chatbot
```

### 3. Backend Setup

```bash
cd mvp/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
nano .env
```

**Backend .env Configuration:**

```env
# Database
DATABASE_URL=postgresql://voicequik:V0Ic3Qu1kl94@localhost:5432/chatbot

# Security
SECRET_KEY=your-secret-key-here-generate-a-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Razorpay (if using)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://13.234.149.62,https://yourdomain.com

# Environment
ENVIRONMENT=production
```

### 4. Run Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run all migrations
python -m app.migrations.run_all_migrations

# Seed database (optional - creates superadmin)
python -m app.scripts.seed_db
```

### 5. Frontend Setup

**Option 1: Deploy Pre-built Frontend (Recommended)**

Since the build files are already in the repository (`mvp/frontend/dist/`), you can deploy them directly without building on the server:

```bash
# The dist folder is already in the repository
# No need to build on the server - just verify it exists
cd ../../mvp/frontend
ls -la dist/

# If dist folder exists, you're ready to deploy
# The Nginx configuration will serve files from this directory
```

**Option 2: Build Frontend on Server (If needed)**

If you need to rebuild on the server or the dist folder is missing:

```bash
cd ../../mvp/frontend

# Install dependencies
npm install

# Create .env file (if building on server)
nano .env
```

**Frontend .env Configuration (if building on server):**

```env
VITE_API_URL=http://13.234.149.62:8081
# Or use your domain:
# VITE_API_URL=https://yourdomain.com/api
VITE_RAZORPAY_KEY_ID=your-razorpay-key-id
```

```bash
# Build for production
npm run build

# Verify build was created
ls -la dist/
```

**Note:** The pre-built frontend in the repository uses the API URL from when it was built. If you need to change the API URL, you'll need to rebuild with the new `.env` file.

---

## Process Management with PM2

### 1. Create PM2 Configuration Files

**Backend PM2 Config** (`/home/voicequik/app/chatbot/ecosystem.config.js`):

The `ecosystem.config.js` file is already included in the repository. Copy it to the server or use it directly:

```bash
# The file is already in the repository root
# Just ensure it's in the correct location on the server
cp ecosystem.config.js /home/voicequik/app/chatbot/
```

The configuration uses `uvicorn` to run the FastAPI backend and `celery` for background tasks.

### 2. Create Logs Directory

```bash
mkdir -p /home/voicequik/app/logs
```

### 3. Start Applications with PM2

```bash
cd /home/voicequik/app/chatbot

# Start backend and celery
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup
# Follow the instructions shown in the output
```

### 4. PM2 Useful Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs chatbot-backend
pm2 logs chatbot-celery

# Restart services
pm2 restart chatbot-backend
pm2 restart chatbot-celery

# Stop services
pm2 stop chatbot-backend
pm2 stop chatbot-celery

# Monitor
pm2 monit
```

---

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/chatbot
```

**Nginx Configuration:**

```nginx
# Backend API
upstream backend {
    server 127.0.0.1:8081;
}

# Frontend
server {
    listen 80;
    server_name 13.234.149.62 yourdomain.com;

    # Frontend
    location / {
        root /home/voicequik/app/chatbot/mvp/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Widget WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Widget static files
    location /widget {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Enable Site and Test Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## SSL Certificate Setup (Optional but Recommended)

### 1. Obtain SSL Certificate

```bash
# Replace yourdomain.com with your actual domain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts to complete the setup
```

### 2. Auto-renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up renewal, but verify
sudo systemctl status certbot.timer
```

---

## Deployment Workflow

### 1. Update Application

```bash
# Switch to voicequik user
sudo su - voicequik
cd /home/voicequik/app/chatbot

# Pull latest changes (includes pre-built frontend)
git pull origin dev  # or your branch name (main/master)

# Backend updates
cd mvp/backend
source venv/bin/activate
pip install -r requirements.txt
python -m app.migrations.run_all_migrations
deactivate

# Frontend updates (if using pre-built files from repository)
# The dist folder is already in the repository, so no build needed
# Just verify the dist folder exists
cd ../frontend
if [ -d "dist" ]; then
    echo "✅ Frontend build found in repository"
    ls -la dist/
else
    echo "⚠️  Frontend build not found. Building on server..."
    npm install
    npm run build
fi

# Restart services
pm2 restart all

# Reload Nginx to serve updated frontend
sudo systemctl reload nginx
```

**Note:** The frontend build files are included in the repository, so you typically don't need to build on the server. Just pull the latest changes and restart services. If you need to change the API URL or other environment variables, rebuild the frontend locally and push the new `dist/` folder to the repository.

### 2. Database Backup

```bash
# Create backup script
sudo nano /home/voicequik/backup_db.sh
```

**Backup Script:**

```bash
#!/bin/bash
BACKUP_DIR="/home/voicequik/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump chatbot > $BACKUP_DIR/chatbot_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "chatbot_*.sql" -mtime +7 -delete

echo "Backup completed: chatbot_$DATE.sql"
```

```bash
# Make executable
chmod +x /home/voicequik/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/voicequik/backup_db.sh
```

---

## Monitoring and Maintenance

### 1. Check Service Status

```bash
# PM2 status
pm2 status

# System services
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### 2. View Logs

```bash
# Application logs
pm2 logs

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

### 3. Database Maintenance

```bash
# Connect to database
sudo -u postgres psql chatbot

# Check database size
SELECT pg_size_pretty(pg_database_size('chatbot'));

# List all tables
\dt

# Exit
\q
```

---

## Testing Deployment

After deployment, verify that both backend and frontend are working correctly.

### 1. Test Backend Deployment

#### Check PM2 Status
```bash
# Check if backend and celery are running
pm2 status

# Should show:
# chatbot-backend    | online | running
# chatbot-celery     | online | running
```

#### Test Backend API Endpoints

**From Server (Local Test):**
```bash
# Test health/root endpoint
curl http://localhost:8081/

# Test API health endpoint (if available)
curl http://localhost:8081/api/health

# Test login endpoint (should return 422 for missing credentials, which is expected)
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

**From Local Machine (External Test):**
```bash
# Replace with your server IP or domain
curl http://13.234.149.62:8081/

# Test API endpoint through Nginx
curl http://13.234.149.62/api/

# Test with domain (if configured)
curl https://yourdomain.com/api/
```

#### Check Backend Logs
```bash
# View real-time backend logs
pm2 logs chatbot-backend

# Check for any errors
pm2 logs chatbot-backend --err

# Check last 100 lines
pm2 logs chatbot-backend --lines 100
```

#### Verify Database Connection
```bash
# Connect to database and check if tables exist
sudo -u postgres psql chatbot -c "\dt"

# Should show tables like: users, agents, interactions, etc.
```

#### Test Celery Worker
```bash
# Check Celery logs
pm2 logs chatbot-celery

# Should see: "celery@hostname ready" message
```

### 2. Test Frontend Deployment

#### Check Frontend Files
```bash
# Verify dist folder exists and has files
ls -la /home/voicequik/app/chatbot/mvp/frontend/dist/

# Should see: index.html, assets/ folder, etc.
```

#### Test Frontend via Browser

**Access Frontend:**
1. Open your browser
2. Navigate to: `http://13.234.149.62` or `https://yourdomain.com`
3. You should see the login page or application interface

**Check Browser Console:**
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Check for any JavaScript errors
4. Check Network tab for API calls

#### Test Frontend API Connection
```bash
# Test if frontend can reach backend API
curl -I http://13.234.149.62/api/

# Should return HTTP 200 or 404 (not 502 or 503)
```

#### Verify Nginx is Serving Frontend
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### 3. Integration Testing

#### Test Complete Flow

1. **Login Test:**
   - Open frontend in browser
   - Try to login with valid credentials
   - Should redirect to dashboard on success

2. **API Communication Test:**
   - Open browser Developer Tools → Network tab
   - Perform any action (login, fetch data, etc.)
   - Check if API calls are successful (status 200)
   - Verify API URL is correct (should point to `/api/`)

3. **WebSocket Test (if using widget):**
   - Open widget on a page
   - Check browser console for WebSocket connection
   - Should see "Connected" or similar message

### 4. Quick Health Check Script

Create a simple health check script:

```bash
# Create health check script
nano /home/voicequik/app/chatbot/health_check.sh
```

**Health Check Script:**

```bash
#!/bin/bash

echo "=== Deployment Health Check ==="
echo ""

# Check PM2 services
echo "1. Checking PM2 Services..."
pm2 status | grep -E "chatbot-backend|chatbot-celery"
if [ $? -eq 0 ]; then
    echo "✅ PM2 services are running"
else
    echo "❌ PM2 services are not running"
fi
echo ""

# Check Backend API
echo "2. Checking Backend API..."
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/)
if [ "$BACKEND_RESPONSE" = "200" ] || [ "$BACKEND_RESPONSE" = "404" ]; then
    echo "✅ Backend API is responding (HTTP $BACKEND_RESPONSE)"
else
    echo "❌ Backend API is not responding (HTTP $BACKEND_RESPONSE)"
fi
echo ""

# Check Frontend Files
echo "3. Checking Frontend Files..."
if [ -d "/home/voicequik/app/chatbot/mvp/frontend/dist" ] && [ -f "/home/voicequik/app/chatbot/mvp/frontend/dist/index.html" ]; then
    echo "✅ Frontend build files exist"
else
    echo "❌ Frontend build files not found"
fi
echo ""

# Check Nginx
echo "4. Checking Nginx..."
NGINX_STATUS=$(sudo systemctl is-active nginx)
if [ "$NGINX_STATUS" = "active" ]; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx is not running"
fi
echo ""

# Check Database
echo "5. Checking Database..."
DB_CHECK=$(sudo -u postgres psql -t -c "SELECT 1" chatbot 2>/dev/null)
if [ "$DB_CHECK" = "1" ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi
echo ""

# Check Redis
echo "6. Checking Redis..."
REDIS_CHECK=$(redis-cli ping 2>/dev/null)
if [ "$REDIS_CHECK" = "PONG" ]; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running"
fi
echo ""

echo "=== Health Check Complete ==="
```

```bash
# Make executable
chmod +x /home/voicequik/app/chatbot/health_check.sh

# Run health check
/home/voicequik/app/chatbot/health_check.sh
```

### 5. Expected Results

**✅ Successful Deployment Indicators:**

- PM2 shows both `chatbot-backend` and `chatbot-celery` as `online`
- Backend API responds with HTTP 200 or 404 (not 502/503)
- Frontend loads in browser without errors
- Browser console shows no critical errors
- API calls from frontend return successful responses
- Database connection works
- Redis connection works
- Nginx serves frontend files correctly

**❌ Common Issues:**

- **502 Bad Gateway**: Backend not running or Nginx can't reach it
- **503 Service Unavailable**: Backend crashed or not started
- **Blank page**: Frontend files not found or Nginx misconfigured
- **CORS errors**: Backend CORS configuration issue
- **API 404**: Nginx routing misconfigured

---

## Troubleshooting

### Backend Not Starting

```bash
# Check PM2 logs
pm2 logs chatbot-backend

# Check if port is in use
sudo lsof -i :8081

# Check environment variables
cd /home/voicequik/app/chatbot/mvp/backend
source venv/bin/activate
python -c "from app.core.config import settings; print(settings.database_url)"
```

### Frontend Not Loading / 500 Internal Server Error

**Common Causes:**
1. File permissions issue (Nginx can't read files)
2. Frontend dist folder missing or empty
3. Nginx configuration error
4. Wrong file paths in Nginx config

**Step-by-Step Fix:**

```bash
# 1. Check if dist folder exists
ls -la /home/voicequik/app/chatbot/mvp/frontend/dist

# 2. If dist folder doesn't exist, pull from repository
cd /home/voicequik/app/chatbot
git pull origin dev  # or your branch name

# 3. Verify dist folder exists and has files
ls -la mvp/frontend/dist/
# Should see: index.html, assets/ folder, etc.

# 4. Fix file permissions (CRITICAL - Nginx needs read access)
# Option A: Add Nginx user to voicequik group (Recommended)
sudo usermod -a -G voicequik www-data
sudo chmod -R 755 /home/voicequik/app/chatbot/mvp/frontend/dist
sudo chown -R voicequik:voicequik /home/voicequik/app/chatbot/mvp/frontend/dist

# Option B: Make files readable by all (Alternative)
sudo chmod -R 755 /home/voicequik/app/chatbot/mvp/frontend/dist
sudo chmod -R 644 /home/voicequik/app/chatbot/mvp/frontend/dist/*

# 5. Verify Nginx can access the directory
sudo -u www-data ls /home/voicequik/app/chatbot/mvp/frontend/dist/
# If this fails, there's a permission issue

# 6. Check Nginx error logs for specific error
sudo tail -20 /var/log/nginx/error.log

# 7. Test Nginx configuration
sudo nginx -t

# 8. If config is OK, reload Nginx
sudo systemctl reload nginx

# 9. If still not working, check Nginx config path
sudo cat /etc/nginx/sites-available/chatbot | grep "root"
# Should show: root /home/voicequik/app/chatbot/mvp/frontend/dist;

# 10. If dist folder is missing, rebuild on server
cd /home/voicequik/app/chatbot/mvp/frontend
npm install
npm run build
```

**Quick Permission Fix (Run these commands):**
```bash
# Fix permissions for frontend files
sudo chmod -R 755 /home/voicequik/app/chatbot/mvp/frontend
sudo chmod -R 644 /home/voicequik/app/chatbot/mvp/frontend/dist/*
sudo chmod 755 /home/voicequik/app/chatbot/mvp/frontend/dist

# Add www-data to voicequik group
sudo usermod -a -G voicequik www-data

# Reload Nginx
sudo systemctl reload nginx
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
sudo -u postgres psql -c "SELECT version();"

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep chatbot
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Check Redis status
sudo systemctl status redis-server
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Reload Nginx
sudo systemctl reload nginx
```

---

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Set strong SECRET_KEY in .env
- [ ] Configure firewall (UFW)
- [ ] Enable SSL/HTTPS
- [ ] Set up regular database backups
- [ ] Configure proper file permissions
- [ ] Disable root SSH login
- [ ] Set up fail2ban for SSH protection
- [ ] Keep system packages updated
- [ ] Monitor application logs regularly

---

## Quick Reference Commands

```bash
# Connect to server
ssh -i live-saas.pem ubuntu@13.234.149.62

# Switch to application user
sudo su - voicequik

# Navigate to app
cd /home/voicequik/app/chatbot

# Deploy frontend (pre-built from repository)
git pull origin dev  # Pull latest code including dist folder
sudo systemctl reload nginx  # Reload Nginx to serve updated frontend

# PM2 commands
pm2 status
pm2 logs
pm2 restart all

# Restart services
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# View logs
pm2 logs chatbot-backend
sudo tail -f /var/log/nginx/error.log

# Verify frontend build exists
ls -la /home/voicequik/app/chatbot/mvp/frontend/dist
```

---

## Support Contacts

For deployment issues or questions, contact the development team.

**Last Updated**: January 2025
