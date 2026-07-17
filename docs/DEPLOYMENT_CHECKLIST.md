# Recruiter In A Box - Deployment Checklist

**Version:** 1.0  
**Date:** 2026-07-16  
**Environment:** Production  

---

## Pre-Deployment Checklist

### 1. Code Verification ✅

- [ ] All code changes committed to main branch
- [ ] No debug code or console.log statements
- [ ] No TODO comments in production code
- [ ] No hardcoded credentials or secrets
- [ ] All environment variables documented
- [ ] Code passes linting (flake8, eslint)
- [ ] TypeScript compilation successful
- [ ] Python syntax validation passed

### 2. Security Hardening ⚠️

- [ ] **CRITICAL**: Generate new `SECRET_KEY` (min 32 characters)
- [ ] **CRITICAL**: Change default database credentials
- [ ] **CRITICAL**: Configure Stripe webhook secret
- [ ] **HIGH**: Enable HTTPS on all endpoints
- [ ] **HIGH**: Configure CORS for production domains
- [ ] **HIGH**: Add rate limiting middleware
- [ ] **MEDIUM**: Add security headers
- [ ] **MEDIUM**: Implement token rotation

### 3. Environment Configuration ⚠️

#### Backend (.env)

```bash
# ===========================================
# REQUIRED ENVIRONMENT VARIABLES
# ===========================================

# Application
APP_NAME="Recruiter In A Box"
DEBUG=false
APP_VERSION="1.0.0"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@host:5432/db"

# Security - CHANGE THESE
SECRET_KEY="your-super-secret-key-minimum-32-characters"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe - Get from Stripe Dashboard
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRICE_PROFESSIONAL="price_..."
STRIPE_PRICE_AGENCY="price_..."

# OpenAI - Get from OpenAI Platform
OPENAI_API_KEY="sk-..."

# Frontend URL (for redirects)
FRONTEND_URL="https://yourdomain.com"
CORS_ORIGINS=["https://yourdomain.com"]

# Email (Resend or other provider)
SMTP_HOST="smtp.resend.com"
SMTP_PORT=587
SMTP_USER="resend"
SMTP_PASSWORD="your-api-key"
EMAIL_FROM="noreply@yourdomain.com"

# Supabase (if using)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"
SUPABASE_SERVICE_KEY="your-service-key"

# Trial Settings
TRIAL_DAYS=14
```

#### Frontend (.env)

```bash
# ===========================================
# FRONTEND ENVIRONMENT VARIABLES
# ===========================================

VITE_API_URL="https://api.yourdomain.com"
VITE_STRIPE_PUBLISHABLE_KEY="pk_live_..."
VITE_APP_NAME="Recruiter In A Box"
```

---

## Infrastructure Setup

### 1. Cloud Provider Configuration ⚠️

#### Option A: AWS

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier recruiter-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --allocated-storage 100 \
  --master-username admin \
  --master-user-password <secure-password>

# Create S3 bucket for uploads
aws s3 mb s3://recruiter-uploads

# Create ECR repositories
aws ecr create-repository --repository-name recruiter-backend
aws ecr create-repository --repository-name recruiter-frontend

# Create ECS cluster
aws ecs create-cluster --cluster-name recruiter-prod
```

#### Option B: Railway/Render

1. Create PostgreSQL database
2. Note connection string
3. Create application services

#### Option C: Supabase

1. Create Supabase project
2. Note API URL and keys
3. Configure authentication
4. Set up storage bucket

### 2. Domain & DNS ⚠️

```bash
# Required DNS Records

# API Subdomain
api.yourdomain.com     A     <load-balancer-ip>
api.yourdomain.com     CAA   0 issue "amazon.com"

# App Subdomain  
app.yourdomain.com     CNAME your-vercel-app.vercel.app

# Redirect Domain (optional)
www.yourdomain.com     301   https://yourdomain.com
yourdomain.com         301   https://www.yourdomain.com
```

### 3. SSL/TLS Certificate ⚠️

```bash
# Using Let's Encrypt with Certbot
certbot --nginx -d api.yourdomain.com -d yourdomain.com

# Or use Cloudflare (automatic SSL)
# Enable "Full" SSL mode in Cloudflare dashboard
```

---

## Database Setup

### 1. Create Production Database ⚠️

```sql
-- Connect to PostgreSQL
psql -h hostname -U postgres -d postgres

-- Create database
CREATE DATABASE recruiter_in_a_box;

-- Create user
CREATE USER recruiter_app WITH PASSWORD 'secure-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE recruiter_in_a_box TO recruiter_app;
```

### 2. Run Migrations ⚠️

```bash
cd backend

# Install Alembic if not present
pip install alembic

# Initialize Alembic (if first time)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 3. Verify Database ⚠️

```sql
-- Check tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Expected tables:
-- users, candidates, job_positions, candidate_scores
-- email_templates, sent_emails, activity_logs
-- subscriptions, team_members, interviews
-- onboarding_progress, email_tracking, resume_summaries
```

---

## Container Deployment

### 1. Build Images ⚠️

