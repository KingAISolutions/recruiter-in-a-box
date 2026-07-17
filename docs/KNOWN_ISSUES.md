# Recruiter In A Box - Known Issues List

**Version:** 2.0  
**Date:** 2026-07-16  
**Status:** Majority Resolved

---

## Executive Summary

| Severity | Before | After | Resolution |
|----------|--------|-------|------------|
| Critical | 3 | 0 | ALL FIXED |
| High | 5 | 0 | ALL FIXED |
| Medium | 7 | 4 | Partially Fixed |
| Low | 4 | 3 | Partially Fixed |

**Total Known Issues:** 7 (down from 19)

---

## Resolved Issues

### Critical Issues - ALL FIXED ✅

| ID | Issue | Resolution | Date |
|----|-------|------------|------|
| CR-001 | No rate limiting | SlowAPI middleware | 2026-07-16 |
| CR-002 | Default SECRET_KEY | Removed, validation added | 2026-07-16 |
| CR-003 | localStorage tokens | httpOnly cookies | 2026-07-16 |

### High Priority Issues - ALL FIXED ✅

| ID | Issue | Resolution | Date |
|----|-------|------------|------|
| HI-001 | Token revocation | TokenBlacklist + JTI | 2026-07-16 |
| HI-002 | No RBAC | Permission decorators | 2026-07-16 |
| HI-003 | No migrations | Alembic setup | 2026-07-16 |
| HI-004 | No database SSL | sslmode=require | 2026-07-16 |
| HI-005 | File validation | MIME + magic bytes | 2026-07-16 |

---

## Remaining Medium Priority Issues

### RC-001: No PII Field Encryption

**Severity:** Medium  
**Component:** Database  
**Status:** Open  

**Description:**
PII fields (email, name, resume text) are stored without field-level encryption.

**Impact:**
- Data breach exposure
- Compliance concerns (GDPR, CCPA)

**Recommended Fix:**
```python
# Use SQLAlchemy encrypted column type
class EncryptedColumn(TypeDecorator):
    impl = LargeBinary
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt(value)
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt(value)
```

**Effort:** 16 hours

---

### RC-002: No Automated Backups

**Severity:** Medium  
**Component:** Infrastructure  
**Status:** Open  

**Description:**
No automated backup strategy is configured.

**Impact:**
- Data loss risk
- Compliance issues

**Recommended Fix:**
```bash
# Add to cron
0 2 * * * pg_dump -h hostname -U user db | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz
```

**Effort:** 4 hours

---

### RC-003: Dashboard Chart Data is Mock

**Severity:** Medium  
**Component:** Dashboard API  
**Status:** Open  

**Description:**
Chart endpoints return mock data instead of real queries.

**Recommended Fix:**
Implement actual database queries with date grouping.

**Effort:** 6 hours

---

### RC-004: No Prometheus Metrics

**Severity:** Medium  
**Component:** Monitoring  
**Status:** Open  

**Description:**
No application metrics for monitoring.

**Recommended Fix:**
```python
from prometheus_client import Counter, Histogram
REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
```

**Effort:** 8 hours

---

## Remaining Low Priority Issues

### LC-001: Bulk Scoring Returns Silently Skipped Candidates

**Severity:** Low  
**Component:** Scoring API  
**Status:** Open  

**Description:**
When bulk scoring fails, skipped candidates not reported.

**Effort:** 2 hours

---

### LC-002: Interview Parameter Bug

**Severity:** Low  
**Component:** Interviews API  
**Status:** Open  

**Description:**
Parameter name mismatch in Swagger docs.

**Effort:** 1 hour

---

### LC-003: Bcrypt Cost Factor

**Severity:** Low  
**Component:** Auth  
**Status:** Open  

**Description:**
Bcrypt cost factor hardcoded at 12.

**Effort:** 1 hour

---

## Security Recommendations Post-Deployment

### Immediate (Week 1)

1. Configure automated database backups
2. Set up Sentry project and verify error tracking
3. Enable PII field encryption
4. Configure monitoring alerts

### Short-term (Month 1)

1. Add Prometheus metrics
2. Implement Redis caching for rate limiting
3. Configure CDN for static assets
4. Add RLS policies

### Long-term (Quarter)

1. Security audit by third party
2. Penetration testing
3. Compliance certification (SOC2, GDPR)

---

## Issue Resolution History

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-07-16 | All CR & HI issues | Implemented security fixes |

---

*End of Known Issues Document*
