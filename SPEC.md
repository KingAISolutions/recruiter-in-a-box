# Recruiter In A Box - Product Specification

## 1. Project Overview

**Project Name:** Recruiter In A Box  
**Project Type:** AI-Powered SaaS Recruitment Platform  
**Core Functionality:** An intelligent recruitment platform that automates candidate sourcing, scoring, and outreach using AI.  
**Target Users:** HR professionals, recruiters, hiring managers, and small to medium businesses.

### Product Positioning
- **Tagline:** Hire Top Talent 10x Faster
- **Problem:** Hiring takes too much time (avg 44 days to hire)
- **Solution:** AI-powered automation for candidate scoring, outreach, and pipeline management

### Pricing Tiers
| Plan | Price | Target |
|------|-------|--------|
| Professional | $99/month | Individual recruiters |
| Agency | $299/month | Recruiting teams (5 seats) |

### Landing Page Features
- Hero section with clear value proposition
- Problem/solution framing
- Feature highlights
- How it works (3-step process)
- Pricing section with comparison
- Customer testimonials
- CTA for free trial signup

## 2. Tech Stack

### Frontend
- React 18 with TypeScript
- Vite (Build Tool)
- Tailwind CSS (Styling)
- React Router (Navigation)
- React Query (Server State Management)
- React Hook Form (Form Handling)
- Zod (Validation)

### Backend
- Python FastAPI
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- python-jose (JWT)
- passlib (Password Hashing)
- PyPDF2 / pdfplumber (PDF Parsing)
- openai (AI Integration)
- python-multipart (File Upload)

### Database & Services
- Supabase (PostgreSQL, Auth, Storage)
- OpenAI API (AI Scoring)

### Deployment
- Docker & Docker Compose
- Environment Variables Management

## 3. Feature Specifications

### 3.1 Authentication System
- **Signup:** Email/password registration with email verification
- **Login:** JWT-based authentication with refresh tokens
- **Password Reset:** Email-based password reset flow
- **Session Management:** Secure session handling with logout
- **Protected Routes:** Middleware for route protection

### 3.2 Resume Management
- **PDF Upload:** Drag-and-drop resume upload with progress indicator
- **Resume Parsing:** Extract name, email, phone, skills, experience, education
- **Candidate Profiles:** CRUD operations for candidates
- **Search & Filter:** Search candidates by name, skills, status
- **Bulk Import:** Upload multiple resumes at once

### 3.3 AI Candidate Scoring
- **Skills Match:** Score 0-100 based on required skills vs. candidate skills
- **Experience Match:** Evaluate years of experience against requirements
- **Education Match:** Assess education level and relevance
- **Overall Score:** Weighted composite score (Skills 40%, Experience 35%, Education 25%)
- **Scoring History:** Track score changes over time

### 3.4 Outreach Management
- **Email Templates:** Create, edit, delete email templates with variables
- **Template Variables:** {candidate_name}, {position}, {company_name}, etc.
- **Bulk Email:** Send personalized emails to multiple candidates
- **Email Tracking:** Track sent, opened, replied, failed status
- **Email Scheduling:** Schedule emails for future delivery

### 3.5 Dashboard
- **Analytics Overview:** Total candidates, active jobs, response rates
- **Pipeline View:** Visual Kanban board of candidate stages
- **Hiring Metrics:** Time-to-hire, cost-per-hire, offer acceptance rate
- **Recent Activity:** Latest actions and notifications
- **Charts:** Bar charts, line graphs, pie charts for metrics

### 3.6 Interview Scheduling
- **Schedule Interviews:** Create interview appointments with candidates
- **Interview Types:** Phone, video, on-site, technical
- **Calendar Integration:** Add meeting links (Zoom, Google Meet)
- **Interview Feedback:** Record notes, ratings, and feedback after interviews
- **Status Tracking:** Scheduled, confirmed, completed, canceled

### 3.7 Team Management (Agency Plan)
- **Team Invitations:** Invite team members via email
- **Role Management:** Owner, admin, member roles with permissions
- **Seat Management:** Track seat usage vs. plan limits
- **Collaborative Access:** Multiple users can access same candidates and jobs

### 3.8 Subscription & Billing
- **Stripe Integration:** Accept payments via Stripe Checkout
- **Plan Management:** Upgrade, downgrade, or cancel subscriptions
- **Billing Portal:** Self-service portal for payment methods
- **Usage Limits:** Enforce candidate/month limits per plan

### 3.9 User Onboarding
- **Welcome Flow:** Step-by-step setup wizard
- **Progress Tracking:** Track completion of onboarding steps
- **Feature Tour:** Interactive product tour for new users
- **Trial System:** 14-day free trial with reminders

### 3.10 Email Open/Click Tracking
- **Tracking Pixels:** Track email opens via 1x1 pixel images
- **Click Tracking:** Track links clicked in emails
- **Analytics:** View open rates, click rates per campaign

### 3.11 AI Resume Summaries
- **Auto-Generate:** Create summaries from resume content
- **Key Strengths:** Extract top 5 candidate strengths
- **Concerns:** Identify potential red flags
- **Next Steps:** AI-powered recommendations

### 3.6 Database Schema

