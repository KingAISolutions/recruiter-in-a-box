# Recruiter In A Box - Production Deployment Guide

**Version:** 1.0  
**Date:** 2026-07-16  

---

## Prerequisites

Before deployment, ensure you have accounts for:
- [Vercel](https://vercel.com) - Frontend hosting
- [Railway](https://railway.app) - Backend hosting
- [Supabase](https://supabase.com) - Database & Storage
- [Stripe](https://stripe.com) - Payments
- [OpenAI](https://platform.openai.com) - AI features

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project credentials:
   - Project URL: `https://xxxxx.supabase.co`
   - `anon` public key
   - `service_role` secret key
   - Database password

### 1.2 Enable Auth

1. Navigate to **Authentication** → **Settings**
2. Configure:
   - Site URL: `https://yourdomain.com`
   - Redirect URLs: Add your domains
   - Enable Email auth

### 1.3 Create Storage Bucket

1. Navigate to **Storage** → **New bucket**
2. Create bucket: `resumes`
3. Set as public bucket
4. Add policies for authenticated access

### 1.4 Get Connection String

1. Navigate to **Settings** → **Database**
2. Under **Connection string**, select **URI**
3. Copy the connection string

---

## Step 2: Railway Backend Deployment

### 2.1 Prepare Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### 2.2 Create Railway Project

```bash
# Create new project
railway init

# Link to existing project (if already created)
railway link <project-id>
```

### 2.3 Add Database

```bash
# Add Supabase as a database variable
railway variables set DATABASE_URL="postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require"
```

### 2.4 Deploy Backend

```bash
# Deploy from backend directory
cd backend

# Set environment variables
railway variables set SECRET_KEY="your-super-secret-key-at-least-32-characters"
railway variables set DEBUG="false"
railway variables set FRONTEND_URL="https://your-frontend.vercel.app"
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'

# Optional: Set API keys
railway variables set OPENAI_API_KEY="sk-..."
railway variables set STRIPE_SECRET_KEY="sk_live_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."

# Deploy
railway up
```

### 2.5 Configure Startup Command

In Railway dashboard:
1. Go to **Settings** → **Start Command**
2. Set: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.6 Get Backend URL

After deployment, note your backend URL:
```
https://backend-xxxxx.up.railway.app
```

---

## Step 3: Vercel Frontend Deployment

### 3.1 Prepare for Vercel

Create `vercel.json` in the frontend directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend.up.railway.app/api/:path*"
    }
  ]
}
```

### 3.2 Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to preview
cd frontend
vercel

# Deploy to production
vercel --prod
```

### 3.3 Configure Environment Variables

In Vercel dashboard or CLI:

```bash
vercel env add VITE_API_URL
# Enter: https://your-backend.up.railway.app/api

vercel env add VITE_APP_NAME
# Enter: Recruiter In A Box

# For production with Stripe:
vercel env add VITE_STRIPE_PUBLISHABLE_KEY
# Enter: pk_live_...
```

### 3.4 Get Frontend URL

After deployment, note your frontend URL:
```
https://your-app.vercel.app
```

---

## Step 4: Backend Environment Configuration

### 4.1 Update Railway Variables

Ensure all required variables are set:

```bash
# Core Application
railway variables set APP_NAME="Recruiter In A Box"
railway variables set APP_VERSION="1.0.0"
railway variables set DEBUG="false"

# Database
railway variables set DATABASE_URL="postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres?sslmode=require"
railway variables set DATABASE_SSL_MODE="require"

# Security - CRITICAL
railway variables set SECRET_KEY="your-unique-secret-key-at-least-32-characters"

# JWT
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="15"
railway variables set REFRESH_TOKEN_EXPIRE_DAYS="7"

# URLs
railway variables set FRONTEND_URL="https://your-app.vercel.app"
railway variables set CORS_ORIGINS='["https://your-app.vercel.app"]'

# Stripe (Production)
railway variables set STRIPE_SECRET_KEY="sk_live_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PRICE_PROFESSIONAL="price_..."
railway variables set STRIPE_PRICE_AGENCY="price_..."

# OpenAI
railway variables set OPENAI_API_KEY="sk-..."

# Email (Resend recommended)
railway variables set SMTP_HOST="smtp.resend.com"
railway variables set SMTP_PORT="587"
railway variables set SMTP_USER="resend"
railway variables set SMTP_PASSWORD="re_..."
railway variables set EMAIL_FROM="noreply@yourdomain.com"

# Optional
railway variables set SENTRY_DSN="https://..."
```

### 4.2 Redeploy

After setting variables, redeploy:
```bash
railway up
```

---

## Step 5: Stripe Configuration

### 5.1 Create Products

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Products**
3. Create products:
   - **Professional**: $99/month
   - **Agency**: $299/month

### 5.2 Get Price IDs

Copy the Price IDs (starts with `price_`)

### 5.3 Configure Webhooks

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Endpoint URL:
   ```
   https://your-backend.up.railway.app/api/webhooks/stripe
   ```
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook signing secret

### 5.4 Update Railway

```bash
railway variables set STRIPE_PRICE_PROFESSIONAL="price_xxx"
railway variables set STRIPE_PRICE_AGENCY="price_xxx"
railway variables set STRIPE_WEBHOOK_SECRET="whsec_xxx"
```

---

## Step 6: Database Migrations

### 6.1 Connect to Database

```bash
# Install PostgreSQL client
psql "postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres?sslmode=require"
```

### 6.2 Run Initial Migration

The initial migration is in `backend/alembic/versions/001_initial_migration.py`.

To apply via Alembic:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL="postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres?sslmode=require"

# Run migrations
alembic upgrade head
```

### 6.3 Verify Tables Created

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

Expected tables:
- users
- candidates
- job_positions
- candidate_scores
- email_templates
- sent_emails
- activity_logs
- token_blacklist
- subscriptions
- team_members
- interviews
- onboarding_progress
- email_tracking
- resume_summaries

---

## Step 7: DNS Configuration (Production)

### 7.1 Configure Domain

In your DNS provider, add:

```
# API Subdomain
api.yourdomain.com     CNAME   your-backend.up.railway.app

# Frontend
yourdomain.com        CNAME   your-app.vercel.app
www.yourdomain.com    CNAME   your-app.vercel.app
```

### 7.2 Update Environment Variables

```bash
# Railway
railway variables set FRONTEND_URL="https://yourdomain.com"
railway variables set CORS_ORIGINS='["https://yourdomain.com"]'

# Vercel
vercel env add VITE_API_URL
# Enter: https://api.yourdomain.com/api
```

---

## Step 8: Verification Tests

### 8.1 Health Check

```bash
curl https://your-backend.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Recruiter In A Box",
  "version": "1.0.0",
  "database": "healthy"
}
```

### 8.2 Signup Test

```bash
curl -X POST https://your-backend.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "company_name": "Test Company"
  }'
