#!/bin/bash
BACKUP_DIR="/home/voicequik/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump chatbot > $BACKUP_DIR/chatbot_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/chatbot_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "chatbot_*.sql.gz" -mtime +7 -delete

echo "Backup completed: chatbot_$DATE.sql.gz"
