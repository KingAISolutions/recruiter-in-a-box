# Recruiter In A Box - OpenAPI Specification

**Version:** 1.0  
**Last Updated:** 2026-07-16  
**Base URL:** `https://api.recruiterinabox.com/v1`  
**Status:** Production Ready

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Candidates](#2-candidates)
3. [Jobs](#3-jobs)
4. [Interviews](#4-interviews)
5. [Subscriptions](#5-subscriptions)
6. [Common Patterns](#6-common-patterns)

---

## 1. Authentication

### 1.1 Register User

Register a new user account and start a 14-day free trial.

**Endpoint:** `POST /api/auth/signup`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "john.doe@company.com",
  "password": "securePassword123!",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string | Yes | Valid email format | User's email address (must be unique) |
| `password` | string | Yes | Min 8 characters | Account password |
| `full_name` | string | Yes | Non-empty | User's display name |
| `company_name` | string | No | Max 255 chars | Company/organization name |

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@company.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "email_verified": false,
  "created_at": "2026-07-16T10:30:00Z",
  "updated_at": "2026-07-16T10:30:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `validation_error` | Invalid request data |
| 409 | `email_exists` | Email already registered |
| 429 | `rate_limited` | Too many requests |

**Example Response (409 Conflict):**
```json
{
  "error": {
    "code": "email_exists",
    "message": "A user with this email already exists",
    "details": []
  }
}
```

---

### 1.2 Login

Authenticate user and receive access tokens.

**Endpoint:** `POST /api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "john.doe@company.com",
  "password": "securePassword123!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Registered email address |
| `password` | string | Yes | Account password |

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "token_type": "bearer"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT token for API authentication (expires in 15 minutes) |
| `refresh_token` | string | Token for refreshing access token (expires in 7 days) |
| `token_type` | string | Always "bearer" |

**Using the Access Token:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `validation_error` | Invalid request data |
| 401 | `invalid_credentials` | Email or password incorrect |
| 429 | `rate_limited` | Too many login attempts |

---

### 1.3 Refresh Token

Get a new access token using a refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "bmV3IHJlZnJlc2ggdG9rZW4...",
  "token_type": "bearer"
}
```

---

### 1.4 Get Current User

Retrieve the authenticated user's profile.

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@company.com",
  "full_name": "John Doe",
  "company_name": "Acme Corp",
  "email_verified": false,
  "created_at": "2026-07-16T10:30:00Z",
  "updated_at": "2026-07-16T10:30:00Z"
}
```

---

### 1.5 Update Current User

Update the authenticated user's profile.

**Endpoint:** `PUT /api/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "John M. Doe",
  "company_name": "Acme Corporation"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | No | Updated display name |
| `company_name` | string | No | Updated company name |

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@company.com",
  "full_name": "John M. Doe",
  "company_name": "Acme Corporation",
  "email_verified": false,
  "created_at": "2026-07-16T10:30:00Z",
  "updated_at": "2026-07-16T10:35:00Z"
}
```

---

## 2. Candidates

### 2.1 List Candidates

Retrieve a paginated list of candidates.

**Endpoint:** `GET /api/candidates`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |
| `search` | string | - | Search in name, email, skills |
| `status` | string | - | Filter by status |
| `source` | string | - | Filter by source |

**Status Values:** `new`, `screening`, `interview`, `offer`, `hired`, `rejected`

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "full_name": "Jane Smith",
      "email": "jane.smith@email.com",
      "phone": "+1-555-0123",
      "skills": ["Python", "React", "TypeScript"],
      "experience_years": 5,
      "education_level": "Bachelor",
      "current_position": "Senior Developer",
      "current_company": "TechCorp",
      "status": "screening",
      "source": "LinkedIn",
      "created_at": "2026-07-10T14:20:00Z",
      "updated_at": "2026-07-15T09:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "full_name": "Michael Johnson",
      "email": "michael.j@email.com",
      "phone": "+1-555-0456",
      "skills": ["Java", "Spring Boot", "AWS"],
      "experience_years": 8,
      "education_level": "Master",
      "current_position": "Tech Lead",
      "current_company": "Enterprise Inc",
      "status": "interview",
      "source": "Referral",
      "created_at": "2026-07-08T11:15:00Z",
      "updated_at": "2026-07-14T16:45:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | Array of candidate objects |
| `total` | integer | Total number of candidates |
| `page` | integer | Current page number |
| `page_size` | integer | Items per page |
| `total_pages` | integer | Total number of pages |

---

### 2.2 Get Candidate

Retrieve a single candidate by ID.

**Endpoint:** `GET /api/candidates/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Candidate unique identifier |

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Jane Smith",
  "email": "jane.smith@email.com",
  "phone": "+1-555-0123",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "resume_url": "https://storage.example.com/resumes/550e8400.pdf",
  "resume_text": "Jane Smith is an experienced software developer...",
  "skills": ["Python", "React", "TypeScript", "PostgreSQL", "Docker"],
  "experience_years": 5,
  "education_level": "Bachelor",
  "current_position": "Senior Developer",
  "current_company": "TechCorp",
  "status": "screening",
  "source": "LinkedIn",
  "notes": "Strong technical background, excellent communication skills",
  "created_at": "2026-07-10T14:20:00Z",
  "updated_at": "2026-07-15T09:00:00Z"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `not_found` | Candidate not found |

---

### 2.3 Create Candidate

Create a new candidate.

**Endpoint:** `POST /api/candidates`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane.smith@email.com",
  "phone": "+1-555-0123",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "skills": ["Python", "React", "TypeScript"],
  "experience_years": 5,
  "education_level": "Bachelor",
  "current_position": "Senior Developer",
  "current_company": "TechCorp",
  "status": "new",
  "source": "LinkedIn",
  "notes": "Strong technical background"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | Yes | Candidate's full name |
| `email` | string | Yes | Valid email address |
| `phone` | string | No | Contact phone number |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `skills` | array[string] | No | List of skills |
| `experience_years` | integer | No | Years of experience |
| `education_level` | string | No | Education level |
| `current_position` | string | No | Current job title |
| `current_company` | string | No | Current employer |
| `status` | string | No | Pipeline status (default: "new") |
| `source` | string | No | Source of candidate |
| `notes` | string | No | Internal notes |

**Education Levels:** `high_school`, `associate`, `bachelor`, `master`, `phd`

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Jane Smith",
  "email": "jane.smith@email.com",
  "phone": "+1-555-0123",
  "linkedin_url": "https://linkedin.com/in/janesmith",
  "skills": ["Python", "React", "TypeScript"],
  "experience_years": 5,
  "education_level": "Bachelor",
  "current_position": "Senior Developer",
  "current_company": "TechCorp",
  "status": "new",
  "source": "LinkedIn",
  "notes": "Strong technical background",
  "created_at": "2026-07-16T10:30:00Z",
  "updated_at": "2026-07-16T10:30:00Z"
}
```

---

### 2.4 Update Candidate

Update an existing candidate.

**Endpoint:** `PUT /api/candidates/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "interview",
  "notes": "Passed initial screening, scheduling interview"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "full_name": "Jane Smith",
  "email": "jane.smith@email.com",
  "status": "interview",
  "notes": "Passed initial screening, scheduling interview",
  "updated_at": "2026-07-16T11:00:00Z"
}
```

---

### 2.5 Upload Resume

Upload a resume file and extract candidate information.

**Endpoint:** `POST /api/candidates/upload`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | PDF or DOCX resume (max 10MB) |
| `name` | string | No | Override extracted name |
| `email` | string | No | Override extracted email |

**Response (200 OK):**
```json
{
  "candidate_id": "550e8400-e29b-41d4-a716-446655440001",
  "resume_url": "https://storage.example.com/resumes/user123/candidate456/resume.pdf",
  "resume_text": "Full text extracted from resume...",
  "extracted_data": {
    "full_name": "Jane Smith",
    "email": "jane.smith@email.com",
    "phone": "+1-555-0123",
    "skills": ["Python", "React", "TypeScript"],
    "experience_years": 5,
    "education_level": "Bachelor",
    "current_position": "Senior Developer",
    "current_company": "TechCorp"
  }
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `invalid_file_type` | Only PDF and DOCX allowed |
| 400 | `file_too_large` | File exceeds 10MB limit |
| 413 | `payload_too_large` | Request too large |

---

### 2.6 Delete Candidate

Delete a candidate and all associated data.

**Endpoint:** `DELETE /api/candidates/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (204 No Content):**
```
(empty body)
```

---

## 3. Jobs

### 3.1 List Jobs

Retrieve a paginated list of job positions.

**Endpoint:** `GET /api/jobs`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |
| `search` | string | - | Search in title, description |
| `status` | string | - | Filter by status |

**Status Values:** `open`, `closed`, `on_hold`

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Senior Software Engineer",
      "description": "We are looking for a senior software engineer...",
      "requirements": {
        "required_skills": ["Python", "React"],
        "preferred_skills": ["AWS", "Docker"],
        "min_experience_years": 5,
        "education_level": "Bachelor"
      },
      "department": "Engineering",
      "location": "San Francisco, CA (Remote)",
      "salary_range": "$120,000 - $160,000",
      "status": "open",
      "created_at": "2026-07-01T09:00:00Z",
      "updated_at": "2026-07-15T14:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "title": "Product Manager",
      "description": "Lead product strategy and development...",
      "requirements": {
        "required_skills": ["Product Management", "Agile"],
        "preferred_skills": ["Technical Background", "B2B SaaS"],
        "min_experience_years": 3,
        "education_level": "Bachelor"
      },
      "department": "Product",
      "location": "New York, NY",
      "salary_range": "$100,000 - $140,000",
      "status": "open",
      "created_at": "2026-07-05T11:00:00Z",
      "updated_at": "2026-07-12T10:15:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### 3.2 Get Job

Retrieve a single job position by ID.

**Endpoint:** `GET /api/jobs/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer to join our team...",
  "requirements": {
    "required_skills": ["Python", "React"],
    "preferred_skills": ["AWS", "Docker"],
    "min_experience_years": 5,
    "education_level": "Bachelor"
  },
  "department": "Engineering",
  "location": "San Francisco, CA (Remote)",
  "salary_range": "$120,000 - $160,000",
  "status": "open",
  "created_at": "2026-07-01T09:00:00Z",
  "updated_at": "2026-07-15T14:30:00Z"
}
```

---

### 3.3 Create Job

Create a new job position.

**Endpoint:** `POST /api/jobs`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer to join our growing team. You will be responsible for building and maintaining our core platform features.",
  "requirements": {
    "required_skills": ["Python", "React", "PostgreSQL"],
    "preferred_skills": ["AWS", "Docker", "Kubernetes"],
    "min_experience_years": 5,
    "education_level": "Bachelor"
  },
  "department": "Engineering",
  "location": "San Francisco, CA (Remote)",
  "salary_range": "$120,000 - $160,000",
  "status": "open"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Job title |
| `description` | string | No | Full job description |
| `requirements` | object | No | Job requirements object |
| `requirements.required_skills` | array[string] | No | Required skills |
| `requirements.preferred_skills` | array[string] | No | Nice-to-have skills |
| `requirements.min_experience_years` | integer | No | Minimum years of experience |
| `requirements.education_level` | string | No | Minimum education requirement |
| `department` | string | No | Department name |
| `location` | string | No | Job location |
| `salary_range` | string | No | Salary range |
| `status` | string | No | Job status (default: "open") |

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Software Engineer",
  "description": "We are looking for a senior software engineer to join our growing team...",
  "requirements": {
    "required_skills": ["Python", "React", "PostgreSQL"],
    "preferred_skills": ["AWS", "Docker", "Kubernetes"],
    "min_experience_years": 5,
    "education_level": "Bachelor"
  },
  "department": "Engineering",
  "location": "San Francisco, CA (Remote)",
  "salary_range": "$120,000 - $160,000",
  "status": "open",
  "created_at": "2026-07-16T10:30:00Z",
  "updated_at": "2026-07-16T10:30:00Z"
}
```

---

### 3.4 Update Job

Update an existing job position.

**Endpoint:** `PUT /api/jobs/{id}`

**Request Body:**
```json
{
  "status": "closed",
  "salary_range": "$130,000 - $170,000"
}
```

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Senior Software Engineer",
  "status": "closed",
  "salary_range": "$130,000 - $170,000",
  "updated_at": "2026-07-16T11:00:00Z"
}
```

---

### 3.5 Delete Job

Delete a job position.

**Endpoint:** `DELETE /api/jobs/{id}`

**Response (204 No Content):**
```
(empty body)
```

---

## 4. Interviews

### 4.1 List Interviews

Retrieve a paginated list of interviews.

**Endpoint:** `GET /api/interviews`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `status` | string | - | Filter by status |
| `candidate_id` | UUID | - | Filter by candidate |
| `upcoming_only` | boolean | false | Show only upcoming |

**Status Values:** `scheduled`, `confirmed`, `completed`, `canceled`, `rescheduled`

**Interview Types:** `phone`, `video`, `onsite`, `technical`

**Response (200 OK):**
```json
{
  "interviews": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "candidate_id": "550e8400-e29b-41d4-a716-446655440001",
      "candidate_name": "Jane Smith",
      "title": "Technical Interview with Jane",
      "interview_type": "video",
      "scheduled_at": "2026-07-20T14:00:00Z",
      "duration_minutes": 60,
      "location": "https://zoom.us/j/123456789",
      "status": "scheduled",
      "notes": "Focus on system design",
      "feedback": null,
      "rating": null,
      "created_at": "2026-07-16T10:00:00Z"
    }
  ],
  "total": 5,
  "upcoming": 3,
  "completed": 2
}
```

---

### 4.2 Get Interview

Retrieve a single interview by ID.

**Endpoint:** `GET /api/interviews/{id}`

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440001",
  "candidate_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_position_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Technical Interview with Jane",
  "interview_type": "video",
  "scheduled_at": "2026-07-20T14:00:00Z",
  "duration_minutes": 60,
  "location": "https://zoom.us/j/123456789",
  "status": "scheduled",
  "notes": "Focus on system design and coding",
  "feedback": null,
  "rating": null,
  "calendar_event_id": "cal_abc123",
  "created_at": "2026-07-16T10:00:00Z",
  "updated_at": "2026-07-16T10:00:00Z"
}
```

