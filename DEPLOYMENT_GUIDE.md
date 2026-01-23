# Deployment Guide - VoiceQuik Chatbot

## Server Information

- **IP Address**: 13.234.149.62
- **Login Username**: ubuntu
- **Product User**: voicequik
- **Product User Password**: V0Ic3Qu1kl94
- **PEM File**: live-saas.pem

---

## Prerequisites

### Local Machine Requirements
- SSH access to the server
- Git installed
- PEM file (`live-saas.pem`) with proper permissions

### Server Requirements
- Ubuntu 20.04/22.04 LTS
- Python 3.12+
- Node.js 18+ and npm
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

```bash
cd ../../mvp/frontend

# Install dependencies
npm install

# Create .env file
nano .env
```

**Frontend .env Configuration:**

```env
VITE_API_URL=http://13.234.149.62:8081
VITE_RAZORPAY_KEY_ID=your-razorpay-key-id
```

### 6. Build Frontend

```bash
# Build for production
npm run build
```

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

# Pull latest changes
git pull origin main  # or your branch name

# Backend updates
cd mvp/backend
source venv/bin/activate
pip install -r requirements.txt
python -m app.migrations.run_all_migrations
deactivate

# Frontend updates
cd ../frontend
npm install
npm run build

# Restart services
pm2 restart all
```

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

### Frontend Not Loading

```bash
# Check if build exists
ls -la /home/voicequik/app/chatbot/mvp/frontend/dist

# Rebuild if needed
cd /home/voicequik/app/chatbot/mvp/frontend
npm run build
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
```

---

## Support Contacts

For deployment issues or questions, contact the development team.

**Last Updated**: January 2025