```

### 8.3 Login Test

```bash
curl -X POST https://your-backend.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 8.4 AI Scoring Test (if OpenAI configured)

```bash
# Get access token from login response
TOKEN="your-access-token"

# Create candidate
curl -X POST https://your-backend.up.railway.app/api/candidates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "skills": ["Python", "JavaScript", "React"],
    "experience_years": 5
  }'

# Score candidate
curl -X POST https://your-backend.up.railway.app/api/scoring/candidate/{candidate_id} \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 9: Post-Deployment Checklist

- [ ] Health check returns healthy status
- [ ] Signup flow works
- [ ] Login flow works
- [ ] Stripe checkout redirects correctly
- [ ] Email sending (Resend) configured
- [ ] AI scoring returns results
- [ ] SSL certificate active
- [ ] CORS configured for production domain
- [ ] Error tracking (Sentry) active
- [ ] Monitoring alerts configured

---

## Troubleshooting

### Backend Not Starting

Check Railway logs:
```bash
railway logs
```

### Database Connection Issues

1. Verify DATABASE_URL format
2. Ensure SSL mode is `require`
3. Check Supabase connection pool settings

### CORS Errors

1. Verify CORS_ORIGINS includes your frontend URL
2. Check FRONTEND_URL matches exactly

### Stripe Webhooks Not Working

1. Verify webhook URL is accessible
2. Check webhook secret matches
3. Review Stripe webhook logs

---

## Support

For issues, check:
1. Railway deployment logs
2. Vercel build logs
3. Stripe webhook logs
4. Application error logs (Sentry)

---

*End of Deployment Guide*