---

### 4.3 Schedule Interview

Schedule a new interview.

**Endpoint:** `POST /api/interviews`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "candidate_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_position_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Technical Interview with Jane",
  "interview_type": "video",
  "scheduled_at": "2026-07-20T14:00:00Z",
  "duration_minutes": 60,
  "location": "https://zoom.us/j/123456789",
  "notes": "Focus on system design and coding skills"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `candidate_id` | UUID | Yes | Candidate to interview |
| `job_position_id` | UUID | No | Related job position |
| `title` | string | No | Interview title |
| `interview_type` | string | No | Type (default: "video") |
| `scheduled_at` | datetime | Yes | Interview date/time (ISO 8601) |
| `duration_minutes` | integer | No | Duration (default: 60) |
| `location` | string | No | Meeting link or address |
| `notes` | string | No | Preparation notes |

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440001",
  "candidate_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Technical Interview with Jane",
  "interview_type": "video",
  "scheduled_at": "2026-07-20T14:00:00Z",
  "duration_minutes": 60,
  "location": "https://zoom.us/j/123456789",
  "status": "scheduled",
  "notes": "Focus on system design and coding skills",
  "created_at": "2026-07-16T10:00:00Z"
}
```

---

### 4.4 Update Interview

Update an existing interview.

**Endpoint:** `PUT /api/interviews/{id}`

**Request Body:**
```json
{
  "scheduled_at": "2026-07-21T15:00:00Z",
  "status": "confirmed"
}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440001",
  "scheduled_at": "2026-07-21T15:00:00Z",
  "status": "confirmed",
  "updated_at": "2026-07-16T12:00:00Z"
}
```

---

### 4.5 Complete Interview

Mark an interview as completed with feedback.

**Endpoint:** `POST /api/interviews/{id}/complete`

**Request Body:**
```json
{
  "feedback": "Excellent technical skills, strong communication. Recommended for next round.",
  "rating": 4
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `feedback` | string | No | Interview feedback notes |
| `rating` | integer | No | Rating 1-5 |

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "feedback": "Excellent technical skills, strong communication. Recommended for next round.",
  "rating": 4,
  "updated_at": "2026-07-20T16:00:00Z"
}
```

---

### 4.6 Cancel Interview

Cancel an interview.

**Endpoint:** `DELETE /api/interviews/{id}`

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440001",
  "status": "canceled",
  "updated_at": "2026-07-19T10:00:00Z"
}
```

