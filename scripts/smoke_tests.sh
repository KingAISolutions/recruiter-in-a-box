#!/bin/bash
# Recruiter In A Box - Production Smoke Tests

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-https://your-backend.up.railway.app}"
FRONTEND_URL="${FRONTEND_URL:-https://your-app.vercel.app}"
TEST_EMAIL="smoke-test-$(date +%s)@test.com"
TEST_PASSWORD="TestPassword123!"

echo "======================================"
echo "Recruiter In A Box - Smoke Tests"
echo "======================================"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""

# Test counter
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

info() {
    echo -e "  ℹ $1"
}

# ===========================================
# TEST 1: Health Check
# ===========================================
test_health() {
    echo ""
    echo "Test 1: Health Check"
    echo "----------------------------"
    
    RESPONSE=$(curl -s -w "%{http_code}" "$BACKEND_URL/health")
    HTTP_CODE="${RESPONSE: -3}"
    BODY="${RESPONSE:0:-3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$BODY" | grep -q "healthy"; then
            pass "Health endpoint returns healthy status"
        else
            fail "Health endpoint response missing 'healthy' status"
            info "Response: $BODY"
        fi
    else
        fail "Health endpoint returned HTTP $HTTP_CODE"
        info "Response: $BODY"
    fi
}

# ===========================================
# TEST 2: Signup Flow
# ===========================================
test_signup() {
    echo ""
    echo "Test 2: Signup Flow"
    echo "----------------------------"
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/signup" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\",
            \"full_name\": \"Smoke Test User\",
            \"company_name\": \"Test Company\"
        }")
    
    HTTP_CODE=$(echo "$RESPONSE" | grep -o '"id"' | wc -l)
    
    if [ "$HTTP_CODE" -gt 0 ]; then
        pass "User signup successful"
    else
        fail "User signup failed"
        info "Response: $RESPONSE"
    fi
}

# ===========================================
# TEST 3: Login Flow
# ===========================================
test_login() {
    echo ""
    echo "Test 3: Login Flow"
    echo "----------------------------"
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")
    
    # Extract token
    ACCESS_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$ACCESS_TOKEN" ]; then
        pass "User login successful"
        export ACCESS_TOKEN
    else
        fail "User login failed"
        info "Response: $RESPONSE"
        export ACCESS_TOKEN=""
    fi
}

# ===========================================
# TEST 4: Get Current User
# ===========================================
test_get_me() {
    echo ""
    echo "Test 4: Get Current User"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        warn "Skipping - no access token"
        return
    fi
    
    RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/auth/me" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    if echo "$RESPONSE" | grep -q '"email"'; then
        pass "Get current user successful"
    else
        fail "Get current user failed"
        info "Response: $RESPONSE"
    fi
}

# ===========================================
# TEST 5: Create Candidate
# ===========================================
test_create_candidate() {
    echo ""
    echo "Test 5: Create Candidate"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        warn "Skipping - no access token"
        return
    fi
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/candidates" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "skills": ["Python", "JavaScript", "React"],
            "experience_years": 5,
            "education_level": "Bachelor"
        }')
    
    CANDIDATE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$CANDIDATE_ID" ]; then
        pass "Candidate created successfully"
        export CANDIDATE_ID
    else
        fail "Candidate creation failed"
        info "Response: $RESPONSE"
        export CANDIDATE_ID=""
    fi
}

# ===========================================
# TEST 6: AI Scoring
# ===========================================
test_ai_scoring() {
    echo ""
    echo "Test 6: AI Scoring"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ] || [ -z "$CANDIDATE_ID" ]; then
        warn "Skipping - missing token or candidate ID"
        return
    fi
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/scoring/candidate/$CANDIDATE_ID" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    if echo "$RESPONSE" | grep -q '"overall_score"'; then
        pass "AI scoring successful"
    else
        warn "AI scoring failed (may be missing OpenAI API key)"
        info "Response: $RESPONSE"
    fi
}

# ===========================================
# TEST 7: Create Job Position
# ===========================================
test_create_job() {
    echo ""
    echo "Test 7: Create Job Position"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        warn "Skipping - no access token"
        return
    fi
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/jobs" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Senior Software Engineer",
            "description": "Looking for an experienced engineer",
            "department": "Engineering",
            "location": "Remote",
            "status": "open",
            "requirements": {
                "required_skills": ["Python", "React"],
                "min_experience_years": 3
            }
        }')
    
    JOB_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$JOB_ID" ]; then
        pass "Job position created successfully"
        export JOB_ID
    else
        fail "Job position creation failed"
        info "Response: $RESPONSE"
        export JOB_ID=""
    fi
}

# ===========================================
# TEST 8: Create Email Template
# ===========================================
test_create_template() {
    echo ""
    echo "Test 8: Create Email Template"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        warn "Skipping - no access token"
        return
    fi
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/templates" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Initial Outreach",
            "subject": "Exciting Opportunity at {company_name}",
            "body": "Hi {candidate_name},\n\nI came across your profile and...",
            "variables": ["candidate_name", "company_name"]
        }')
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        pass "Email template created successfully"
    else
        fail "Email template creation failed"
        info "Response: $RESPONSE"
    fi
}

# ===========================================
# TEST 9: Dashboard Overview
# ===========================================
test_dashboard() {
    echo ""
    echo "Test 9: Dashboard Overview"
    echo "----------------------------"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        warn "Skipping - no access token"
        return
    fi
    
    RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/dashboard/overview" \
        -H "Authorization: Bearer $ACCESS_TOKEN")
    
    if echo "$RESPONSE" | grep -q '"total_candidates"'; then
        pass "Dashboard overview accessible"
    else
        fail "Dashboard overview failed"
        info "Response: $RESPONSE"
    fi
}

# ===========================================
# TEST 10: CORS Headers
# ===========================================
test_cors() {
    echo ""
    echo "Test 10: CORS Headers"
    echo "----------------------------"
    
    RESPONSE=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/auth/me" \
        -H "Origin: $FRONTEND_URL" \
        -H "Access-Control-Request-Method: GET")
    
    if echo "$RESPONSE" | grep -qi "access-control-allow"; then
        pass "CORS headers present"
    else
        warn "CORS headers may not be configured"
    fi
}

# ===========================================
# Run All Tests
# ===========================================
run_tests() {
    test_health
    test_signup
    test_login
    test_get_me
    test_create_candidate
    test_ai_scoring
    test_create_job
    test_create_template
    test_dashboard
    test_cors
}

# Execute tests
run_tests

# ===========================================
# Summary
# ===========================================
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review.${NC}"
    exit 1
fi
