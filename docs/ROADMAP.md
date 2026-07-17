# Recruiter In A Box - Development Roadmap

**Version:** 1.0  
**Last Updated:** 2026-07-16  
**Status:** Draft for Review

---

## Table of Contents

1. [Overview](#1-overview)
2. [Epic 1: Authentication](#2-epic-1-authentication)
3. [Epic 2: Candidate Management](#3-epic-2-candidate-management)
4. [Epic 3: AI Scoring](#4-epic-3-ai-scoring)
5. [Epic 4: Outreach](#5-epic-4-outreach)
6. [Epic 5: Analytics](#6-epic-5-analytics)
7. [Epic 6: Billing](#7-epic-6-billing)
8. [Epic 7: Deployment](#8-epic-7-deployment)
9. [Timeline Overview](#9-timeline-overview)
10. [Milestone Summary](#10-milestone-summary)

---

## 1. Overview

### 1.1 Development Phases

```
+==============================================================================+
|                         DEVELOPMENT PHASES                                      |
+==============================================================================+

Phase 1: Foundation (Weeks 1-4)
+---------+---------+---------+---------+
| Auth    | User    | Basic   | Tests   |
| Core    | Model   | API     | Setup   |
+---------+---------+---------+---------+

Phase 2: Core Features (Weeks 5-8)
+---------+---------+---------+---------+
|Candidate| Job     | Basic   | Stripe  |
| CRUD    | CRUD    | Pipeline| Setup  |
+---------+---------+---------+---------+

Phase 3: AI & Outreach (Weeks 9-12)
+---------+---------+---------+---------+
| AI      | Email   | Temp-   | Track- |
| Scoring | Service | lates  | ing    |
+---------+---------+---------+---------+

Phase 4: Polish & Launch (Weeks 13-16)
+---------+---------+---------+---------+
|Analytics| Onboard | Team   | Deploy |
|Dashboard | Flow    | Manage | Prod   |
+---------+---------+---------+---------+
```

### 1.2 Priority Matrix

```
                    HIGH IMPACT
                         │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    │   Auth Core       │   AI Scoring      │
    │   Candidate CRUD  │   Outreach        │
    │   Job CRUD        │   Analytics       │
    │                   │                   │
────┼───────────────────┼───────────────────┼──── LOW IMPACT
    │                   │                   │
    │   Team Manage     │   Onboarding      │
    │   Interviews      │   Custom Branding │
    │                   │                   │
    │                   │                   │
                         │
                    LOW IMPACT
```

---

## 2. Epic 1: Authentication

**Objective:** Secure user authentication and authorization system with JWT tokens and session management.

### 2.1 Milestones

#### Milestone 1.1: User Registration ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 1.1.1 | Create user registration endpoint | 4 |
| 1.1.2 | Implement password hashing (bcrypt) | 2 |
| 1.1.3 | Add email validation | 2 |
| 1.1.4 | Create user response schema | 1 |
| 1.1.5 | Write unit tests | 4 |
| **Total** | | **13 hours** |

**Deliverables:**
- `POST /api/auth/signup` endpoint
- Password validation and hashing
- Duplicate email check

#### Milestone 1.2: Login & JWT Tokens ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 1.2.1 | Create login endpoint | 4 |
| 1.2.2 | Implement JWT token generation | 4 |
| 1.2.3 | Add refresh token mechanism | 4 |
| 1.2.4 | Create token validation middleware | 4 |
| 1.2.5 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- `POST /api/auth/login` endpoint
- Access token (15 min expiry)
- Refresh token (7 day expiry)
- `get_current_user` dependency

#### Milestone 1.3: Password Reset ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 1.3.1 | Create password reset request endpoint | 4 |
| 1.3.2 | Generate reset token | 2 |
| 1.3.3 | Create password reset confirmation endpoint | 4 |
| 1.3.4 | Implement token expiration | 2 |
| 1.3.5 | Write unit tests | 4 |
| **Total** | | **16 hours** |

**Deliverables:**
- `POST /api/auth/reset-password` endpoint
- `POST /api/auth/reset-password/confirm` endpoint
- Token-based reset flow

#### Milestone 1.4: User Profile ⭐
**Estimated Duration:** 1 day  
**Priority:** P2 (Medium)

| Task | Description | Hours |
|------|-------------|-------|
| 1.4.1 | Create profile retrieval endpoint | 2 |
| 1.4.2 | Create profile update endpoint | 2 |
| 1.4.3 | Write unit tests | 4 |
| **Total** | | **8 hours** |

**Deliverables:**
- `GET /api/auth/me` endpoint
- `PUT /api/auth/me` endpoint

### 2.2 Implementation Order

```
1. User Registration (1.1) → Login & JWT (1.2) → Password Reset (1.3) → Profile (1.4)
   |__________________|__________________|__________________|
          Week 1               Week 2              Week 3
```

---

## 3. Epic 2: Candidate Management

**Objective:** Full CRUD operations for candidates with resume parsing and profile management.

### 3.1 Milestones

#### Milestone 2.1: Candidate CRUD ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 2.1.1 | Create candidate model and schema | 4 |
| 2.1.2 | Implement list candidates endpoint | 4 |
| 2.1.3 | Implement create candidate endpoint | 4 |
| 2.1.4 | Implement get candidate endpoint | 2 |
| 2.1.5 | Implement update candidate endpoint | 2 |
| 2.1.6 | Implement delete candidate endpoint | 2 |
| 2.1.7 | Add pagination | 2 |
| 2.1.8 | Write unit tests | 8 |
| **Total** | | **28 hours** |

**Deliverables:**
- `GET /api/candidates` with pagination
- `POST /api/candidates`
- `GET /api/candidates/{id}`
- `PUT /api/candidates/{id}`
- `DELETE /api/candidates/{id}`

#### Milestone 2.2: Resume Upload & Parsing ⭐
**Estimated Duration:** 4 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 2.2.1 | Set up file upload endpoint | 4 |
| 2.2.2 | Implement PDF text extraction | 8 |
| 2.2.3 | Create basic text parsing logic | 8 |
| 2.2.4 | Extract name, email, phone | 4 |
| 2.2.5 | Extract skills and experience | 4 |
| 2.2.6 | Store resume file (Supabase) | 4 |
| 2.2.7 | Write unit tests | 8 |
| **Total** | | **40 hours** |

**Deliverables:**
- `POST /api/candidates/upload`
- PDF text extraction
- Basic field extraction
- File storage integration

#### Milestone 2.3: Search & Filtering ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 2.3.1 | Implement text search | 4 |
| 2.3.2 | Add status filter | 2 |
| 2.3.3 | Add source filter | 2 |
| 2.3.4 | Add skills filter | 4 |
| 2.3.5 | Write unit tests | 4 |
| **Total** | | **16 hours** |

**Deliverables:**
- Full-text search on candidates
- Multiple filter options
- Combined search + filter

#### Milestone 2.4: Pipeline Status ⭐
**Estimated Duration:** 1 day  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 2.4.1 | Define status transitions | 2 |
| 2.4.2 | Add bulk status update | 4 |
| 2.4.3 | Write unit tests | 2 |
| **Total** | | **8 hours** |

**Deliverables:**
- Status workflow: new → screening → interview → offer → hired/rejected
- Bulk status updates

### 3.2 Implementation Order

```
Candidate CRUD (2.1) → Resume Upload (2.2) → Search (2.3) → Pipeline (2.4)
|________________|___________________|________________|_______________|
      Week 5              Week 6             Week 7           Week 8
```

---

## 4. Epic 3: AI Scoring

**Objective:** AI-powered candidate evaluation with skills, experience, and education matching.

### 4.1 Milestones

#### Milestone 3.1: AI Service Integration ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 3.1.1 | Set up OpenAI API client | 4 |
| 3.1.2 | Create scoring prompt templates | 4 |
| 3.1.3 | Implement skills matching | 8 |
| 3.1.4 | Implement experience scoring | 4 |
| 3.1.5 | Implement education scoring | 4 |
| 3.1.6 | Write unit tests | 8 |
| **Total** | | **32 hours** |

**Deliverables:**
- OpenAI integration
- Skills match scoring (40% weight)
- Experience match scoring (35% weight)
- Education match scoring (25% weight)

#### Milestone 3.2: Candidate Scoring API ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 3.2.1 | Create scoring endpoint | 4 |
| 3.2.2 | Add job requirements context | 4 |
| 3.2.3 | Store scores in database | 4 |
| 3.2.4 | Return score breakdown | 2 |
| 3.2.5 | Write unit tests | 4 |
| **Total** | | **18 hours** |

**Deliverables:**
- `POST /api/scoring/candidate/{id}`
- Score breakdown with details
- Database persistence

#### Milestone 3.3: Bulk Scoring ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 3.3.1 | Create bulk scoring endpoint | 4 |
| 3.3.2 | Implement queue processing | 8 |
| 3.3.3 | Add progress tracking | 4 |
| 3.3.4 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- `POST /api/scoring/bulk`
- Background job processing
- Progress notifications

#### Milestone 3.4: Resume Summaries ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 3.4.1 | Create summary prompt | 4 |
| 3.4.2 | Implement summary generation | 8 |
| 3.4.3 | Extract key strengths | 4 |
| 3.4.4 | Extract concerns | 4 |
| 3.4.5 | Write unit tests | 4 |
| **Total** | | **24 hours** |

**Deliverables:**
- AI-generated candidate summaries
- Key strengths extraction
- Potential concerns identification

### 4.2 Implementation Order

```
AI Service (3.1) → Scoring API (3.2) → Bulk Scoring (3.3) → Summaries (3.4)
|_______________|________________|_________________|________________|
      Week 9           Week 10           Week 11             Week 12
```

---

## 5. Epic 4: Outreach

**Objective:** Email templates, bulk sending, and engagement tracking.

### 5.1 Milestones

#### Milestone 4.1: Email Templates ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 4.1.1 | Create template model and schema | 2 |
| 4.1.2 | Implement CRUD endpoints | 8 |
| 4.1.3 | Add variable interpolation | 4 |
| 4.1.4 | Create default templates | 4 |
| 4.1.5 | Write unit tests | 4 |
| **Total** | | **22 hours** |

**Deliverables:**
- `GET/POST /api/templates`
- `GET/PUT/DELETE /api/templates/{id}`
- Variable system: `{candidate_name}`, `{position}`, etc.

#### Milestone 4.2: Email Sending ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 4.2.1 | Set up SMTP configuration | 4 |
| 4.2.2 | Create single email endpoint | 4 |
| 4.2.3 | Implement template rendering | 4 |
| 4.2.4 | Add email queuing | 4 |
| 4.2.5 | Track sent status | 4 |
| 4.2.6 | Write unit tests | 4 |
| **Total** | | **24 hours** |

**Deliverables:**
- `POST /api/outreach/send`
- Template-based email composition
- Email queue with status tracking

#### Milestone 4.3: Bulk Email ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 4.3.1 | Create bulk send endpoint | 4 |
| 4.3.2 | Implement batch processing | 8 |
| 4.3.3 | Add progress tracking | 4 |
| 4.3.4 | Rate limiting per recipient | 4 |
| 4.3.5 | Write unit tests | 4 |
| **Total** | | **24 hours** |

**Deliverables:**
- `POST /api/outreach/bulk`
- Batch processing with queue
- Progress tracking

#### Milestone 4.4: Email Tracking ⭐
**Estimated Duration:** 3 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 4.4.1 | Create tracking pixel | 4 |
| 4.4.2 | Implement open tracking | 4 |
| 4.4.3 | Implement click tracking | 8 |
| 4.4.4 | Add tracking dashboard | 4 |
| 4.4.5 | Write unit tests | 4 |
| **Total** | | **24 hours** |

**Deliverables:**
- Open tracking (1x1 pixel)
- Click tracking (URL rewriting)
- Tracking dashboard

### 5.2 Implementation Order

```
Templates (4.1) → Email Sending (4.2) → Bulk Email (4.3) → Tracking (4.4)
|_____________|___________________|_________________|________________|
      Week 9           Week 10           Week 11           Week 12
```

---

## 6. Epic 5: Analytics

**Objective:** Dashboard with hiring metrics, pipeline visualization, and activity tracking.

### 6.1 Milestones

#### Milestone 5.1: Dashboard API ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 5.1.1 | Create overview endpoint | 4 |
| 5.1.2 | Create pipeline endpoint | 4 |
| 5.1.3 | Create metrics endpoint | 4 |
| 5.1.4 | Create activity endpoint | 4 |
| 5.1.5 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- `GET /api/dashboard/overview`
- `GET /api/dashboard/pipeline`
- `GET /api/dashboard/metrics`
- `GET /api/dashboard/activity`

#### Milestone 5.2: Activity Logging ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 5.2.1 | Create activity log model | 2 |
| 5.2.2 | Implement logging service | 4 |
| 5.2.3 | Add logging to all endpoints | 8 |
| 5.2.4 | Create activity feed | 4 |
| 5.2.5 | Write unit tests | 4 |
| **Total** | | **22 hours** |

**Deliverables:**
- Comprehensive activity logging
- Activity feed per user
- Event history

#### Milestone 5.3: Charts & Visualizations ⭐
**Estimated Duration:** 3 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 5.3.1 | Create candidates over time endpoint | 4 |
| 5.3.2 | Create email performance endpoint | 4 |
| 5.3.3 | Create hiring funnel endpoint | 4 |
| 5.3.4 | Integrate Recharts | 4 |
| 5.3.5 | Build dashboard UI | 8 |
| **Total** | | **24 hours** |

**Deliverables:**
- Line charts (candidates over time)
- Bar charts (email performance)
- Funnel visualization
- Interactive dashboard

### 6.2 Implementation Order

```
Dashboard API (5.1) → Activity Logging (5.2) → Charts (5.3)
|________________|_____________________|________________|
      Week 13             Week 14               Week 15
```

---

## 7. Epic 6: Billing

**Objective:** Stripe integration for subscriptions, checkout, and billing management.

### 7.1 Milestones

#### Milestone 6.1: Stripe Setup ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 6.1.1 | Create Stripe account and products | 2 |
| 6.1.2 | Set up price IDs in config | 2 |
| 6.1.3 | Create Stripe service | 4 |
| 6.1.4 | Implement webhook handler | 8 |
| 6.1.5 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- Professional ($99/mo) and Agency ($299/mo) plans
- Stripe service integration
- Webhook endpoint

#### Milestone 6.2: Subscription Management ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 6.2.1 | Create subscription model | 2 |
| 6.2.2 | Implement checkout session | 4 |
| 6.2.3 | Implement billing portal | 4 |
| 6.2.4 | Handle plan changes | 4 |
| 6.2.5 | Write unit tests | 4 |
| **Total** | | **18 hours** |

**Deliverables:**
- `POST /api/subscriptions/checkout`
- `POST /api/subscriptions/portal`
- Plan upgrade/downgrade

#### Milestone 6.3: Trial System ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 6.3.1 | Auto-create trial on signup | 4 |
| 6.3.2 | Track trial expiration | 4 |
| 6.3.3 | Show trial banner in UI | 4 |
| 6.3.4 | Implement upgrade flow | 4 |
| 6.3.5 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- 14-day free trial
- Trial expiration handling
- Upgrade prompts

#### Milestone 6.4: Team Billing ⭐
**Estimated Duration:** 2 days  
**Priority:** P1 (High)

| Task | Description | Hours |
|------|-------------|-------|
| 6.4.1 | Create team member model | 2 |
| 6.4.2 | Implement seat tracking | 4 |
| 6.4.3 | Add seat limits to checkout | 4 |
| 6.4.4 | Create invite flow | 6 |
| 6.4.5 | Write unit tests | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- Team seats per plan
- Invitation system
- Role-based access (owner, admin, member)

### 7.2 Implementation Order

```
Stripe Setup (6.1) → Subscription (6.2) → Trial (6.3) → Team Billing (6.4)
|_______________|__________________|_________________|________________|
      Week 5              Week 6             Week 7              Week 8
```

---

## 8. Epic 7: Deployment

**Objective:** Production deployment with Docker, CI/CD, and monitoring.

### 8.1 Milestones

#### Milestone 7.1: Docker Configuration ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 7.1.1 | Create backend Dockerfile | 4 |
| 7.1.2 | Create frontend Dockerfile | 4 |
| 7.1.3 | Create docker-compose.yml | 4 |
| 7.1.4 | Set up nginx configuration | 4 |
| 7.1.5 | Create .env.example | 2 |
| **Total** | | **18 hours** |

**Deliverables:**
- Multi-stage Docker builds
- Development docker-compose
- Production docker-compose
- Nginx reverse proxy

#### Milestone 7.2: CI/CD Pipeline ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 7.2.1 | Create GitHub Actions workflow | 8 |
| 7.2.2 | Add backend tests to CI | 4 |
| 7.2.3 | Add frontend tests to CI | 4 |
| 7.2.4 | Set up Docker build/push | 4 |
| 7.2.5 | Configure deployment trigger | 4 |
| **Total** | | **24 hours** |

**Deliverables:**
- GitHub Actions CI/CD
- Automated testing
- Docker image builds
- Deployment automation

#### Milestone 7.3: Production Infrastructure ⭐
**Estimated Duration:** 3 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 7.3.1 | Set up production database | 4 |
| 7.3.2 | Configure Redis cache | 4 |
| 7.3.3 | Set up file storage (S3/Supabase) | 4 |
| 7.3.4 | Configure environment variables | 4 |
| 7.3.5 | Set up monitoring (Sentry) | 4 |
| **Total** | | **20 hours** |

**Deliverables:**
- Production PostgreSQL
- Redis for caching
- Supabase storage
- Sentry error tracking

#### Milestone 7.4: Security Hardening ⭐
**Estimated Duration:** 2 days  
**Priority:** P0 (Critical)

| Task | Description | Hours |
|------|-------------|-------|
| 7.4.1 | Enable HTTPS/SSL | 4 |
| 7.4.2 | Configure CORS | 2 |
| 7.4.3 | Set up rate limiting | 4 |
| 7.4.4 | Implement security headers | 4 |
| 7.4.5 | Security audit | 4 |
| **Total** | | **18 hours** |

**Deliverables:**
- SSL/TLS encryption
- CORS configuration
- Rate limiting
- Security headers (HSTS, CSP, etc.)

#### Milestone 7.5: Onboarding Flow ⭐
**Estimated Duration:** 2 days  
**Priority:** P2 (Medium)

| Task | Description | Hours |
|------|-------------|-------|
| 7.5.1 | Create onboarding model | 2 |
| 7.5.2 | Implement progress tracking | 4 |
| 7.5.3 | Build onboarding modal UI | 8 |
| 7.5.4 | Add welcome email | 4 |
| 7.5.5 | Write unit tests | 4 |
| **Total** | | **22 hours** |

**Deliverables:**
- 5-step onboarding wizard
- Progress tracking
- Welcome email sequence

### 8.2 Implementation Order

```
Docker (7.1) → CI/CD (7.2) → Infrastructure (7.3) → Security (7.4) → Onboarding (7.5)
|________|______________|_______________|_____________|________________|
   Week 13      Week 14          Week 15          Week 16           Week 16
```

---

## 9. Timeline Overview

```
+==============================================================================+
|                           DEVELOPMENT TIMELINE                                    |
+==============================================================================+

        Week 1    Week 2    Week 3    Week 4    Week 5    Week 6    Week 7    Week 8
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 1  │█████████│█████████│████     │         │         │         │         │
Auth    │  1.1    │  1.2    │ 1.3-4  │         │         │         │         │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 2  │         │         │         │█████████│█████████│█████████│████     │
Cand    │         │         │         │  2.1    │  2.2    │  2.3    │ 2.4     │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 6  │         │         │         │         │█████████│█████████│█████████│
Billing │         │         │         │         │  6.1    │  6.2    │ 6.3-4   │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 3  │         │         │         │         │         │         │         │█████████
AI      │         │         │         │         │         │         │         │  3.1
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 4  │         │         │         │         │         │         │         │█████████
Outreach│         │         │         │         │         │         │         │  4.1
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 3  │█████████│█████████│█████████│█████████│         │         │         │
AI      │  3.1    │  3.2    │  3.3    │  3.4    │         │         │         │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 4  │█████████│█████████│█████████│█████████│         │         │         │
Outreach│  4.1    │  4.2    │  4.3    │  4.4    │         │         │         │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 5  │         │         │         │         │█████████│█████████│█████████│
Analytics         │         │         │         │  5.1    │  5.2    │  5.3    │
        ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Epic 7  │         │         │         │         │█████████│█████████│█████████│█████████
Deploy  │         │         │         │         │  7.1    │  7.2    │  7.3-4  │ 7.5
        └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘

LEGEND: ████ = Active development
```

---

## 10. Milestone Summary

### Total Estimated Hours

| Epic | Milestones | Total Hours |
|------|-----------|------------|
| Epic 1: Authentication | 4 | 57 hours |
| Epic 2: Candidate Management | 4 | 72 hours |
| Epic 3: AI Scoring | 4 | 94 hours |
| Epic 4: Outreach | 4 | 90 hours |
| Epic 5: Analytics | 3 | 66 hours |
| Epic 6: Billing | 4 | 78 hours |
| Epic 7: Deployment | 5 | 102 hours |
| **TOTAL** | **28** | **559 hours** |

### Milestone Priority Order

| Priority | Milestone | Epic | Hours |
|----------|-----------|------|-------|
| P0 | Auth Core | 1 | 33 hours |
| P0 | Candidate CRUD | 2 | 28 hours |
| P0 | Resume Upload | 2 | 40 hours |
| P0 | AI Service | 3 | 32 hours |
| P0 | Scoring API | 3 | 18 hours |
| P0 | Email Templates | 4 | 22 hours |
| P0 | Email Sending | 4 | 24 hours |
| P0 | Bulk Email | 4 | 24 hours |
| P0 | Stripe Setup | 6 | 20 hours |
| P0 | Subscription | 6 | 18 hours |
| P0 | Trial System | 6 | 20 hours |
| P0 | Docker Config | 7 | 18 hours |
| P0 | CI/CD | 7 | 24 hours |
| P0 | Infrastructure | 7 | 20 hours |
| P0 | Security | 7 | 18 hours |
| P1 | Search & Filtering | 2 | 16 hours |
| P1 | Pipeline Status | 2 | 8 hours |
| P1 | Bulk Scoring | 3 | 20 hours |
| P1 | Resume Summaries | 3 | 24 hours |
| P1 | Email Tracking | 4 | 24 hours |
| P1 | Dashboard API | 5 | 20 hours |
| P1 | Activity Logging | 5 | 22 hours |
| P1 | Charts | 5 | 24 hours |
| P1 | Team Billing | 6 | 20 hours |
| P2 | Password Reset | 1 | 16 hours |
| P2 | User Profile | 1 | 8 hours |
| P2 | Onboarding | 7 | 22 hours |

### Phase Summary

| Phase | Duration | Milestones | Deliverables |
|-------|---------|-----------|--------------|
| **Phase 1: Foundation** | Weeks 1-4 | 8 | Auth, Core API, Docker |
| **Phase 2: Core Features** | Weeks 5-8 | 8 | Candidates, Jobs, Billing |
| **Phase 3: AI & Outreach** | Weeks 9-12 | 8 | AI Scoring, Email |
| **Phase 4: Polish & Launch** | Weeks 13-16 | 4 | Analytics, Security, Deploy |

---

## Appendix A: Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-------------|
| OpenAI API changes | Medium | Medium | Abstract behind service layer |
| Stripe integration issues | Low | High | Use Stripe SDK, test thoroughly |
| Database performance | Medium | High | Add indexes, use connection pooling |
| Email deliverability | Medium | Medium | SPF/DKIM/DMARC setup |
| Team scope creep | High | Medium | Strict milestone boundaries |

---

## Appendix B: Dependencies

```
Auth (1) ─────┬────> Everything
                │
Candidate CRUD (2.1) ──> Resume Upload (2.2)
                │
Resume Upload (2.2) ──> AI Scoring (3.1)
                │
Templates (4.1) ────> Email Sending (4.2) ──> Bulk Email (4.3)
                                   │
                                   └──> Email Tracking (4.4)
```

---

*End of Roadmap Document*