```bash
# Build backend image
docker build -f Dockerfile.backend -t recruiter-backend:latest .

# Build frontend image
docker build -f Dockerfile.frontend -t recruiter-frontend:latest .

# Tag for registry
docker tag recruiter-backend:latest registry.yourdomain.com/recruiter-backend:v1.0.0
docker tag recruiter-frontend:latest registry.yourdomain.com/recruiter-frontend:v1.0.0

# Push to registry
docker push registry.yourdomain.com/recruiter-backend:v1.0.0
docker push registry.yourdomain.com/recruiter-frontend:v1.0.0
```

### 2. Production docker-compose.yml ⚠️

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - app-network
    restart: unless-stopped

  backend:
    image: registry.yourdomain.com/recruiter-backend:v1.0.0
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CORS_ORIGINS=["https://yourdomain.com"]
    secrets:
      - stripe_webhook_secret
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    image: registry.yourdomain.com/recruiter-frontend:v1.0.0
    environment:
      - VITE_API_URL=https://api.yourdomain.com
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

secrets:
  stripe_webhook_secret:
    file: ./secrets/stripe_webhook_secret.txt
```

### 3. Nginx Configuration ⚠️

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check (no rate limit)
        location /health {
            proxy_pass http://backend;
            proxy_http_version 1.1;
        }
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect to https
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## Monitoring Setup

### 1. Logging Configuration ⚠️

```bash
# Set up log aggregation (Datadog, ELK, etc.)
# Configure log format as JSON
# Set up log rotation (7 days)
```

### 2. Error Tracking ⚠️

```bash
# Install Sentry SDK
pip install sentry-sdk

# Add to backend code
import sentry_sdk
sentry_sdk.init(
    dsn="https://key@sentry.io/project",
    traces_sample_rate=0.1
)
```

### 3. Health Checks ⚠️

```python
# Update health endpoint to check dependencies
@app.get("/health")
async def health_check():
    checks = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {
            "database": await check_database(),
            "openai": await check_openai(),
            "stripe": await check_stripe()
        }
    }
    return checks
```

### 4. Metrics ⚠️

```bash
# Add Prometheus metrics
pip install prometheus-client

# Expose /metrics endpoint
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
```

---

## Stripe Configuration

### 1. Stripe Dashboard Setup ⚠️

1. Create Stripe account if not done
2. Enable Developer mode for testing
3. Create products and prices:
   - Professional: $99/month
   - Agency: $299/month

### 2. Configure Webhooks ⚠️

```bash
# Webhook endpoint URL
https://api.yourdomain.com/api/webhooks/stripe

# Events to listen:
# - checkout.session.completed
# - customer.subscription.updated
# - customer.subscription.deleted
# - invoice.payment_succeeded
# - invoice.payment_failed
```

### 3. Update Environment ⚠️

```bash
STRIPE_PRICE_PROFESSIONAL="price_xxx"  # From Stripe Dashboard
STRIPE_PRICE_AGENCY="price_xxx"          # From Stripe Dashboard
STRIPE_WEBHOOK_SECRET="whsec_xxx"        # From Stripe CLI or Dashboard
```

---

## Post-Deployment Verification

### 1. Smoke Tests ⚠️

```bash
# Health check
curl https://api.yourdomain.com/health

# Expected response:
# {"status":"healthy","app":"Recruiter In A Box","version":"1.0.0"}

# Test signup
curl -X POST https://api.yourdomain.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Test login
curl -X POST https://api.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### 2. Frontend Verification ⚠️

- [ ] Landing page loads at `https://yourdomain.com`
- [ ] Signup flow works
- [ ] Login flow works
- [ ] Dashboard loads after login
- [ ] No console errors
- [ ] HTTPS working (green padlock)

### 3. API Verification ⚠️

- [ ] All endpoints respond
- [ ] Authentication works
- [ ] CORS properly configured
- [ ] Rate limiting active

---

## Rollback Plan

### Quick Rollback Steps ⚠️

```bash
# 1. Stop current containers
docker-compose down

# 2. Pull previous version
docker pull registry.yourdomain.com/recruiter-backend:v0.9.0
docker pull registry.yourdomain.com/recruiter-frontend:v0.9.0

# 3. Update docker-compose to use previous version
# Edit image tags to v0.9.0

# 4. Restart
docker-compose up -d

# 5. Verify
curl https://api.yourdomain.com/health
```

---

## Maintenance

### Regular Tasks

| Task | Frequency | Owner |
|------|-----------|-------|
| Security updates | Weekly | DevOps |
| Dependency updates | Weekly | DevOps |
| Database backups | Daily | DevOps |
| Log review | Daily | Security |
| SSL certificate renewal | 90 days | DevOps |
| Performance review | Monthly | Engineering |

### Backup Schedule

```bash
# Daily database backup
0 2 * * * pg_dump -h hostname -U recruiter_app recruiter_in_a_box | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Keep 30 days of backups
0 3 * * * find /backups -mtime +30 -delete
```

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Engineering Lead | | | |
| DevOps | | | |
| Security | | | |
| Product Owner | | | |

---

*End of Deployment Checklist*
