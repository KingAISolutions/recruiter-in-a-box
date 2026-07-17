# Recruiter In A Box - Known Issues List

**Version:** 1.0  
**Date:** 2026-07-16  
**Status:** Active  

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 3 | Must fix before production |
| High | 5 | Should fix before production |
| Medium | 7 | Fix in near-term roadmap |
| Low | 4 | Nice to have / technical debt |

**Total Known Issues:** 19

---

## Critical Issues (Must Fix Before Production)

### CR-001: No Rate Limiting

**Severity:** Critical  
**Component:** Backend API  
**Status:** Open  

**Description:**
No rate limiting is implemented on any API endpoint. The application is vulnerable to:
- Brute force attacks on login endpoint
- API abuse and DoS attacks
- Resource exhaustion via bulk operations

**Impact:**
- Security vulnerability
- Service availability risk
- Potential billing fraud

**Current Behavior:**
```python
# All endpoints allow unlimited requests
@router.post("/auth/login")  # No rate limit
async def login(...):
    ...
```

**Recommended Fix:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(...):
    ...
```

**Effort:** 4 hours

---

### CR-002: Default SECRET_KEY in Codebase

**Severity:** Critical  
**Component:** Backend Config  
**Status:** Open  

**Description:**
The application ships with a default `SECRET_KEY` that must be changed before production use.

**Current Code (core/config.py):**
```python
SECRET_KEY: str = "your-secret-key-change-in-production"
```

**Impact:**
- JWT tokens can be forged if the default key is not changed
- All existing tokens become invalid after key rotation

**Workaround:**
Set `SECRET_KEY` environment variable in production.

**Recommended Fix:**
```python
import secrets

SECRET_KEY: str = settings.SECRET_KEY  # No default, fail if not set

# Or validate at startup
if settings.SECRET_KEY == "your-secret-key-change-in-production":
    raise ValueError("SECRET_KEY must be changed from default")
```

**Effort:** 2 hours

---

### CR-003: Token Storage Vulnerability

**Severity:** Critical  
**Component:** Frontend  
**Status:** Open  

**Description:**
Access and refresh tokens are stored in localStorage, which is vulnerable to XSS attacks.

**Current Code (frontend/src/services/api.ts):**
```typescript
// Line 35 - Token stored in localStorage
const token = localStorage.getItem('access_token')
```

**Impact:**
- XSS vulnerabilities can steal tokens
- Stolen tokens allow account takeover

**Recommended Fix:**
Use httpOnly cookies for token storage:
```typescript
// Use cookie-based auth instead
document.cookie = `access_token=${token}; HttpOnly; Secure; SameSite=Strict`
```

**Effort:** 8 hours (requires backend changes for cookie handling)

---

## High Priority Issues

### HI-001: No Token Revocation

**Severity:** High  
**Component:** Backend Auth  
**Status:** Open  

**Description:**
There is no mechanism to revoke JWT tokens. If a token is compromised, it remains valid until expiration.

**Impact:**
- Cannot force logout
- Cannot invalidate tokens after password change
- Stolen tokens remain usable

**Workaround:**
Wait for token to expire (15 minutes for access token).

**Recommended Fix:**
Implement Redis-based token blacklist or use short-lived tokens.

**Effort:** 6 hours

---

### HI-002: No Role-Based Access Control

**Severity:** High  
**Component:** Backend API  
**Status:** Open  

**Description:**
Team member roles (owner, admin, member) are stored but never enforced. All authenticated users have full access.

**Current Behavior:**
```python
# Role is stored but never checked
class TeamMember(Base):
    role = Column(String(50), default="member")  # owner, admin, member

# No permission checks in endpoints
@router.put("/teams/{member_id}")  # Any authenticated user can modify
async def update_team_member(...):
    ...
