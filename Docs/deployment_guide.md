# Deployment Guide - Service Marketplace Platform

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] Update `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG = False` in production settings
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database
- [ ] Configure Redis instance
- [ ] Set up email service (SMTP/SendGrid/AWS SES)
- [ ] Configure AWS S3 for file storage (optional)
- [ ] Set up Sentry for error tracking (optional)
- [ ] Review and update all environment variables

### Environment Variables (Production)

Create `.env` file with:

```bash
# Django
SECRET_KEY=your-super-secret-key-min-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=marketplace_prod
DB_USER=marketplace_user
DB_PASSWORD=strong-db-password
DB_HOST=your-db-host.rds.amazonaws.com
DB_PORT=5432

# Redis
REDIS_HOST=your-redis-host.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# AWS S3 (Optional)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=marketplace-media
AWS_S3_REGION_NAME=us-east-1

# Sentry (Optional)
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Admin
ADMIN_EMAIL=admin@yourdomain.com
```

---

## 📦 Deployment Methods

### Method 1: Docker Deployment (Recommended)

#### 1. Build and Deploy

```bash
# Clone repository
git clone <repository-url>
cd marketplace

# Create .env file
cp .env.example .env
# Edit .env with production values

# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

#### 2. Verify Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f web

# Test API
curl http://localhost/api/services/categories/
```

---

### Method 2: VPS/Dedicated Server Deployment

#### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx redis-server -y

# Install supervisor for process management
sudo apt install supervisor -y
```

#### 2. PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE marketplace_prod;
CREATE USER marketplace_user WITH PASSWORD 'strong-password';
ALTER ROLE marketplace_user SET client_encoding TO 'utf8';
ALTER ROLE marketplace_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE marketplace_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE marketplace_prod TO marketplace_user;
\q
```

#### 3. Application Setup

```bash
# Create app user
sudo useradd -m -s /bin/bash marketplace
sudo su - marketplace

# Clone repository
git clone <repository-url> /home/marketplace/app
cd /home/marketplace/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit with production values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

#### 4. Gunicorn Setup

Create `/etc/supervisor/conf.d/marketplace.conf`:

```ini
[program:marketplace]
command=/home/marketplace/app/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
directory=/home/marketplace/app
user=marketplace
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/marketplace/app/logs/gunicorn.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"
```

#### 5. Celery Worker Setup

Create `/etc/supervisor/conf.d/celery_worker.conf`:

```ini
[program:celery_worker]
command=/home/marketplace/app/venv/bin/celery -A config worker -l info --concurrency=4
directory=/home/marketplace/app
user=marketplace
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/marketplace/app/logs/celery_worker.log
```

#### 6. Celery Beat Setup

Create `/etc/supervisor/conf.d/celery_beat.conf`:

```ini
[program:celery_beat]
command=/home/marketplace/app/venv/bin/celery -A config beat -l info
directory=/home/marketplace/app
user=marketplace
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/marketplace/app/logs/celery_beat.log
```

#### 7. Reload Supervisor

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

#### 8. Nginx Configuration

Create `/etc/nginx/sites-available/marketplace`:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /home/marketplace/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/marketplace/app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/marketplace /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### Method 3: AWS Deployment

#### Using AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB:
```bash
eb init -p python-3.11 marketplace
```

3. Create environment:
```bash
eb create marketplace-prod --database.engine postgres
```

4. Deploy:
```bash
eb deploy
```

#### Using AWS ECS/Fargate

1. Build and push Docker image to ECR
2. Create ECS cluster
3. Define task definitions
4. Create services for web, celery worker, and beat
5. Configure Application Load Balancer
6. Set up RDS PostgreSQL and ElastiCache Redis
7. Configure auto-scaling policies

---

## 🔧 Post-Deployment Tasks

### 1. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_users_email_active ON users(email, is_active);
CREATE INDEX CONCURRENTLY idx_bookings_status_date ON bookings(status, scheduled_date);
CREATE INDEX CONCURRENTLY idx_services_active_featured ON services(is_active, is_featured);

-- Analyze tables
ANALYZE users;
ANALYZE services;
ANALYZE bookings;
ANALYZE reviews;
```

### 2. Set Up Monitoring

**Sentry Integration:**
```python
# Already configured in production.py
# Just set SENTRY_DSN in .env
```

**Application Performance Monitoring:**
- Set up New Relic or Datadog
- Monitor database query performance
- Track API response times
- Monitor Celery task execution

### 3. Set Up Backups

**Database Backups:**
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U marketplace_user marketplace_prod > $BACKUP_DIR/backup_$TIMESTAMP.sql
# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Media Files Backup:**
```bash
# Backup to S3
aws s3 sync /home/marketplace/app/media/ s3://your-backup-bucket/media/
```

### 4. Configure Cron Jobs

