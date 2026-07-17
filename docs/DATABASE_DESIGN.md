# Recruiter In A Box - Database Design Document

**Version:** 1.0  
**Last Updated:** 2026-07-16  
**Database:** PostgreSQL (via Supabase)  
**Status:** Complete

---

## Table of Contents

1. [Entity Relationship Diagram](#1-entity-relationship-diagram)
2. [Table Definitions](#2-table-definitions)
3. [Relationships](#3-relationships)
4. [Indexing Strategy](#4-indexing-strategy)
5. [Row-Level Security Policies](#5-row-level-security-policies)
6. [Supabase Implementation](#6-supabase-implementation)
7. [Migration Scripts](#7-migration-scripts)

---

## 1. Entity Relationship Diagram

### 1.1 Full ERD

```
+==============================================================================+
|                              COMPLETE DATABASE SCHEMA                           |
+==============================================================================+

                                    +---------------------+
                                    |       USERS         |
                                    +---------------------+
                                    | id (PK, UUID)      |
                                    | email (UNIQUE)     |-------------------------+
                                    | password_hash      |                         |
                                    | full_name          |                         |
                                    | company_name       |                         |
                                    | email_verified     |                         |
                                    | created_at        |                         |
                                    | updated_at        |                         |
                                    +----------+----------+                         |
                                               |                                  |
                          +----------------------+----------------------+            |
                          |                      |                      |            |
                          v                      v                      v            |
        +-----------------------+  +-----------------------+  +-------------------+  |
        |    SUBSCRIPTIONS      |  |      CANDIDATES       |  |   JOB_POSITIONS   |  |
        +-----------------------+  +-----------------------+  +-------------------+  |
        | id (PK, UUID)        |  | id (PK, UUID)        |  | id (PK, UUID)    |  |
        | user_id (FK) --------|->| user_id (FK)         |  | user_id (FK) -----|->|
        | stripe_customer_id    |  | full_name            |  | title            |  |
        | stripe_subscription_id |  | email                |  | description       |  |
        | plan_type            |  | phone                |  | requirements (JSON)| |
        | status               |  | resume_url           |  | department        |  |
        | current_period_start |  | resume_text (TEXT)  |  | location          |  |
        | current_period_end   |  | skills (JSON)       |  | salary_range      |  |
        | trial_end            |  | experience_years     |  | status           |  |
        | cancel_at_period_end |  | education_level     |  | created_at       |  |
        +----------+------------+  | current_position     |  | updated_at       |  |
                 |               | current_company      |  +-------------------+  |
                 |               | linkedin_url        |           |           |
                 |               | status              |           |           |
                 |               | source              |           |           |
                 |               | notes               |           |           |
                 |               | created_at          |           |           |
                 |               | updated_at          |           |           |
                 |               +----------+----------+           |           |
                 |                          |                  |           |
                 |         +---------------+------------------+           |
                 |         |               |                              |
                 v         v               v                              v
        +-----------------------+  +-----------------------+  +-------------------+
        |    TEAM_MEMBERS       |  |   CANDIDATE_SCORES  |  |   SENT_EMAILS   |
        +-----------------------+  +-----------------------+  +-------------------+
        | id (PK, UUID)        |  | id (PK, UUID)        |  | id (PK, UUID)   |
        | subscription_id (FK) |  | candidate_id (FK)   |  | user_id (FK)    |
        | email                |  | job_position_id (FK) |  | candidate_id(FK)--+
        | name                 |  | skills_score        |  | template_id(FK)  |
        | role                 |  | experience_score     |  | job_position_id  |
        | status               |  | education_score     |  | subject          |
        | invite_token         |  | overall_score       |  | body             |
        | invited_at           |  | breakdown (JSON)    |  | status           |
        | joined_at            |  | created_at          |  | sent_at          |
        | last_active_at       |  +-----------------------+  | delivered_at     |
        +-----------------------+                            | opened_at        |
                                                          | replied_at       |
                                                          +--------+----------+
                                                                   |
                                    +--------------------------------+
                                    |                                |
                                    v                                v
                        +-----------------------+      +-----------------------+
                        |   EMAIL_TEMPLATES     |      |     INTERVIEWS      |
                        +-----------------------+      +-----------------------+
                        | id (PK, UUID)        |      | id (PK, UUID)        |
                        | user_id (FK)         |      | candidate_id (FK) --|--+
                        | name                 |      | user_id (FK)         |  |
                        | subject              |      | job_position_id (FK) |  |
                        | body (TEXT)          |      | title                |  |
                        | variables (JSON)     |      | interview_type       |  |
                        | created_at          |      | scheduled_at         |  |
                        | updated_at          |      | duration_minutes     |  |
                        +-----------------------+      | location             |  |
                                                      | status               |  |
                                                      | notes                |  |
                                                      | feedback             |  |
                                                      | rating (1-5)        |  |
                                                      +-----------------------+


        +-----------------------+      +-----------------------+      +-------------------+
        |  ONBOARDING_PROGRESS |      |   EMAIL_TRACKING    |      | RESUME_SUMMARIES |
        +-----------------------+      +-----------------------+      +-------------------+
        | id (PK, UUID)        |      | id (PK, UUID)        |      | id (PK, UUID)    |
        | user_id (FK) --------|->   | sent_email_id (FK)  |--+   | candidate_id(FK)--|-+
        | step_profile_completed|      | user_id (FK)        |  |   | user_id (FK)     |  |
        | step_first_job       |      | tracking_id (UNIQUE)|  |   | summary           |  |
        | step_first_candidate |      | ip_address          |  |   | key_strengths(JSON)| |
        | step_first_email     |      | user_agent          |  |   | concerns (JSON)   |  |
        | step_integration     |      | opened              |  |   | next_steps (JSON)  |  |
        | current_step         |      | opened_at           |  |   | model_used        |  |
        | tour_completed       |      | click_count         |  |   | tokens_used       |  |
        | tour_dismissed_at    |      | links_clicked (JSON)|  |   | cost_usd          |  |
        +-----------------------+      +-----------------------+  |   | created_at        |
                                                              +-----------------------+
        +-----------------------+
        |    ACTIVITY_LOGS      |
        +-----------------------+
        | id (PK, UUID)        |
        | user_id (FK)         |------------------+
        | candidate_id (FK)    |                  |
        | action               |                  |
        | entity_type         |                  |
        | entity_id (UUID)    |                  |
        | details (JSON)      |                  |
        | created_at          |                  |
        +-----------------------+                  |
                                                      |
                                    +---------------+
                                    |               |
                                    v               v
                            +-----------+   +-----------+
                            | SUPABASE  |   |  AUDIT    |
                            | AUTH      |   |  TRAIL     |
                            | USERS     |   |           |
                            +-----------+   +-----------+
```

### 1.2 Core Entity Relationships

```
USERS (1) ----< (N) CANDIDATES
USERS (1) ----< (N) JOB_POSITIONS
USERS (1) ----< (N) EMAIL_TEMPLATES
USERS (1) ----< (N) SENT_EMAILS
USERS (1) ----< (N) INTERVIEWS
USERS (1) ----< (1) SUBSCRIPTIONS
USERS (1) ----< (1) ONBOARDING_PROGRESS

SUBSCRIPTIONS (1) ----< (N) TEAM_MEMBERS

CANDIDATES (1) ----< (N) CANDIDATE_SCORES
CANDIDATES (1) ----< (N) SENT_EMAILS
CANDIDATES (1) ----< (N) INTERVIEWS
CANDIDATES (1) ----< (1) RESUME_SUMMARIES

JOB_POSITIONS (1) ----< (N) CANDIDATE_SCORES
JOB_POSITIONS (1) ----< (N) INTERVIEWS

EMAIL_TEMPLATES (1) ----< (N) SENT_EMAILS

SENT_EMAILS (1) ----< (N) EMAIL_TRACKING
```

---

## 2. Table Definitions

### 2.1 Core Tables

#### 2.1.1 Users Table

```sql
-- ============================================================
-- TABLE: users
-- DESCRIPTION: Core user accounts with authentication data
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    
    -- Verification
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_password_length CHECK (char_length(password_hash) >= 60)
);

-- Comments
COMMENT ON TABLE users IS 'Core user accounts with authentication and profile data';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password with cost factor 12';
COMMENT ON COLUMN users.email_verified IS 'Email verification status for new signups';
```

#### 2.1.2 Candidates Table

```sql
-- ============================================================
-- TABLE: candidates
-- DESCRIPTION: Job seeker profiles with parsed resume data
-- ============================================================

CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Contact Info
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    
    -- Resume Data
    resume_url VARCHAR(500),
    resume_text TEXT,
    
    -- Parsed Data
    skills JSONB DEFAULT '[]'::jsonb,
    experience_years INTEGER DEFAULT 0,
    education_level VARCHAR(100),
    current_position VARCHAR(255),
    current_company VARCHAR(255),
    
    -- Pipeline Status
    status VARCHAR(50) NOT NULL DEFAULT 'new' 
        CHECK (status IN ('new', 'screening', 'interview', 'offer', 'hired', 'rejected')),
    
    -- Source tracking
    source VARCHAR(100),
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes (see Section 4)
-- Comments
COMMENT ON TABLE candidates IS 'Job seeker profiles with parsed resume data';
COMMENT ON COLUMN candidates.skills IS 'Array of extracted skills from resume';
COMMENT ON COLUMN candidates.status IS 'Pipeline stage: new > screening > interview > offer > hired/rejected';
```

#### 2.1.3 Job Positions Table

```sql
-- ============================================================
-- TABLE: job_positions
-- DESCRIPTION: Open job positions/requisitions
-- ============================================================

CREATE TABLE job_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Position Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirements JSONB DEFAULT '{}'::jsonb,
    department VARCHAR(100),
    location VARCHAR(255),
    salary_range VARCHAR(100),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'closed', 'on_hold')),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE job_positions IS 'Open job positions and requisitions';
COMMENT ON COLUMN job_positions.requirements IS 'JSON with required_skills, preferred_skills, min_experience, education';
```

### 2.2 Scoring Tables

#### 2.2.1 Candidate Scores Table

```sql
-- ============================================================
-- TABLE: candidate_scores
-- DESCRIPTION: AI-generated candidate evaluation scores
-- ============================================================

CREATE TABLE candidate_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_position_id UUID REFERENCES job_positions(id) ON DELETE SET NULL,
    
    -- Scores (0-100 scale)
    skills_score INTEGER NOT NULL DEFAULT 0 CHECK (skills_score >= 0 AND skills_score <= 100),
    experience_score INTEGER NOT NULL DEFAULT 0 CHECK (experience_score >= 0 AND experience_score <= 100),
    education_score INTEGER NOT NULL DEFAULT 0 CHECK (education_score >= 0 AND education_score <= 100),
    overall_score INTEGER NOT NULL DEFAULT 0 CHECK (overall_score >= 0 AND overall_score <= 100),
    
    -- Detailed Breakdown
    breakdown JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure one score per candidate-job pair
    UNIQUE(candidate_id, job_position_id)
);

COMMENT ON TABLE candidate_scores IS 'AI-generated candidate evaluation scores against job requirements';
COMMENT ON COLUMN candidate_scores.breakdown IS 'Detailed scoring breakdown with matched skills, gaps, etc.';
```

#### 2.2.2 Resume Summaries Table

```sql
-- ============================================================
-- TABLE: resume_summaries
-- DESCRIPTION: AI-generated resume summaries and insights
-- ============================================================

CREATE TABLE resume_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    candidate_id UUID NOT NULL UNIQUE REFERENCES candidates(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- AI Generated Content
    summary TEXT,
    key_strengths JSONB DEFAULT '[]'::jsonb,
    potential_concerns JSONB DEFAULT '[]'::jsonb,
    recommended_next_steps JSONB DEFAULT '[]'::jsonb,
    
    -- Usage Metadata
    model_used VARCHAR(100),
    tokens_used INTEGER,
    cost_usd INTEGER,  -- Cost in cents
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE resume_summaries IS 'AI-generated summaries and insights from resume parsing';
```

### 2.3 Communication Tables

#### 2.3.1 Email Templates Table

```sql
-- ============================================================
-- TABLE: email_templates
-- DESCRIPTION: Reusable email templates with variable interpolation
-- ============================================================

CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Template Content
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    
    -- Variable definitions
    variables JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE email_templates IS 'Reusable email templates for outreach campaigns';
COMMENT ON COLUMN email_templates.variables IS 'Array of variable names used in template';
```

#### 2.3.2 Sent Emails Table

```sql
-- ============================================================
-- TABLE: sent_emails
-- DESCRIPTION: Email history with tracking status
-- ============================================================

CREATE TABLE sent_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Relationships
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    template_id UUID REFERENCES email_templates(id) ON DELETE SET NULL,
    job_position_id UUID REFERENCES job_positions(id) ON DELETE SET NULL,
    
    -- Email Content
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    
    -- Tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'sent', 'delivered', 'opened', 'replied', 'failed', 'bounced')),
    
    -- Timestamps
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    error_message TEXT,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sent_emails IS 'Email history with delivery and engagement tracking';
```

#### 2.3.3 Email Tracking Table

```sql
-- ============================================================
-- TABLE: email_tracking
-- DESCRIPTION: Individual email open and click events
-- ============================================================

CREATE TABLE email_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    sent_email_id UUID NOT NULL REFERENCES sent_emails(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique tracking identifier
    tracking_id VARCHAR(255) NOT NULL UNIQUE,
    
    -- Client Info
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- Events
    opened BOOLEAN NOT NULL DEFAULT FALSE,
    opened_at TIMESTAMPTZ,
    click_count INTEGER NOT NULL DEFAULT 0,
    links_clicked JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE email_tracking IS 'Individual email tracking events for analytics';
```

### 2.4 SaaS Tables

#### 2.4.1 Subscriptions Table

```sql
-- ============================================================
-- TABLE: subscriptions
-- DESCRIPTION: User subscription and billing information
-- ============================================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Stripe Integration
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    
    -- Plan Info
    plan_type VARCHAR(50) NOT NULL DEFAULT 'trial'
        CHECK (plan_type IN ('trial', 'professional', 'agency')),
    status VARCHAR(50) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete')),
    
    -- Billing Period
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE subscriptions IS 'User subscription and billing information from Stripe';
```

#### 2.4.2 Team Members Table

```sql
-- ============================================================
-- TABLE: team_members
-- DESCRIPTION: Team collaboration with role-based access
-- ============================================================

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    
    -- Member Info
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'member'
        CHECK (role IN ('owner', 'admin', 'member')),
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'removed')),
    
    -- Invitation
    invite_token VARCHAR(255),
    invited_at TIMESTAMPTZ,
    joined_at TIMESTAMPTZ,
    last_active_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT team_members_unique_email_per_subscription UNIQUE (subscription_id, email)
);

COMMENT ON TABLE team_members IS 'Team collaboration with role-based access control';
COMMENT ON COLUMN team_members.role IS 'Owner (1 per subscription), Admin (can manage team), Member (standard access)';
```

#### 2.4.3 Interviews Table

```sql
-- ============================================================
-- TABLE: interviews
-- DESCRIPTION: Interview scheduling and feedback
-- ============================================================

CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_position_id UUID REFERENCES job_positions(id) ON DELETE SET NULL,
    
    -- Interview Details
    title VARCHAR(255),
    interview_type VARCHAR(50) DEFAULT 'video'
        CHECK (interview_type IN ('phone', 'video', 'onsite', 'technical')),
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    location VARCHAR(255),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'confirmed', 'completed', 'canceled', 'rescheduled')),
    
    -- Feedback
    notes TEXT,
    feedback TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    -- Calendar Integration
    calendar_event_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE interviews IS 'Interview scheduling with feedback and ratings';
```

#### 2.4.4 Onboarding Progress Table

```sql
-- ============================================================
-- TABLE: onboarding_progress
-- DESCRIPTION: User onboarding step tracking
-- ============================================================

CREATE TABLE onboarding_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Step Completion Flags
    step_profile_completed BOOLEAN NOT NULL DEFAULT FALSE,
    step_first_job_completed BOOLEAN NOT NULL DEFAULT FALSE,
    step_first_candidate_completed BOOLEAN NOT NULL DEFAULT FALSE,
    step_first_email_completed BOOLEAN NOT NULL DEFAULT FALSE,
    step_integration_completed BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Progress Tracking
    current_step INTEGER NOT NULL DEFAULT 1,
    total_steps INTEGER NOT NULL DEFAULT 5,
    
    -- Tour Status
    tour_completed BOOLEAN NOT NULL DEFAULT FALSE,
    tour_dismissed_at TIMESTAMPTZ,
    
    -- Welcome Email
    welcome_email_sent BOOLEAN NOT NULL DEFAULT FALSE,
    welcome_email_sent_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE onboarding_progress IS 'User onboarding step completion tracking';
```

### 2.5 Utility Tables

#### 2.5.1 Activity Logs Table

```sql
-- ============================================================
-- TABLE: activity_logs
-- DESCRIPTION: Audit trail for user actions
-- ============================================================

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationships
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
    
    -- Activity Info
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    details JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE activity_logs IS 'Audit trail for user actions and system events';
```

---

## 3. Relationships

### 3.1 Relationship Definitions

| Parent Table | Child Table | Relationship Type | Foreign Key | Cascade |
|--------------|------------|------------------|------------|---------|
| `users` | `candidates` | 1:N | `user_id` | CASCADE |
| `users` | `job_positions` | 1:N | `user_id` | CASCADE |
| `users` | `email_templates` | 1:N | `user_id` | CASCADE |
| `users` | `sent_emails` | 1:N | `user_id` | CASCADE |
| `users` | `interviews` | 1:N | `user_id` | CASCADE |
| `users` | `subscriptions` | 1:1 | `user_id` | CASCADE |
| `users` | `onboarding_progress` | 1:1 | `user_id` | CASCADE |
| `subscriptions` | `team_members` | 1:N | `subscription_id` | CASCADE |
| `candidates` | `candidate_scores` | 1:N | `candidate_id` | CASCADE |
| `candidates` | `sent_emails` | 1:N | `candidate_id` | CASCADE |
| `candidates` | `interviews` | 1:N | `candidate_id` | CASCADE |
| `candidates` | `resume_summaries` | 1:1 | `candidate_id` | CASCADE |
| `job_positions` | `candidate_scores` | 1:N | `job_position_id` | SET NULL |
| `job_positions` | `interviews` | 1:N | `job_position_id` | SET NULL |
| `email_templates` | `sent_emails` | 1:N | `template_id` | SET NULL |
| `sent_emails` | `email_tracking` | 1:N | `sent_email_id` | CASCADE |

### 3.2 Foreign Key Constraints

```sql
-- Users to Candidates
ALTER TABLE candidates
ADD CONSTRAINT candidates_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Users to Job Positions
ALTER TABLE job_positions
ADD CONSTRAINT job_positions_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Candidate Scores
ALTER TABLE candidate_scores
ADD CONSTRAINT candidate_scores_candidate_id_fkey
FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE candidate_scores
ADD CONSTRAINT candidate_scores_job_position_id_fkey
FOREIGN KEY (job_position_id) REFERENCES job_positions(id) ON DELETE SET NULL;

-- Sent Emails
ALTER TABLE sent_emails
ADD CONSTRAINT sent_emails_candidate_id_fkey
FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE sent_emails
ADD CONSTRAINT sent_emails_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE sent_emails
ADD CONSTRAINT sent_emails_template_id_fkey
FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE SET NULL;

-- Subscriptions
ALTER TABLE subscriptions
ADD CONSTRAINT subscriptions_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Team Members
ALTER TABLE team_members
ADD CONSTRAINT team_members_subscription_id_fkey
FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE;

-- Interviews
ALTER TABLE interviews
ADD CONSTRAINT interviews_candidate_id_fkey
FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE interviews
ADD CONSTRAINT interviews_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE interviews
ADD CONSTRAINT interviews_job_position_id_fkey
FOREIGN KEY (job_position_id) REFERENCES job_positions(id) ON DELETE SET NULL;

-- Onboarding Progress
ALTER TABLE onboarding_progress
ADD CONSTRAINT onboarding_progress_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Email Tracking
ALTER TABLE email_tracking
ADD CONSTRAINT email_tracking_sent_email_id_fkey
FOREIGN KEY (sent_email_id) REFERENCES sent_emails(id) ON DELETE CASCADE;

ALTER TABLE email_tracking
ADD CONSTRAINT email_tracking_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Resume Summaries
ALTER TABLE resume_summaries
ADD CONSTRAINT resume_summaries_candidate_id_fkey
FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE;

ALTER TABLE resume_summaries
ADD CONSTRAINT resume_summaries_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

---

## 4. Indexing Strategy

### 4.1 Primary Indexes (Auto-created)

All primary keys automatically have B-tree indexes created.

### 4.2 Foreign Key Indexes

```sql
-- High-usage foreign keys for JOIN performance
CREATE INDEX idx_candidates_user_id ON candidates(user_id);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_created_at ON candidates(created_at);

CREATE INDEX idx_job_positions_user_id ON job_positions(user_id);
CREATE INDEX idx_job_positions_status ON job_positions(status);

CREATE INDEX idx_sent_emails_user_id ON sent_emails(user_id);
CREATE INDEX idx_sent_emails_candidate_id ON sent_emails(candidate_id);
CREATE INDEX idx_sent_emails_status ON sent_emails(status);
CREATE INDEX idx_sent_emails_sent_at ON sent_emails(sent_at);

CREATE INDEX idx_candidate_scores_candidate_id ON candidate_scores(candidate_id);
CREATE INDEX idx_candidate_scores_job_position_id ON candidate_scores(job_position_id);

CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_user_id ON interviews(user_id);
CREATE INDEX idx_interviews_scheduled_at ON interviews(scheduled_at);
CREATE INDEX idx_interviews_status ON interviews(status);

CREATE INDEX idx_email_templates_user_id ON email_templates(user_id);

CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);

CREATE INDEX idx_team_members_subscription_id ON team_members(subscription_id);
CREATE INDEX idx_team_members_email ON team_members(email);
```

### 4.3 Composite Indexes

```sql
-- Candidate lookup by user and status
CREATE INDEX idx_candidates_user_status ON candidates(user_id, status);

-- Sent emails by user and date
CREATE INDEX idx_sent_emails_user_sent ON sent_emails(user_id, sent_at DESC);

-- Interviews by user and date
CREATE INDEX idx_interviews_user_scheduled ON interviews(user_id, scheduled_at ASC);

-- Activity logs for user timeline
CREATE INDEX idx_activity_logs_user_created ON activity_logs(user_id, created_at DESC);

-- Candidate scores for ranking
CREATE INDEX idx_candidate_scores_overall ON candidate_scores(candidate_id, overall_score DESC);
```

### 4.4 Partial Indexes

```sql
-- Active candidates only
CREATE INDEX idx_candidates_active ON candidates(user_id, created_at DESC)
WHERE status NOT IN ('hired', 'rejected');

-- Open jobs only
CREATE INDEX idx_job_positions_open ON job_positions(user_id, created_at DESC)
WHERE status = 'open';

-- Undelivered emails (for retry processing)
CREATE INDEX idx_sent_emails_pending ON sent_emails(user_id, created_at ASC)
WHERE status IN ('pending', 'failed');

-- Upcoming interviews
CREATE INDEX idx_interviews_upcoming ON interviews(user_id, scheduled_at ASC)
WHERE status IN ('scheduled', 'confirmed') AND scheduled_at > NOW();

-- Open team invitations
CREATE INDEX idx_team_members_pending ON team_members(subscription_id, invited_at DESC)
WHERE status = 'pending';
```

### 4.5 Full-Text Search Indexes

```sql
-- Candidate full-text search
CREATE INDEX idx_candidates_resume_fts ON candidates
USING GIN (to_tsvector('english', coalesce(resume_text, '') || ' ' || full_name || ' ' || COALESCE(skills::text, '')));

-- Job position full-text search
CREATE INDEX idx_job_positions_fts ON job_positions
USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || COALESCE(requirements::text, '')));

-- Email template search
CREATE INDEX idx_email_templates_fts ON email_templates
USING GIN (to_tsvector('english', name || ' ' || subject || ' ' || body));
```

### 4.6 JSONB Indexes

```sql
-- Skills array containment search
CREATE INDEX idx_candidates_skills ON candidates USING GIN (skills);

-- Candidate score breakdown for analysis
CREATE INDEX idx_candidate_scores_breakdown ON candidate_scores USING GIN (breakdown);
```

---

## 5. Row-Level Security Policies

### 5.1 Enable RLS on All Tables

```sql
-- Enable RLS on all user-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE sent_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
```

### 5.2 Helper Functions

```sql
-- Get current user ID from auth context
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID AS $$
  SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::UUID
$$ LANGUAGE SQL STABLE;

-- Check if user belongs to subscription team
CREATE OR REPLACE FUNCTION is_team_member(p_subscription_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM team_members tm
    JOIN subscriptions s ON s.id = tm.subscription_id
    WHERE s.id = p_subscription_id
      AND tm.user_id = auth.uid()
      AND tm.status = 'active'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get subscription for user
CREATE OR REPLACE FUNCTION get_user_subscription()
RETURNS UUID AS $$
  SELECT s.id FROM subscriptions s WHERE s.user_id = auth.uid()
$$ LANGUAGE SQL SECURITY DEFINER;
```

### 5.3 RLS Policies

```sql
-- ============================================================
-- CANDIDATES POLICIES
-- ============================================================

-- Users can see their own candidates
CREATE POLICY candidates_select ON candidates
  FOR SELECT
  USING (user_id = auth.uid());

-- Users can insert their own candidates
CREATE POLICY candidates_insert ON candidates
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Users can update their own candidates
CREATE POLICY candidates_update ON candidates
  FOR UPDATE
  USING (user_id = auth.uid());

-- Users can delete their own candidates
CREATE POLICY candidates_delete ON candidates
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================
-- JOB POSITIONS POLICIES
-- ============================================================

CREATE POLICY job_positions_select ON job_positions
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY job_positions_insert ON job_positions
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY job_positions_update ON job_positions
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY job_positions_delete ON job_positions
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================
-- EMAIL TEMPLATES POLICIES
-- ============================================================

CREATE POLICY email_templates_select ON email_templates
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY email_templates_insert ON email_templates
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY email_templates_update ON email_templates
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY email_templates_delete ON email_templates
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================
-- SENT EMAILS POLICIES
-- ============================================================

CREATE POLICY sent_emails_select ON sent_emails
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY sent_emails_insert ON sent_emails
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY sent_emails_update ON sent_emails
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY sent_emails_delete ON sent_emails
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================
-- CANDIDATE SCORES POLICIES
-- ============================================================

-- Allow access through candidate ownership
CREATE POLICY candidate_scores_select ON candidate_scores
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM candidates c
      WHERE c.id = candidate_scores.candidate_id
        AND c.user_id = auth.uid()
    )
  );

CREATE POLICY candidate_scores_insert ON candidate_scores
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM candidates c
      WHERE c.id = candidate_scores.candidate_id
        AND c.user_id = auth.uid()
    )
  );

CREATE POLICY candidate_scores_update ON candidate_scores
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM candidates c
      WHERE c.id = candidate_scores.candidate_id
        AND c.user_id = auth.uid()
    )
  );