```

**Impact:**
- Team collaboration features don't work as designed
- Any user can modify any team member's role

**Recommended Fix:**
Add permission decorators:
```python
def require_role(*roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                raise HTTPException(403)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@router.delete("/teams/{member_id}")
@require_role("owner", "admin")  # Only owners and admins
async def remove_team_member(...):
    ...
```

**Effort:** 12 hours

---

### HI-003: Missing Database Migrations

**Severity:** High  
**Component:** Database  
**Status:** Open  

**Description:**
The application uses `Base.metadata.create_all()` for schema creation instead of a proper migration system like Alembic.

**Current Code (core/database.py):**
```python
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # No versioning
```

**Impact:**
- No schema versioning
- Cannot safely rollback changes
- Production deployments are risky

**Recommended Fix:**
Implement Alembic migrations:
```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

**Effort:** 8 hours

---

### HI-004: No Database SSL Configuration

**Severity:** High  
**Component:** Database  
**Status:** Open  

**Description:**
Database connections are not encrypted. SSL must be explicitly enabled for production.

**Current Code (core/database.py):**
```python
# No SSL configuration
engine = create_async_engine(settings.DATABASE_URL, ...)
```

**Impact:**
- Sensitive data (resumes, PII) transmitted unencrypted
- Compliance issues (SOC2, GDPR)

**Recommended Fix:**
```python
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", 
    "postgresql+asyncpg://?sslmode=require"
)
```

**Effort:** 1 hour

---

### HI-005: No Security Headers

**Severity:** High  
**Component:** Backend  
**Status:** Open  

**Description:**
Missing security headers leave the application vulnerable to common web attacks.

**Missing Headers:**
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security
- Content-Security-Policy

**Impact:**
- Clickjacking attacks
- MIME sniffing
- Protocol downgrade attacks

**Recommended Fix:**
```python
from fastapi.middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

**Effort:** 4 hours

---

## Medium Priority Issues

### ME-001: Limited File Type Validation

**Severity:** Medium  
**Component:** File Upload  
**Status:** Open  

**Description:**
File upload only validates by extension, not by actual content type.

**Current Code (utils/helpers.py):**
```python
def validate_file_type(filename: str) -> bool:
    allowed_extensions = {'.pdf'}  # Only checks extension
```

**Impact:**
- Malicious files could be uploaded with .pdf extension

**Recommended Fix:**
```python
import magic

def validate_file_type(filename: str, content: bytes) -> bool:
    mime = magic.from_buffer(content, mime=True)
    return mime == 'application/pdf'
```

**Effort:** 4 hours

---

### ME-002: No Monitoring/Metrics

**Severity:** Medium  
**Component:** Infrastructure  
**Status:** Open  

**Description:**
No metrics, tracing, or observability infrastructure is in place.

**Impact:**
- No visibility into application health
- Cannot detect issues proactively
- Difficult to troubleshoot production problems

**Recommended Fix:**
1. Add Prometheus metrics
2. Integrate distributed tracing (Jaeger)
3. Set up alerting

**Effort:** 16 hours

---

### ME-003: Dashboard Chart Data is Mock

**Severity:** Medium  
**Component:** Dashboard API  
**Status:** Open  

**Description:**
The chart endpoints return mock data instead of real database queries.

**Current Code (dashboard/router.py line 230-246):**
```python
# Returns mock data
count = (i % 7) + 1  # Simulated daily counts
data.append({"date": date.strftime("%Y-%m-%d"), "count": count})
```

**Impact:**
- Analytics charts don't show real data
- Misleading dashboard information

**Recommended Fix:**
Implement actual database queries with date grouping.

**Effort:** 6 hours

---

### ME-004: Interview Type Query Parameter Bug

**Severity:** Medium  
**Component:** Interviews API  
**Status:** Open  

**Description:**
The interviews router uses `status_filter` parameter but Swagger expects `status`.

**Current Code (interviews/router.py):**
```python
async def list_interviews(
    status_filter: Optional[str] = Query(None, alias="status"),  # alias mismatch
```

**Impact:**
- API documentation shows incorrect parameter name
- Potential confusion for API consumers

**Recommended Fix:**
Use consistent parameter names.

**Effort:** 1 hour

---

### ME-005: File Upload Path Traversal Risk

**Severity:** Medium  
**Component:** File Upload  
**Status:** Open  

**Description:**
Filename generation could allow path traversal if not properly sanitized.

**Current Code (candidates/router.py):**
```python
filename = generate_filename(file.filename, str(current_user.id))
file_path = upload_dir / filename.split('/')[-1]  # Simple split
```

**Impact:**
- Potential path traversal attacks
- Files could be written outside intended directory

**Recommended Fix:**
```python
# Sanitize filename thoroughly
safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', original_filename)
unique_id = uuid.uuid4().hex[:8]
filename = f"{user_id}/{unique_id}_{safe_filename}"
```

**Effort:** 2 hours

---

### ME-006: No Automated Backups

**Severity:** Medium  
**Component:** Database  
**Status:** Open  

**Description:**
No automated backup strategy is configured for production.

**Impact:**
- Data loss risk
- Compliance issues

**Recommended Fix:**
```bash
# Daily backup cron job
0 2 * * * pg_dump -h hostname -U user db | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Weekly offsite backup
0 3 * * 0 aws s3 cp /backups/ s3://bucket/backups/ --recursive
```

**Effort:** 4 hours

---

### ME-007: Refresh Token Not Hashed

**Severity:** Medium  
**Component:** Auth  
**Status:** Open  

**Description:**
Refresh tokens are stored in plain text in the database.

**Impact:**
- If database is compromised, refresh tokens can be used directly

**Recommended Fix:**
```python
# Hash refresh tokens like passwords
refresh_token_hash = hash_token(refresh_token)
# Store hash, verify by comparing hashes
```

**Effort:** 4 hours

---

## Low Priority Issues

### LO-001: Bulk Scoring Returns Silently Skipped Candidates

**Severity:** Low  
**Component:** Scoring API  
**Status:** Open  

**Description:**
When bulk scoring fails for some candidates, they're silently skipped.

**Current Code (scoring/router.py):**
```python
for candidate_id in bulk_data.candidate_ids:
    candidate = result.scalar_one_or_none()
    if not candidate:
        continue  # Silently skipped, no error returned
```

**Impact:**
- User doesn't know which candidates failed
- Partial success without feedback

**Recommended Fix:**
Return list of failed candidate IDs.

**Effort:** 2 hours

---

### LO-002: No Password Complexity Requirements

**Severity:** Low  
**Component:** Auth  
**Status:** Open  

**Description:**
Password validation only requires minimum length of 8 characters.

**Impact:**
- Users can set weak passwords

**Recommended Fix:**
```python
class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
    )
```

**Effort:** 2 hours

---

### LO-003: Bcrypt Cost Factor Not Configurable

**Severity:** Low  
**Component:** Auth  
**Status:** Open  

**Description:**
Bcrypt cost factor uses library default (12), not configurable.

**Impact:**
- Cannot increase security as hardware improves
- No defense against GPU-based attacks

**Recommended Fix:**
```python
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=14  # Configurable via settings
)
```

**Effort:** 1 hour

---

### LO-004: No Request ID Tracing

**Severity:** Low  
**Component:** Logging  
**Status:** Open  

**Description:**
No request ID is generated or logged for request tracing.

**Impact:**
- Difficult to correlate logs
- Harder to debug production issues

**Recommended Fix:**
```python
@app.middleware
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"[{request_id}] {request.method} {request.url}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

**Effort:** 2 hours

---

## Resolved Issues

| ID | Issue | Resolution Date |
|----|-------|-----------------|
| RS-001 | CORS wildcard in production | Fixed by using env variable |
| RS-002 | Async database driver | Changed from psycopg2 to asyncpg |
| RS-003 | Import path errors | Fixed app.api.deps imports |

---

## Issue Tracker Links

| Component | GitHub Issues Label |
|-----------|-------------------|
| Backend | `area/backend` |
| Frontend | `area/frontend` |
| Security | `area/security` |
| Database | `area/database` |
| DevOps | `area/devops` |

---

## Contribution Guidelines

When adding new issues:
1. Assign severity (Critical/High/Medium/Low)
2. Add component tag
3. Include code snippets showing current behavior
4. Provide recommended fix
5. Estimate implementation effort

---

*End of Known Issues Document*