---

## 5. Subscriptions

### 5.1 Get Subscription Status

Get current subscription and plan limits.

**Endpoint:** `GET /api/subscriptions/status`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "subscription": {
    "id": "880e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "stripe_customer_id": "cus_abc123",
    "stripe_subscription_id": "sub_xyz789",
    "plan_type": "professional",
    "status": "trialing",
    "current_period_start": "2026-07-16T10:30:00Z",
    "current_period_end": "2026-07-30T10:30:00Z",
    "trial_end": "2026-07-30T10:30:00Z",
    "cancel_at_period_end": false,
    "created_at": "2026-07-16T10:30:00Z"
  },
  "plan_limits": {
    "candidates_per_month": 100,
    "job_positions": 10,
    "team_seats": 1,
    "ai_scoring": true,
    "email_outreach": true,
    "analytics": "basic",
    "support": "email"
  },
  "trial_days_remaining": 14,
  "trial_expired": false
}
```

**Plan Types:** `trial`, `professional`, `agency`

**Plan Limits:**

| Limit | Professional | Agency |
|-------|--------------|--------|
| `candidates_per_month` | 100 | -1 (unlimited) |
| `job_positions` | 10 | -1 (unlimited) |
| `team_seats` | 1 | 5 |
| `ai_scoring` | true | true |
| `email_outreach` | true | true |
| `analytics` | "basic" | "advanced" |
| `support` | "email" | "priority" |

---

### 5.2 Create Checkout Session

Create a Stripe checkout session for subscription.

**Endpoint:** `POST /api/subscriptions/checkout`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "plan": "professional"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan` | string | Yes | Plan to subscribe to |