CREATE POLICY candidate_scores_delete ON candidate_scores
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM candidates c
      WHERE c.id = candidate_scores.candidate_id
        AND c.user_id = auth.uid()
    )
  );

-- ============================================================
-- INTERVIEWS POLICIES
-- ============================================================

CREATE POLICY interviews_select ON interviews
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY interviews_insert ON interviews
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY interviews_update ON interviews
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY interviews_delete ON interviews
  FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================
-- SUBSCRIPTIONS POLICIES
-- ============================================================

CREATE POLICY subscriptions_select ON subscriptions
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY subscriptions_update ON subscriptions
  FOR UPDATE
  USING (user_id = auth.uid());

-- Only system can insert subscriptions (via API)
CREATE POLICY subscriptions_insert ON subscriptions
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- ============================================================
-- TEAM MEMBERS POLICIES
-- ============================================================

-- Members can see their team
CREATE POLICY team_members_select ON team_members
  FOR SELECT
  USING (
    subscription_id IN (
      SELECT id FROM subscriptions WHERE user_id = auth.uid()
    )
    OR
    EXISTS (
      SELECT 1 FROM subscriptions s
      JOIN team_members tm2 ON tm2.subscription_id = s.id
      WHERE tm2.email = (
        SELECT email FROM users WHERE id = auth.uid()
      )
      AND tm2.status = 'active'
    )
  );

