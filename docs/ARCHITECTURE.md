# Recruiter In A Box - System Architecture Document

**Version:** 1.0  
**Last Updated:** 2026-07-16  
**Status:** Ready for Review

---

## Table of Contents

1. [Business Overview](#1-business-overview)
2. [User Roles](#2-user-roles)
3. [System Components](#3-system-components)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Backend Architecture](#5-backend-architecture)
6. [AI Services](#6-ai-services)
7. [Authentication Flow](#7-authentication-flow)
8. [Database Architecture](#8-database-architecture)
9. [File Storage Strategy](#9-file-storage-strategy)
10. [Third-Party Integrations](#10-third-party-integrations)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Security Considerations](#12-security-considerations)

---

## 1. Business Overview

### 1.1 Product Vision

**Recruiter In A Box** is an AI-powered SaaS recruitment platform that helps businesses hire top talent 10x faster by automating candidate sourcing, scoring, and outreach.

### 1.2 Value Proposition

| Pain Point | Solution |
|------------|----------|
| 44+ days average hiring time | AI-powered candidate scoring |
| Resume overload | Automated parsing and ranking |
| Manual outreach | Bulk email with templates |
| Disorganized pipeline | Visual Kanban pipeline |
| Team collaboration | Multi-seat agency plans |

### 1.3 Business Model

```
+---------------------------------------------------------------------+
|                         PRICING TIERS                                 |
+---------------------+---------------------+---------------------------+
|       TRIAL         |    PROFESSIONAL     |          AGENCY          |
|    (14 days)       |     $99/month       |        $299/month        |
+---------------------+---------------------+---------------------------+
| Full feature access |  100 candidates     |  Unlimited candidates    |
| No credit card      |  10 jobs           |  Unlimited jobs          |
| required            |  1 seat            |  5 team seats           |
|                     |  Basic analytics   |  Advanced analytics      |
|                     |  Email support     |  Priority support       |
|                     |                    |  Custom branding        |
+---------------------+---------------------+---------------------------+
```

### 1.4 Core Features

1. **Resume Management** - Upload, parse, and manage candidate profiles
2. **AI Scoring** - Automated candidate evaluation against job requirements
3. **Outreach** - Email templates, bulk sending, tracking
4. **Pipeline** - Visual Kanban board for candidate progression
5. **Team Collaboration** - Multi-user access with role-based permissions
6. **Interview Scheduling** - Calendar integration and feedback
7. **Analytics** - Hiring metrics and performance dashboards

---

## 2. User Roles

### 2.1 Role Hierarchy

```
                         +-----------+
                         |   OWNER  |
                         | (1 max)  |
                         +-----+-----+
                               |
              +----------------+----------------+
              |                                 |
        +-----+-----+                     +-----+-----+
        |   ADMIN   |                     |   ADMIN   |
        |  (Agency  |                     |  (Agency  |
        |   only)   |                     |   only)   |
        +-----+-----+                     +-----+-----+
              |                                 |
              +-----------------+----------------+
                              |
              +---------------+---------------+
              |               |               |
        +-----+-----+   +---+---+   +---+---+
        |   MEMBER  |   | MEMBER|   | MEMBER|
        +-----------+   +-------+   +-------+
```

### 2.2 Role Permissions Matrix

| Feature | Owner | Admin | Member |
|---------|-------|-------|--------|
| Manage billing | Yes | No | No |
| Invite team | Yes | Yes | No |
| Remove team | Yes | Yes | No |
| Manage jobs | Yes | Yes | Yes |
| Manage candidates | Yes | Yes | Yes |
| Send emails | Yes | Yes | Yes |
| View analytics | Yes | Yes | Yes |
| Schedule interviews | Yes | Yes | Yes |

### 2.3 User Registration Flow

```
+------------+     +----------+     +----------+
|  Sign Up   | --->|  Email  | --->|  Login  |
|   Form     |     |  Verify |     |Dashboard |
+------------+     +----------+     +----------+
      |                                    |
      v                                    v
+------------+                    +----------+
|  Create    | ----------------> | Onboard |
|   Trial    |                   |  Modal  |
+------------+                   +----------+
```

---

## 3. System Components

### 3.1 High-Level Architecture

```
                                    +-------------------------------------------------------------+
                                    |                          USERS                                |
                                    |  +---------+  +---------+  +---------+  +---------+          |
                                    |  |Web App  |  | Mobile  |  |  API   |  |Webhooks |          |
                                    |  | Browser |  |   App   |  | Clients |  |  (SMTP) |          |
                                    |  +----+----+  +----+----+  +----+----+  +----+----+          |
                                    +---------+------------+------------+------------+------------+
                                                  |            |            |             |
                                                  v            v            v             v
                    +-------------------------------------------------------------------+
                    |                      LOAD BALANCER / CDN                               |
                    +-------------------------------------------------------------------+
                                                  |
                                                  v
        +---------------------------------------------------------------+
        |                     FRONTEND (Vercel/CDN)                       |
        |  +-----------+  +-----------+  +-----------+  +-----------+  |
        |  |  Landing  |  |  Login/   |  |Dashboard/ |  |  Pricing  |  |
        |  |   Page    |  |  Signup   |  |   App     |  |   Plans   |  |
        |  +-----------+  +-----------+  +-----------+  +-----------+  |
        +---------------------------------------------------------------+
                                                  |
                                                  v REST API
        +---------------------------------------------------------------+
        |                  BACKEND (FastAPI + Uvicorn)                    |
        |  +----------+  +----------+  +----------+  +----------+       |
        |  | Auth API|  |Candidates|  |  Jobs    |  |  Email   |       |
        |  +----+-----+  +----+-----+  +----+-----+  +----+-----+       |
        |       |             |             |             |              |
        |  +----v-------------v-------------v-------------v----+         |
        |  |                 BUSINESS LOGIC LAYER           |         |
        |  |  +----------+  +----------+  +----------+     |         |
        |  |  |   Auth   |  |   AI/ML  |  |  Email   |     |         |
        |  |  |  Service |  |  Service |  |  Service |     |         |
        |  |  +----------+  +----------+  +----------+     |         |
        |  +----------------------------------------------------+         |
        +---------------------------------------------------------------+
                                    |                    |                    |
                                    v                    v                    v
                    +----------------+  +----------------+  +----------------+
                    |   PostgreSQL   |  |     Redis      |  |    OpenAI     |
                    |   (Primary DB) |  |   (Cache/Q)   |  |   (AI/ML)     |
                    +----------------+  +----------------+  +----------------+
                                    |
                                    v
                    +----------------+
                    |    Supabase    |
                    |   (File Store) |
                    +----------------+
```

### 3.2 Component Inventory

| Component | Technology | Purpose | Scalability |
|----------|------------|---------|-------------|
| Frontend | React + Vite | User interface | CDN-ready |
| API Gateway | Nginx/Cloudflare | Request routing | Horizontal |
| Backend | FastAPI | Business logic | Horizontal |
| Database | PostgreSQL | Persistent storage | Vertical/Read replicas |
| Cache | Redis | Sessions, cache | Cluster |
| File Storage | Supabase S3 | Resume uploads | Auto-scale |
| AI Service | OpenAI API | Scoring/Summaries | API limits |
| Payments | Stripe | Subscriptions | Handled externally |

---

## 4. Frontend Architecture

### 4.1 Technology Stack

```
+---------------------------------------------------------------------+
|                         FRONTEND STACK                                |
+---------------------------------------------------------------------+
|                                                                      |
|     +------------+       +------------+       +------------+          |
|     |   React   |       |   Vite    |       |  Tailwind  |          |
|     |   18.x    |   +   |   Build   |   +   |    CSS     |          |
|     |  (UI Lib) |   |   |   Tool    |   |   |  (Styling) |          |
|     +------------+   |   +------------+   |   +------------+          |
|                      |          |         |                           |
|                      v          v         v                           |
|              +------------+  +------------+  +------------+           |
|              |React Router|  |React Query|  |   Lucide   |           |
|              |  (Routes)  |  |  (State)  |  |  (Icons)  |           |
|              +------------+  +------------+  +------------+           |
|                                                                      |
+---------------------------------------------------------------------+
```

### 4.2 Page Structure

```
src/
|-- pages/
|   |-- Landing.tsx          # Marketing landing page
|   |-- Pricing.tsx           # Pricing plans
|   |-- Login.tsx            # Authentication
|   |-- Signup.tsx           # Registration
|   |-- Dashboard.tsx        # Main dashboard
|   |-- Candidates.tsx       # Candidate management
|   |-- Jobs.tsx             # Job positions
|   |-- Interviews.tsx       # Interview scheduling
|   |-- Templates.tsx        # Email templates
|   |-- Outreach.tsx         # Email campaigns
|   |-- Team.tsx             # Team management
|   |-- Analytics.tsx        # Reports/charts
|   +-- Settings.tsx        # User settings
|
|-- components/
|   |-- layout/
|   |   |-- Sidebar.tsx     # Navigation sidebar
|   |   |-- Header.tsx       # Top header
|   |   +-- Layout.tsx       # Main layout wrapper
|   |
|   |-- common/
|   |   |-- Button.tsx       # Reusable button
|   |   |-- Card.tsx          # Container card
|   |   |-- Modal.tsx         # Dialog modal
|   |   |-- Input.tsx         # Form inputs
|   |   +-- Badge.tsx         # Status badges
|   |
|   +-- onboarding/
|       +-- OnboardingModal.tsx  # Setup wizard
|
|-- services/
|   +-- api.ts               # Axios API client
|
|-- hooks/
|   +-- useAuth.tsx         # Authentication hook
|
+-- types/
    +-- index.ts             # TypeScript definitions
```

### 4.3 State Management Strategy

```
+---------------------------------------------------------------------+
|                      STATE MANAGEMENT                                  |
+---------------------------------------------------------------------+

+--------------+     +--------------+     +--------------+
|  Server State|     |   UI State   |     |  Auth State  |
| (React Query)|     |  (useState) |     |  (Context)  |
+--------------+     +--------------+     +--------------+
| * API data   |     | * Modal open |     | * User data |
| * Cached     |     | * Form inputs|     | * Token     |
| * Loading    |     | * Active tab |     | * Permissions|
| * Errors     |     | * Search     |     | * Subscription|
+-------+------+     +------+------+     +------+------+
        |                   |                   |
        v                   v                   v
+--------------------------------------------------------------------+
|                     REQUEST LAYER (Axios)                            |
|  * Automatic retry    * Request/response interceptors                |
|  * Token refresh      * Error handling                              |
+--------------------------------------------------------------------+
```

---

## 5. Backend Architecture

### 5.1 Technology Stack

```
+---------------------------------------------------------------------+
|                         BACKEND STACK                                 |
+---------------------------------------------------------------------+

     +------------+       +------------+       +------------+
     |  FastAPI   |       | SQLAlchemy |       |  Pydantic  |
     | (Framework|   +   |   (ORM)    |   +   | (Validation)|
     +------------+   |   +------------+   |   +------------+
                       |          |         |
                       v          v         v
              +------------+  +------------+  +------------+
              |  Uvicorn  |  |  AsyncPG   |  |  JWT Auth   |
              |  (Server) |  |  (Driver)  |  | (python-jose)|
              +------------+  +------------+  +------------+

+---------------------------------------------------------------------+
```

### 5.2 API Structure

```
backend/app/
|-- api/
|   |-- __init__.py              # Router aggregation
|   |-- auth/
|   |   +-- router.py           # POST /api/auth/*
|   |-- candidates/
|   |   +-- router.py           # CRUD /api/candidates/*
|   |-- jobs/
|   |   +-- router.py           # CRUD /api/jobs/*
|   |-- scoring/
|   |   +-- router.py           # POST /api/scoring/*
|   |-- templates/
|   |   +-- router.py           # CRUD /api/templates/*
|   |-- outreach/
|   |   +-- router.py           # POST /api/outreach/*
|   |-- dashboard/
|   |   +-- router.py           # GET /api/dashboard/*
|   |-- subscriptions/
|   |   +-- router.py           # POST /api/subscriptions/*
|   |-- teams/
|   |   +-- router.py           # CRUD /api/teams/*
|   |-- interviews/
|   |   +-- router.py           # CRUD /api/interviews/*
|   +-- onboarding/
|       +-- router.py           # GET/POST /api/onboarding/*
|
|-- core/
|   |-- config.py               # Settings/env vars
|   |-- database.py             # DB connection
|   +-- security.py            # Password hashing, JWT
|
|-- models/
|   |-- models.py               # Core entities
|   +-- subscription_models.py  # SaaS entities
|
|-- schemas/
|   |-- schemas.py              # Core schemas
|   +-- saas_schemas.py        # SaaS schemas
|
|-- services/
|   |-- ai_service.py           # OpenAI integration
|   +-- stripe_service.py       # Stripe integration
|
+-- utils/
    |-- helpers.py              # Utility functions
    +-- seed.py                # Database seeding
```

### 5.3 API Endpoints Summary

| Category | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| Auth | POST | `/api/auth/signup` | User registration |
| Auth | POST | `/api/auth/login` | User login |
| Auth | POST | `/api/auth/refresh` | Refresh token |
| Auth | POST | `/api/auth/reset-password` | Password reset |
| Candidates | GET | `/api/candidates` | List candidates |
| Candidates | POST | `/api/candidates` | Create candidate |
| Candidates | POST | `/api/candidates/upload` | Upload resume |
| Jobs | GET | `/api/jobs` | List jobs |
| Jobs | POST | `/api/jobs` | Create job |
| Scoring | POST | `/api/scoring/candidate/:id` | Score candidate |
| Templates | GET | `/api/templates` | List templates |
| Templates | POST | `/api/templates` | Create template |
| Outreach | POST | `/api/outreach/send` | Send email |
| Outreach | POST | `/api/outreach/bulk` | Bulk send |
| Dashboard | GET | `/api/dashboard/overview` | Stats overview |
| Subscriptions | GET | `/api/subscriptions/status` | Get status |
| Subscriptions | POST | `/api/subscriptions/checkout` | Create checkout |
| Teams | GET | `/api/teams` | List members |
| Teams | POST | `/api/teams/invite` | Invite member |
| Interviews | GET | `/api/interviews` | List interviews |
| Interviews | POST | `/api/interviews` | Schedule interview |
| Onboarding | GET | `/api/onboarding` | Get progress |

---

## 6. AI Services

### 6.1 AI Service Architecture

```
+---------------------------------------------------------------------+
|                         AI SERVICES                                   |
+---------------------------------------------------------------------+

+-------------------+         +-------------------+
|    CANDIDATE      |         |     RESUME        |
|    SCORING        |         |    SUMMARIES     |
+-------------------+         +-------------------+
| * Skills match    |         | * Key strengths  |
| * Experience match |         | * Concerns       |
| * Education match  |         | * Next steps    |
| * Overall score    |         | * Quick summary |
+--------+----------+         +--------+----------+
         |                              |
         +---------------+--------------+
                         |
                         v
              +-------------------+
              |     OPENAI API     |
              |   (GPT-4 Turbo)   |
              +-------------------+
```

### 6.2 Scoring Algorithm

```
+---------------------------------------------------------------------+
|                CANDIDATE SCORING ALGORITHM                            |
+---------------------------------------------------------------------+

CANDIDATE DATA                    JOB REQUIREMENTS
+---------------                  -----------------
* Skills: [Python, React...]     * Required: [Python, AWS]
* Experience: 5 years            * Preferred: [React, Docker]
* Education: Bachelor             * Min Exp: 3 years
                                  * Education: Bachelor

        |                               |
        v                               v
+---------------+           +---------------------+
| SKILLS SCORE |           |   EXPERIENCE SCORE  |
|    (40%)     |           |       (35%)        |
+---------------+           +---------------------+
| * 4/5 required|           | * 5 >= 3, excess  |
|   match = 80% |           |   bonus = 115%    |
| * 2/3 prefer |           | * Cap at 100%     |
|   match = 67% |           +---------+---------+
| * Weighted    |                     |
|   = 76%      |                     |
+-------+-------+                     |
        |                             |
        +------------+----------------+
                     |
                     v
            +-----------------+
            |    EDUCATION     |
            |     SCORE        |
            |     (25%)       |
            +-----------------+
            | Bachelor (3) >= |
            | Bachelor (3)    |
            | Score = 100%   |
            +--------+--------+
                     |
                     v
+---------------------------------------------------------------------+
|                      OVERALL SCORE                                    |
|                                                                      |
|   (76 x 0.40) + (100 x 0.35) + (100 x 0.25) = 90.4               |
|                                                                      |
|   +--------------------------------------------------------------+ |
|   |  SCORE BREAKDOWN                                             | |
|   |  [██████████████████████████████████████░░░░]  90.4/100    | |
|   +--------------------------------------------------------------+ |
+---------------------------------------------------------------------+
```

---

## 7. Authentication Flow

### 7.1 Authentication Architecture

```
+---------------------------------------------------------------------+
|                     AUTHENTICATION FLOW                                |
+---------------------------------------------------------------------+

+---------+                                      +---------+
|  USER   |                                      | BACKEND |
+---------+                                      +----+----+
     |                                               |
     |  1. POST /api/auth/signup                     |
     |  -------------------------------------------> |
     |     {email, password, full_name}              |
     |                                               |
     |  2. Create user, hash password                |
     |  3. Generate tokens                          |
     |     * Access token (15 min)                   |
     |     * Refresh token (7 days)                  |
     |  <------------------------------------------- |
     |     {access_token, refresh_token}              |
     |                                               |
     |  4. Store tokens in memory/localStorage      |
     |                                               |
     |  5. API requests with Bearer token           |
     |  -------------------------------------------> |
     |     Authorization: Bearer {access_token}       |
     |                                               |
     |  6. Validate JWT, check expiration          |
     |  <------------------------------------------- |
     |     {data} or {error: 401}                  |
     |                                               |
     |  7. If 401, try refresh                     |
     |  -------------------------------------------> |
     |     POST /api/auth/refresh                   |
     |     {refresh_token}                           |
     |                                               |
     |  <------------------------------------------- |
     |     {new_access_token, new_refresh_token}     |
```

### 7.2 JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "plan": "professional",
  "iat": 1689000000,
  "exp": 1689000900
}
```

---

## 8. Database Architecture

### 8.1 Entity Relationship Diagram

```
+---------------------------------------------------------------------+
|                       DATABASE SCHEMA                                 |
+---------------------------------------------------------------------+

                                 +-----------------+
                                 |     USERS       |
                                 +-----------------+
                                 | id (PK)        |
                                 | email (UNIQUE) |
                                 | password_hash   |
                                 | full_name      |
                                 | company_name   |
                                 | email_verified |
                                 | created_at     |
                                 +--------+--------+
                                          |
              +----------------------------+----------------------------+
              |                            |                            |
              v                            v                            v
+-----------------------+    +-----------------------+    +-----------------------+
|   SUBSCRIPTIONS       |    |     CANDIDATES        |    |    JOB_POSITIONS      |
+-----------------------+    +-----------------------+    +-----------------------+
| id (PK)              |    | id (PK)              |    | id (PK)              |
| user_id (FK)        <----->| user_id (FK)         |    | user_id (FK)         <--+
| stripe_customer       |    | full_name            |    | title                |   |
| stripe_sub           |    | email                |    | description          |   |
| plan_type            |    | phone                |    | requirements         |   |
| status               |    | resume_url           |    | department           |   |
| trial_end            |    | skills               |    | location             |   |
+----------+-----------+    | status              |    | status               |   |
           |               +---------+-----------+    +-----------------------+
           |                         |                                 |
           |         +--------------+--------------+                   |
           |         |              |              |                   |
           |         v              v              v                   |
           |  +-----------+  +-----------+  +-----------+           |
           |  | CANDIDATE |  |SENT_EMAILS|  |INTERVIEWS |           |
           |  |  SCORES   |  |           |  |           |           |
           |  +-----------+  +-----------+  +-----------+           |
           |  |candidate_id<--|candidate_id<--|candidate_id<----------+
           |  | job_id (FK)|  | user_id    |  | job_id (FK)|
           |  +-----------+  | subject    |  | scheduled  |
           |                 | status     |  | status    |
           |                 | opened_at  |  | feedback  |
           |                 +-----------+  +-----------+
           v
    +-------------------+
    |   TEAM_MEMBERS   |
    +-------------------+
    | id (PK)          |
    | subscription_id <---+
    | email            |
    | role             |
    | status           |
    | invite_token     |
    +-------------------+
```

### 8.2 Database Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `users` | User accounts | email, password_hash, full_name |
| `subscriptions` | Billing info | stripe_customer_id, plan_type, trial_end |
| `team_members` | Team collaboration | email, role, invite_token |
| `candidates` | Job seekers | full_name, email, skills, status |
| `job_positions` | Open roles | title, requirements, status |
| `candidate_scores` | AI scores | skills_score, experience_score, overall_score |
| `email_templates` | Email templates | name, subject, body |
| `sent_emails` | Email history | status, opened_at, replied_at |
| `interviews` | Interview schedule | scheduled_at, feedback, rating |
| `onboarding_progress` | User onboarding | current_step, tour_completed |
| `email_tracking` | Open/click tracking | tracking_id, opened, click_count |
| `resume_summaries` | AI summaries | summary, key_strengths |
| `activity_logs` | Audit trail | action, entity_type, entity_id |

---

## 9. File Storage Strategy

### 9.1 Storage Architecture

```
+---------------------------------------------------------------------+
|                      FILE STORAGE FLOW                                 |
+---------------------------------------------------------------------+

+--------+      +--------+      +--------+      +--------+
|Browser |      |Backend |      |Supabase|      |   S3   |
+--------+      +---+----+      +----+----+      +----+----+
   |                |                |                |
   | 1. Upload     |                |                |
   |    file       |                |                |
   | ------------->|                |                |
   |                |                |                |
   | 2. Validate   |                |                |
   |    (size,     |                |                |
   |     type)     |                |                |
   |                |                |                |
   | 3. Request    |                |                |
   |    upload URL |                |                |
   | ------------->|                |                |
   |                | 4. Generate  |                |
   |                |    signed URL|                |
   |                | <------------|                |
   |                |                |                |
   | 5. Upload     |                |                |
   |    directly   |                |                |
   | ------------------------------------------------>|
   |                |                |                |
   | 6. Return URL |                |                |
   | <-------------|                |                |
   |                |                |                |
   | 7. Save URL   |                |                |
   |    to DB      |                |                |
   | ------------->|                |                |
```

### 9.2 File Types & Limits

| File Type | Max Size | Storage Location | Retention |
|-----------|----------|-----------------|------------|
| Resume (PDF) | 10 MB | Supabase Storage | Until deleted |
| Resume (DOCX) | 10 MB | Supabase Storage | Until deleted |
| Profile Image | 2 MB | Supabase Storage | Until deleted |

---

## 10. Third-Party Integrations

### 10.1 Integration Map

```
+---------------------------------------------------------------------+
|                   THIRD-PARTY INTEGRATIONS                            |
+---------------------------------------------------------------------+

                       +-----------------+
                       |    RECRUITER    |
                       |    IN A BOX     |
                       +--------+--------+
                                |
        +-------------+---------+---------+-------------+
        |             |         |         |             |
        v             v         v         v             v
    +---------+  +---------+  +---------+  +---------+  +---------+
    | Supabase|  | Stripe  |  | OpenAI  |  |  SMTP   |  |Calendar |
    | Storage |  |Payments |  |   API   |  |Provider |  |   API   |
    +---------+  +---------+  +---------+  +---------+  +---------+
    | Resume   |  | Subs    |  | Scoring |  | Outreach|  | Zoom    |
    | Upload   |  | Billing |  | Summaries|  | Email  |  | Meet   |
    +---------+  +---------+  +---------+  +---------+  +---------+
```

### 10.2 Integration Details

| Service | Purpose | Data Exchanged | Security |
|---------|---------|----------------|----------|
| **Stripe** | Payments | Customer ID, Subscription ID, Payment methods | PCI compliant |
| **OpenAI** | AI/ML | Resume text, Job requirements | API key, no PII storage |
| **Supabase** | Storage/DB | Resume files, User data | Row-level security |
| **SMTP** | Email | Email content, Recipient addresses | TLS encryption |
| **Google Calendar** | Scheduling | Event details, Attendees | OAuth 2.0 |

---

## 11. Deployment Architecture

### 11.1 Production Architecture

```
+---------------------------------------------------------------------+
|                     PRODUCTION DEPLOYMENT                             |
+---------------------------------------------------------------------+

                              INTERNET
                                  |
                                  v
+---------------------------------------------------------------------+
|                        CLOUDFLARE CDN                                 |
|                    (DDoS Protection, SSL)                             |
+---------------------------------------------------------------------+
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
+-------------------------------+     +-------------------------------+
|         VERCEL / NETLIFY      |     |       RAILWAY / FLY.IO       |
|         (Frontend Hosting)     |     |       (Backend Hosting)       |
|                               |     |                               |
|  * CDN distribution          |     |  * Docker containers          |
|  * Edge caching              |     |  * Auto-scaling              |
|  * Preview deployments       |     |  * Load balancing            |
+-------------------------------+     +---------------+--------------+
                                                |
                              +-----------------+-----------------+
                              |                 |                 |
                              v                 v                 v
                    +----------------+  +----------------+  +----------------+
                    |   PostgreSQL   |  |     Redis      |  |   Supabase    |
                    | (RDS/Supabase |  |   (Upstash)   |  |   (Storage)   |
                    |    Primary)    |  |   (Cache)     |  |               |
                    +----------------+  +----------------+  +----------------+
```

---

## 12. Security Considerations

### 12.1 Security Architecture

```
+---------------------------------------------------------------------+
|                        SECURITY LAYERS                                |
+---------------------------------------------------------------------+

+---------------------------------------------------------------------+
|  LAYER 1: NETWORK                                                  |
+---------------------------------------------------------------------+
|  * CloudFlare DDoS protection                                       |
|  * TLS 1.3 encryption                                              |
|  * HSTS headers                                                     |
|  * CORS policies                                                    |
+---------------------------------------------------------------------+
                              |
                              v
+---------------------------------------------------------------------+
|  LAYER 2: APPLICATION                                              |
+---------------------------------------------------------------------+
|  * JWT authentication                                              |
|  * Rate limiting (100 req/min)                                      |
|  * Input validation (Pydantic)                                      |
|  * SQL injection prevention (ORM)                                   |
|  * XSS prevention (React auto-escaping)                            |
+---------------------------------------------------------------------+
                              |
                              v
+---------------------------------------------------------------------+
|  LAYER 3: DATA                                                     |
+---------------------------------------------------------------------+
|  * Password hashing (Bcrypt, cost=12)                                |
|  * Database encryption at rest                                       |
|  * Row-level security                                               |
|  * PII encryption                                                  |
|  * Secure file upload (type validation)                             |
+---------------------------------------------------------------------+
                              |
                              v
+---------------------------------------------------------------------+
|  LAYER 4: ACCESS                                                   |
+---------------------------------------------------------------------+
|  * Role-based access control (RBAC)                                 |
|  * API key scoping                                                  |
|  * Audit logging                                                    |
|  * Session management                                               |
|  * Token expiration/rotation                                         |
+---------------------------------------------------------------------+
```

### 12.2 Security Checklist

| Category | Item | Status |
|----------|------|--------|
| **Transport** | HTTPS enforced | Yes |
| **Transport** | TLS 1.2+ only | Yes |
| **Auth** | JWT with short expiry | Yes |
| **Auth** | Secure refresh tokens | Yes |
| **Auth** | Password hashing | Yes |
| **Input** | Input validation | Yes |
| **Output** | Output encoding | Yes |
| **Database** | Parameterized queries | Yes |
| **Files** | File type validation | Yes |
| **Files** | File size limits | Yes |
| **Secrets** | Env vars, not code | Yes |
| **Logging** | Audit trail | Yes |

### 12.3 API Rate Limiting

```
+---------------------------------------------------------------------+
|                       RATE LIMITING RULES                             |
+---------------------------------------------------------------------+

+--------------------+---------------------------------------------------+
| Endpoint Pattern   | Limit                                            |
+--------------------+---------------------------------------------------+
| /api/auth/*        | 10 requests/minute per IP                       |
| /api/candidates/*  | 100 requests/minute per user                   |
| /api/outreach/*    | 50 requests/minute per user                    |
| /api/scoring/*     | 20 requests/minute per user                    |
| /api/* (read)      | 200 requests/minute per user                   |
+--------------------+---------------------------------------------------+
```

---

## Appendix A: System Diagrams

### A.1 Complete Data Flow

```
+---------------------------------------------------------------------+
|                   COMPLETE SYSTEM DATA FLOW                           |
+---------------------------------------------------------------------+

USER --> BROWSER --> CDN --> FRONTEND --> REST API --> BACKEND
  |                                              |
  |                                              v
  |                                        +-------------+
  |                                        |  SERVICES   |
  |                                        |             |
  |                                        | * AI/ML     |
  |                                        | * Email     |
  |                                        | * Billing   |
  |                                        | * Onboard   |
  |                                        +------+------+
  |                                               |
      |              |              |           |
      v              v              v           v
  +---------+   +---------+   +---------+   +---------+
  |  OpenAI |   | Stripe  |   |  SMTP   |   |Supabase |
  |   API   |   |         |   | Server  |   | Storage |
  +---------+   +---------+   +---------+   +---------+
                                                  |
                                                  v
                                             +---------+
                                             |Postgres |
                                             |   DB    |
                                             +---------+
```

### A.2 Subscription State Machine

```
+---------------------------------------------------------------------+
|              SUBSCRIPTION STATE MACHINE                                |
+---------------------------------------------------------------------+

                    +--------------+
                    |    TRIAL      |
                    |  (14 days)   |
                    +------+-------+
                           |
          +---------------+---------------+
          |               |               |
          v               v               v
    +----------+   +----------+   +----------+
    |EXPIRED   |   | ACTIVE   |   |EXPIRED   |
    |(manual)  |   |  (paid)  |   |(no pay)  |
    +----------+   +-----+-----+   +----------+
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
    +----------+ +----------+ +----------+
    | CANCELED | | PAST_DUE | | ACTIVE   |
    |(by user) | | (payment | |(downgrade|
    +----------+ | failed)  | | plan)    |
                 +----------+ +----------+
```

---

## Appendix B: API Response Formats

### B.1 Success Response
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

### B.2 Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | AI Assistant | Initial architecture document |

---

*End of Document*