```
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE)
├── password_hash (VARCHAR)
├── full_name (VARCHAR)
├── company_name (VARCHAR)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
└── email_verified (BOOLEAN)

candidates
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── full_name (VARCHAR)
├── email (VARCHAR)
├── phone (VARCHAR)
├── resume_url (VARCHAR)
├── resume_text (TEXT)
├── skills (JSONB)
├── experience_years (INTEGER)
├── education_level (VARCHAR)
├── current_position (VARCHAR)
├── current_company (VARCHAR)
├── linkedin_url (VARCHAR)
├── status (VARCHAR) -- new, screening, interview, offer, hired, rejected
├── source (VARCHAR)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

job_positions
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── title (VARCHAR)
├── description (TEXT)
├── requirements (JSONB)
├── department (VARCHAR)
├── location (VARCHAR)
├── salary_range (VARCHAR)
├── status (VARCHAR) -- open, closed, on_hold
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

candidate_scores
├── id (UUID, PK)
├── candidate_id (UUID, FK -> candidates)
├── job_position_id (UUID, FK -> job_positions)
├── skills_score (INTEGER)
├── experience_score (INTEGER)
├── education_score (INTEGER)
├── overall_score (INTEGER)
├── breakdown (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

email_templates
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── name (VARCHAR)
├── subject (VARCHAR)
├── body (TEXT)
├── variables (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

sent_emails
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── candidate_id (UUID, FK -> candidates)
├── template_id (UUID, FK -> email_templates)
├── job_position_id (UUID, FK -> job_positions)
├── subject (VARCHAR)
├── body (TEXT)
├── status (VARCHAR) -- pending, sent, delivered, opened, replied, failed
├── sent_at (TIMESTAMP)
├── delivered_at (TIMESTAMP)
├── opened_at (TIMESTAMP)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

activity_logs
├── id (UUID, PK)
├── user_id (UUID, FK -> users)
├── action (VARCHAR)
├── entity_type (VARCHAR)
├── entity_id (UUID)
├── details (JSONB)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## 4. API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/reset-password/confirm` - Confirm password reset
- `GET /api/auth/me` - Get current user

### Candidates
- `GET /api/candidates` - List candidates (with pagination, filters)
- `POST /api/candidates` - Create candidate
- `GET /api/candidates/:id` - Get candidate details
- `PUT /api/candidates/:id` - Update candidate
- `DELETE /api/candidates/:id` - Delete candidate
- `POST /api/candidates/upload` - Upload resume PDF
- `POST /api/candidates/parse` - Parse resume content
- `PUT /api/candidates/:id/status` - Update candidate status

### Job Positions
- `GET /api/jobs` - List job positions
- `POST /api/jobs` - Create job position
- `GET /api/jobs/:id` - Get job details
- `PUT /api/jobs/:id` - Update job position
- `DELETE /api/jobs/:id` - Delete job position

### AI Scoring
- `POST /api/scoring/candidate/:id` - Score single candidate
- `POST /api/scoring/bulk` - Bulk score candidates
- `GET /api/scoring/:candidateId/history` - Get scoring history

### Email Templates
- `GET /api/templates` - List email templates
- `POST /api/templates` - Create template
- `GET /api/templates/:id` - Get template
- `PUT /api/templates/:id` - Update template
- `DELETE /api/templates/:id` - Delete template

### Outreach
- `POST /api/outreach/send` - Send single email
- `POST /api/outreach/bulk` - Bulk send emails
- `GET /api/outreach/emails` - List sent emails
- `GET /api/outreach/emails/:id` - Get email details
- `GET /api/outreach/stats` - Get email statistics

### Dashboard
- `GET /api/dashboard/overview` - Get dashboard overview
- `GET /api/dashboard/pipeline` - Get pipeline data
- `GET /api/dashboard/metrics` - Get hiring metrics
- `GET /api/dashboard/activity` - Get recent activity

## 5. Project Structure

```
recruiter-in-a-box/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── auth/
│   │   │   ├── candidates/
│   │   │   ├── dashboard/
│   │   │   ├── email/
│   │   │   └── layout/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── candidates/
│   │   │   ├── jobs/
│   │   │   ├── scoring/
│   │   │   ├── templates/
│   │   │   ├── outreach/
│   │   │   └── dashboard/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
├── .env.example
├── README.md
└── SPEC.md
```

## 6. Security Considerations

- JWT tokens with short expiration (15 minutes access, 7 days refresh)
- Password hashing with bcrypt
- Input validation with Pydantic/Zod
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention with React's built-in escaping
- CORS configuration for API
- Rate limiting on auth endpoints
- Secure file upload with type validation

## 7. Acceptance Criteria

### Authentication
- [ ] User can sign up with email/password
- [ ] User receives email verification (simulated in dev)
- [ ] User can log in and receive JWT tokens
- [ ] User can request password reset
- [ ] Protected routes redirect to login

### Resume Management
- [ ] User can upload PDF resumes
- [ ] Resume content is parsed and stored
- [ ] Candidate profiles display all extracted data
- [ ] User can search and filter candidates
- [ ] User can update candidate status

### AI Scoring
- [ ] User can score candidates against job requirements
- [ ] Scores include skills, experience, education breakdown
- [ ] Overall score is calculated with proper weights
- [ ] Scoring history is maintained

### Outreach
- [ ] User can create email templates with variables
- [ ] User can send bulk personalized emails
- [ ] Email status is tracked (sent, delivered, opened)
- [ ] User can view email statistics

### Dashboard
- [ ] Dashboard shows key metrics
- [ ] Pipeline view displays candidates by stage
- [ ] Charts visualize hiring trends
- [ ] Recent activity is displayed

### Deployment
- [ ] Application runs in Docker containers
- [ ] Environment variables are properly configured
- [ ] Database migrations run on startup
- [ ] Production build completes successfully