**Plan Values:** `professional` ($99/mo), `agency` ($299/mo)

**Response (200 OK):**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/test_...",
  "session_id": "cs_test_abc123"
}
```

**User Flow:**
1. Receive `checkout_url`
2. Redirect user to Stripe Checkout
3. After payment, Stripe redirects to `success_url`
4. Webhook updates subscription status

---

### 5.3 Create Billing Portal

Create a Stripe billing portal session.

**Endpoint:** `POST /api/subscriptions/portal`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "portal_url": "https://billing.stripe.com/session/test_..."
}
```

**User Flow:**
1. Receive `portal_url`
2. Redirect user to billing portal
3. User can update payment method, view invoices, cancel subscription

---

### 5.4 Cancel Subscription

Cancel the current subscription.

**Endpoint:** `POST /api/subscriptions/cancel`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cancel_now` | boolean | false | Cancel immediately or at period end |

**Response (200 OK):**
```json
{
  "message": "Subscription canceled. Access continues until 2026-08-16."
}
```

---

## 6. Common Patterns

### 6.1 Pagination

All list endpoints support pagination:

```http
GET /api/candidates?page=2&page_size=50
```

**Pagination Response Fields:**
```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "page_size": 50,
  "total_pages": 3
}
```

### 6.2 Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

**Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Invalid request data |
| `unauthorized` | 401 | Missing or invalid token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `conflict` | 409 | Resource conflict |
| `rate_limited` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

### 6.3 Rate Limiting

**Rate limit headers included in all responses:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1689500060
```