-- Admins can manage team
CREATE POLICY team_members_insert ON team_members
  FOR INSERT
  WITH CHECK (
    subscription_id IN (
      SELECT id FROM subscriptions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY team_members_update ON team_members
  FOR UPDATE
  USING (
    subscription_id IN (
      SELECT id FROM subscriptions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY team_members_delete ON team_members
  FOR DELETE
  USING (
    subscription_id IN (
      SELECT id FROM subscriptions WHERE user_id = auth.uid()
    )
    AND role != 'owner'
  );

-- ============================================================
-- ONBOARDING PROGRESS POLICIES
-- ============================================================

CREATE POLICY onboarding_progress_select ON onboarding_progress
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY onboarding_progress_insert ON onboarding_progress
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY onboarding_progress_update ON onboarding_progress
  FOR UPDATE
  USING (user_id = auth.uid());

-- ============================================================
-- RESUME SUMMARIES POLICIES
-- ============================================================

CREATE POLICY resume_summaries_select ON resume_summaries
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY resume_summaries_insert ON resume_summaries
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY resume_summaries_update ON resume_summaries
  FOR UPDATE
  USING (user_id = auth.uid());

-- ============================================================
-- EMAIL TRACKING POLICIES
-- ============================================================

CREATE POLICY email_tracking_select ON email_tracking
  FOR SELECT
  USING (user_id = auth.uid());

-- ============================================================
-- ACTIVITY LOGS POLICIES
-- ============================================================

CREATE POLICY activity_logs_select ON activity_logs
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY activity_logs_insert ON activity_logs
  FOR INSERT
  WITH CHECK (user_id = auth.uid());
```

---

## 6. Supabase Implementation

### 6.1 Supabase Project Setup

```sql
-- ============================================================
-- SUPABASE SCHEMA SETUP
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy search

-- Set search path
ALTER DATABASE postgres SET search_path TO public, auth;
```

### 6.2 Supabase Auth Integration

```sql
-- ============================================================
-- SUPABASE AUTH TRIGGERS
-- ============================================================

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Create subscription for new user
  INSERT INTO public.subscriptions (
    user_id,
    plan_type,
    status,
    trial_end,
    current_period_start,
    current_period_end
  ) VALUES (
    NEW.id,
    'trial',
    'trialing',
    NOW() + INTERVAL '14 days',
    NOW(),
    NOW() + INTERVAL '14 days'
  );
  
  -- Create onboarding progress
  INSERT INTO public.onboarding_progress (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_candidates_updated_at
  BEFORE UPDATE ON candidates
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_job_positions_updated_at
  BEFORE UPDATE ON job_positions
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_sent_emails_updated_at
  BEFORE UPDATE ON sent_emails
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
```

### 6.3 Storage Buckets

```sql
-- ============================================================
-- SUPABASE STORAGE SETUP
-- ============================================================

-- Create resumes bucket (run in Supabase dashboard or via API)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('resumes', 'resumes', false);

-- Storage policies for resumes
CREATE POLICY "Users can upload resumes"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'resumes'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can view their resumes"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'resumes'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can update their resumes"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'resumes'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

CREATE POLICY "Users can delete their resumes"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'resumes'
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

### 6.4 Database Functions

```sql
-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Search candidates by skills
CREATE OR REPLACE FUNCTION search_candidates_by_skills(
  p_skills TEXT[],
  p_match_threshold INTEGER DEFAULT 1
)
RETURNS TABLE (
  candidate_id UUID,
  match_count INTEGER,
  candidate_data JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    COUNT(*)::INTEGER AS match_count,
    jsonb_build_object(
      'id', c.id,
      'full_name', c.full_name,
      'email', c.email,
      'skills', c.skills,
      'experience_years', c.experience_years,
      'status', c.status
    ) AS candidate_data
  FROM candidates c,
       unnest(c.skills) AS skill
  WHERE skill = ANY(p_skills)
  GROUP BY c.id
  HAVING COUNT(*) >= p_match_threshold
  ORDER BY match_count DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get candidate pipeline stats
CREATE OR REPLACE FUNCTION get_candidate_pipeline_stats(p_user_id UUID)
RETURNS TABLE (
  status VARCHAR(50),
  count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT c.status, COUNT(*)::BIGINT
  FROM candidates c
  WHERE c.user_id = p_user_id
  GROUP BY c.status
  ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get hiring metrics
CREATE OR REPLACE FUNCTION get_hiring_metrics(p_user_id UUID, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
  metric_name TEXT,
  metric_value NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 'total_candidates'::TEXT, COUNT(DISTINCT c.id)::NUMERIC
  FROM candidates c
  WHERE c.user_id = p_user_id
    AND c.created_at >= NOW() - (p_days || ' days')::INTERVAL
  
  UNION ALL
  
  SELECT 'total_hired'::TEXT, COUNT(DISTINCT c.id)::NUMERIC
  FROM candidates c
  WHERE c.user_id = p_user_id
    AND c.status = 'hired'
    AND c.updated_at >= NOW() - (p_days || ' days')::INTERVAL
  
  UNION ALL
  
  SELECT 'avg_time_to_hire_days'::TEXT,
    COALESCE(AVG(EXTRACT(DAY FROM c.updated_at - c.created_at))::NUMERIC, 0)
  FROM candidates c
  WHERE c.user_id = p_user_id
    AND c.status = 'hired'
    AND c.updated_at >= NOW() - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Email tracking pixel endpoint (returns 1x1 transparent GIF)
CREATE OR REPLACE FUNCTION track_email_open(p_tracking_id TEXT)
RETURNS BYTEA AS $$
BEGIN
  -- Update tracking record
  UPDATE email_tracking
  SET
    opened = TRUE,
    opened_at = NOW()
  WHERE tracking_id = p_tracking_id
    AND opened = FALSE;
  
  -- Return 1x1 transparent GIF
  RETURN E'\x474946383961010001008c00000000000021f90400100020002c000000010001000000020354486c00000015000021000000ff02ff0aff00012c0100000b4a4803ff25000000';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 6.5 Real-time Subscriptions

```sql
-- Enable real-time for activity updates
ALTER PUBLICATION supabase_realtime ADD TABLE activity_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE interviews;
ALTER PUBLICATION supabase_realtime ADD TABLE candidates;
```

### 6.6 Backups & Retention

```sql
-- ============================================================
-- BACKUP CONFIGURATION
-- ============================================================

-- Point-in-time recovery is enabled by default on Supabase Pro tier
-- Configure retention policy for activity logs

CREATE OR REPLACE FUNCTION cleanup_old_activity_logs()
RETURNS void AS $$
BEGIN
  DELETE FROM activity_logs
  WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Run cleanup weekly (configure in Supabase Cron or external scheduler)
-- SELECT cron.schedule('cleanup-activity-logs', '0 2 * * 0', 'SELECT cleanup_old_activity_logs()');
```

---

## 7. Migration Scripts

### 7.1 Initial Migration

```sql
-- ============================================================
-- MIGRATION: 001_initial_schema.sql
-- Run with: supabase db push or via migration file
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    resume_url VARCHAR(500),
    resume_text TEXT,
    skills JSONB DEFAULT '[]'::jsonb,
    experience_years INTEGER DEFAULT 0,
    education_level VARCHAR(100),
    current_position VARCHAR(255),
    current_company VARCHAR(255),
    linkedin_url VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    source VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- [Continue with all other tables...]

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_candidates_user_id ON candidates(user_id);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
-- [Continue with all other tables...]

-- Create RLS policies (see Section 5)
-- [Policies defined in Section 5.3...]
```

### 7.2 Update Migration Template

```sql
-- ============================================================
-- MIGRATION: 002_add_xyz.sql
-- Description: Add new feature
-- ============================================================

BEGIN;

-- Add new column
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS source VARCHAR(100);

-- Add index
CREATE INDEX IF NOT EXISTS idx_candidates_source ON candidates(source);

-- Update policy if needed
DROP POLICY IF EXISTS candidates_select ON candidates;
CREATE POLICY candidates_select ON candidates
  FOR SELECT
  USING (user_id = auth.uid());

COMMIT;
```

---

## Appendix A: Quick Reference

### Table Summary

| Table | Rows/User | Size Est. | RLS |
|-------|-----------|-----------|-----|
| users | 1 | 1 KB | No |
| candidates | 100s-1000s | 10-50 KB | Yes |
| job_positions | 10s | 5 KB | Yes |
| candidate_scores | Linked to candidates | 1 KB | Yes |
| email_templates | 10s | 2 KB | Yes |
| sent_emails | 1000s | 5 KB | Yes |
| interviews | 100s | 2 KB | Yes |
| subscriptions | 1 | 1 KB | Yes |
| team_members | 1-5 | 1 KB | Yes |
| onboarding_progress | 1 | 1 KB | Yes |
| email_tracking | Linked to sent_emails | 0.5 KB | Yes |
| resume_summaries | Linked to candidates | 2 KB | Yes |
| activity_logs | 1000s | 0.5 KB | Yes |

### Storage Estimates

| Resource | Estimate |
|----------|----------|
| Per user (basic) | 50-100 KB |
| Per candidate | 10-50 KB |
| Per email | 5 KB |
| Resume file storage | 1-10 MB per file |

---

*End of Database Design Document*
