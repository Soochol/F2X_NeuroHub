# Deployment Guide

## Overview

This guide covers deploying the F2X NeuroHub FastAPI backend to production environments.

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Nginx (recommended)
- Supervisor or systemd (for process management)
- SSL certificate (for HTTPS)

## Environment Setup

### 1. Production Environment Variables

Create `.env.production`:

```bash
# Application
APP_NAME="F2X NeuroHub MES"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/f2x_neurohub_mes

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://app.f2x-neurohub.com,https://admin.f2x-neurohub.com

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### 2. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Deployment Options

### Option 1: Docker (Recommended)

#### Docker Setup

1. **Create Dockerfile** (already exists):
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build image**:
   ```bash
   docker build -t f2x-neurohub-backend:latest .
   ```

3. **Run container**:
   ```bash
   docker run -d \
     --name f2x-backend \
     -p 8000:8000 \
     --env-file .env.production \
     f2x-neurohub-backend:latest
   ```

#### Docker Compose

Use the existing `docker-compose.yml`:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Option 2: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip postgresql-client nginx -y

# Create application user
sudo useradd -m -s /bin/bash f2x
sudo su - f2x
```

#### 2. Application Setup

```bash
# Clone repository
git clone <repository-url> /home/f2x/backend
cd /home/f2x/backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env.production
nano .env.production  # Edit with production values
```

#### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE f2x_neurohub_mes;
CREATE USER f2x_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE f2x_neurohub_mes TO f2x_user;
\q

# Run migrations
cd /path/to/database
psql -U f2x_user -d f2x_neurohub_mes -f deploy.sql
```

#### 4. Process Management with Systemd

Create `/etc/systemd/system/f2x-backend.service`:

```ini
[Unit]
Description=F2X NeuroHub FastAPI Backend
After=network.target postgresql.service

[Service]
Type=notify
User=f2x
Group=f2x
WorkingDirectory=/home/f2x/backend
Environment="PATH=/home/f2x/backend/venv/bin"
EnvironmentFile=/home/f2x/backend/.env.production
ExecStart=/home/f2x/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable f2x-backend
sudo systemctl start f2x-backend
sudo systemctl status f2x-backend
```

#### 5. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/f2x-backend`:

```nginx
upstream f2x_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.f2x-neurohub.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.f2x-neurohub.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/f2x-neurohub.crt;
    ssl_certificate_key /etc/ssl/private/f2x-neurohub.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/f2x-backend-access.log;
    error_log /var/log/nginx/f2x-backend-error.log;

    # Max upload size
    client_max_body_size 10M;

    # Proxy settings
    location / {
        proxy_pass http://f2x_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static {
        alias /home/f2x/backend/static;
        expires 30d;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/f2x-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Gunicorn with Uvicorn Workers

More robust for production:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Uvicorn workers
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --access-logfile /var/log/f2x/access.log \
    --error-logfile /var/log/f2x/error.log
```

## Performance Tuning

### 1. Worker Configuration

Calculate optimal workers:
```
workers = (2 x $num_cores) + 1
```

For 4 CPU cores: `--workers 9`

### 2. Database Connection Pooling

In `app/database.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Max connections
    max_overflow=10,        # Additional connections
    pool_pre_ping=True,     # Check connection validity
    pool_recycle=3600,      # Recycle connections every hour
)
```

### 3. Caching

Consider adding Redis for caching:

```bash
pip install redis fastapi-cache2
```

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

## Monitoring

### 1. Application Logs

```bash
# Systemd logs
sudo journalctl -u f2x-backend -f

# Application logs
tail -f /var/log/f2x/*.log
```

### 2. Health Check Endpoint

Already available at `/health`:

```bash
curl https://api.f2x-neurohub.com/health
```

### 3. Prometheus Metrics (Optional)

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

## Backup Strategy

### 1. Database Backups

Automated PostgreSQL backup:

```bash
#!/bin/bash
# /home/f2x/scripts/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/f2x/backups"
DB_NAME="f2x_neurohub_mes"

pg_dump -U f2x_user $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /home/f2x/scripts/backup-db.sh
```

### 2. Application Backups

```bash
# Backup application files
tar -czf /home/f2x/backups/app_$(date +%Y%m%d).tar.gz /home/f2x/backend
```

## Security Checklist

- [ ] Use HTTPS with valid SSL certificate
- [ ] Set strong SECRET_KEY
- [ ] Disable DEBUG mode
- [ ] Use environment variables for secrets
- [ ] Enable CORS with specific origins
- [ ] Set up firewall (UFW)
- [ ] Configure PostgreSQL to accept only local connections
- [ ] Use strong database passwords
- [ ] Regularly update dependencies
- [ ] Set up fail2ban for SSH
- [ ] Enable automatic security updates
- [ ] Implement rate limiting (optional)

## Rollback Procedure

### 1. Application Rollback

```bash
# Stop service
sudo systemctl stop f2x-backend

# Checkout previous version
cd /home/f2x/backend
git checkout <previous-commit-hash>

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start f2x-backend
```

### 2. Database Rollback

```bash
# Restore from backup
gunzip < /home/f2x/backups/backup_YYYYMMDD.sql.gz | psql -U f2x_user f2x_neurohub_mes
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u f2x-backend -n 50

# Check port
sudo netstat -tulpn | grep 8000

# Test manually
cd /home/f2x/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Connection Issues

```bash
# Test connection
psql -U f2x_user -h localhost -d f2x_neurohub_mes

# Check PostgreSQL status
sudo systemctl status postgresql
```

### High Memory Usage

```bash
# Check processes
top
htop

# Reduce workers
# Edit systemd service file and reduce --workers value
```

## Updates and Maintenance

### Application Updates

```bash
# Pull latest code
git pull origin main

# Install new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart f2x-backend

# Check status
sudo systemctl status f2x-backend
```

### Database Migrations

```bash
# Run new migrations
alembic upgrade head

# Or use deploy.sql for schema changes
psql -U f2x_user -d f2x_neurohub_mes -f database/deploy.sql
```

## Production Checklist

- [ ] Production environment variables configured
- [ ] Database deployed and verified
- [ ] SSL certificate installed
- [ ] Nginx reverse proxy configured
- [ ] Systemd service enabled
- [ ] Logs directory created with proper permissions
- [ ] Backup script configured and tested
- [ ] Monitoring set up
- [ ] Health check endpoint accessible
- [ ] Documentation updated
- [ ] Team notified of deployment

---

**Last Updated**: 2025-11-18
