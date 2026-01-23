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