| Endpoint Pattern | Limit |
|-----------------|-------|
| `/api/auth/*` | 10 req/min per IP |
| `/api/candidates/*` | 100 req/min per user |
| `/api/jobs/*` | 100 req/min per user |
| `/api/interviews/*` | 50 req/min per user |
| `/api/subscriptions/*` | 20 req/min per user |
| All other endpoints | 200 req/min per user |

### 6.4 HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### 6.5 Authentication

All endpoints except `/api/auth/*` require authentication:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Tokens expire after 15 minutes. Use the refresh endpoint to get new tokens.

---

## Appendix A: OpenAPI YAML

```yaml
openapi: 3.0.0
info:
  title: Recruiter In A Box API
  version: 1.0.0
  description: AI-Powered SaaS Recruitment Platform

servers:
  - url: https://api.recruiterinabox.com/v1
    description: Production

paths:
  /auth/signup:
    post:
      tags: [Authentication]
      summary: Register new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SignupRequest'
      responses:
        201:
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  /auth/login:
    post:
      tags: [Authentication]
      summary: Login user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenResponse'

components:
  schemas:
    SignupRequest:
      type: object
      required:
        - email
        - password
        - full_name
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          minLength: 8
        full_name:
          type: string
        company_name:
          type: string

    LoginRequest:
      type: object
      required:
        - email
        - password
      properties:
        email:
          type: string
          format: email
        password:
          type: string

    TokenResponse:
      type: object
      properties:
        access_token:
          type: string
        refresh_token:
          type: string
        token_type:
          type: string

    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        full_name:
          type: string
        company_name:
          type: string
        created_at:
          type: string
          format: date-time

    Candidate:
      type: object
      properties:
        id:
          type: string
          format: uuid
        full_name:
          type: string
        email:
          type: string
          format: email
        skills:
          type: array
          items:
            type: string
        status:
          type: string
          enum: [new, screening, interview, offer, hired, rejected]

    Job:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        status:
          type: string
          enum: [open, closed, on_hold]
        requirements:
          type: object

    Interview:
      type: object
      properties:
        id:
          type: string
          format: uuid
        candidate_id:
          type: string
          format: uuid
        interview_type:
          type: string
          enum: [phone, video, onsite, technical]
        scheduled_at:
          type: string
          format: date-time
        status:
          type: string
          enum: [scheduled, confirmed, completed, canceled]
```

---

*End of API Specification*