```bash
# Add to crontab
crontab -e

# Database backup daily at 2 AM
0 2 * * * /home/marketplace/scripts/backup_db.sh

# Clean old logs weekly
0 0 * * 0 find /home/marketplace/app/logs -type f -mtime +30 -delete

# Update statistics daily at 3 AM
0 3 * * * cd /home/marketplace/app && /home/marketplace/app/venv/bin/python manage.py update_stats
```

### 5. Security Hardening

```bash
# Firewall rules
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Disable root SSH login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## 📊 Performance Tuning

### 1. PostgreSQL Tuning

Edit `/etc/postgresql/15/main/postgresql.conf`:

```conf
# Memory settings (for 8GB RAM server)
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 64MB

# Connection settings
max_connections = 200

# Query tuning
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200

# Write ahead log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 2. Gunicorn Tuning

For 4 CPU cores:
```bash
# Workers = (2 × CPU cores) + 1
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 9 \
  --worker-class gevent \
  --worker-connections 1000 \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### 3. Nginx Tuning

Edit `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    # Buffer settings
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;

    # Cache
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
}
```

### 4. Redis Tuning

Edit `/etc/redis/redis.conf`:

```conf
# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (disable for cache-only)
save ""
appendonly no

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 60
```

### 5. Celery Optimization

```python
# config/celery.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
```

---

## 🚨 Monitoring & Alerts

### 1. Health Check Endpoint

Create `apps/core/views.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

### 2. Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- StatusCake

Monitor:
- `/api/health/` endpoint
- Response times
- SSL certificate expiration

### 3. Log Aggregation

**Using ELK Stack or CloudWatch:**
- Centralize logs from all services
- Set up alerts for errors
- Monitor slow queries
- Track API usage patterns

---

## 🔄 Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /home/marketplace/app
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate
          python manage.py collectstatic --noinput
          sudo supervisorctl restart marketplace
          sudo supervisorctl restart celery_worker
          sudo supervisorctl restart celery_beat
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

1. **Application Servers:**
   - Deploy multiple web instances behind load balancer
   - Use session storage in Redis (already configured)
   - Ensure stateless application design

2. **Database:**
   - Set up read replicas for read-heavy operations
   - Use connection pooling (PgBouncer)
   - Partition large tables

3. **Celery Workers:**
   - Scale workers independently based on queue size
   - Use separate queues for different task priorities

4. **Cache Layer:**
   - Use Redis Cluster for high availability
   - Implement cache warming strategies
   - Monitor cache hit rates

### Load Balancer Configuration (AWS ALB)

```yaml
Target Groups:
  - Web Servers: Port 8000
  - Health Check: /api/health/
  - Deregistration Delay: 30s

Load Balancer:
  - Algorithm: Round Robin
  - Sticky Sessions: Enabled (cookie-based)
  - Connection Draining: 30s
```

---

## 🛡️ Disaster Recovery

### Backup Strategy

1. **Database:** Daily automated backups with 30-day retention
2. **Media Files:** Sync to S3 with versioning enabled
3. **Code:** Version controlled in Git
4. **Configuration:** Store in secure vault (AWS Secrets Manager)

### Recovery Procedures

**Database Restore:**
```bash
# Stop application
sudo supervisorctl stop marketplace

# Restore database
psql -U marketplace_user marketplace_prod < backup_20251028.sql

# Restart application
sudo supervisorctl start marketplace
```

**Complete System Restore:**
1. Provision new server
2. Deploy application from Git
3. Restore database from backup
4. Sync media files from S3
5. Update DNS records

---

## 📞 Troubleshooting

### Common Issues

**Issue: High Database CPU**
```bash
# Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

# Solution: Add missing indexes, optimize queries
```

**Issue: Celery tasks backing up**
```bash
# Check queue size
celery -A config inspect active_queues

# Scale workers
sudo supervisorctl start celery_worker:*
```

**Issue: Memory leak**
```bash
# Monitor memory
free -h
htop

# Check Gunicorn workers
ps aux | grep gunicorn

# Restart workers
sudo supervisorctl restart marketplace
```

**Issue: 502 Bad Gateway**
```bash
# Check Gunicorn status
sudo supervisorctl status marketplace

# Check logs
tail -f /home/marketplace/app/logs/gunicorn.log

# Check Nginx error log
tail -f /var/log/nginx/error.log
```

---

## ✅ Final Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] Backup strategy implemented
- [ ] Monitoring and alerts set up
- [ ] Security hardening completed
- [ ] Performance tuning applied
- [ ] Health checks configured
- [ ] Documentation updated
- [ ] Team trained on deployment procedures
- [ ] Rollback plan prepared

---

## 🎯 Success Metrics

After deployment, monitor:

- **Uptime:** Target 99.9% availability
- **Response Time:** < 200ms for 95th percentile
- **Error Rate:** < 0.1% of requests
- **Database Queries:** < 50ms average
- **Celery Tasks:** < 5 minute average completion
- **Cache Hit Rate:** > 80%

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Optimization](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html)

---

For questions or issues, contact: support@marketplace.com