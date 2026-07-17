import pytest
from httpx import AsyncClient
from app.models import User


@pytest.mark.asyncio
async def test_create_candidate(client: AsyncClient, auth_headers, test_user):
    """Test creating a candidate."""
    response = await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "skills": ["Python", "JavaScript", "React"],
            "experience_years": 5,
            "education_level": "Bachelor",
            "current_position": "Software Engineer",
            "current_company": "Tech Corp",
            "status": "new",
            "source": "LinkedIn"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["skills"] == ["Python", "JavaScript", "React"]
    assert data["experience_years"] == 5


@pytest.mark.asyncio
async def test_list_candidates(client: AsyncClient, auth_headers, test_user):
    """Test listing candidates."""
    # Create a candidate first
    await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        }
    )
    
    response = await client.get("/api/candidates", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_candidate(client: AsyncClient, auth_headers, test_user):
    """Test getting a specific candidate."""
    # Create a candidate
    create_response = await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "John Smith",
            "email": "johnsmith@example.com"
        }
    )
    candidate_id = create_response.json()["id"]
    
    response = await client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Smith"


@pytest.mark.asyncio
async def test_update_candidate(client: AsyncClient, auth_headers, test_user):
    """Test updating a candidate."""
    # Create a candidate
    create_response = await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "Bob Wilson",
            "email": "bob@example.com",
            "status": "new"
        }
    )
    candidate_id = create_response.json()["id"]
    
    # Update
    response = await client.put(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers,
        json={
            "full_name": "Robert Wilson",
            "status": "screening"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Robert Wilson"
    assert data["status"] == "screening"


@pytest.mark.asyncio
async def test_update_candidate_status(client: AsyncClient, auth_headers, test_user):
    """Test updating candidate status."""
    # Create a candidate
    create_response = await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "Alice Brown",
            "email": "alice@example.com"
        }
    )
    candidate_id = create_response.json()["id"]
    
    # Update status
    response = await client.put(
        f"/api/candidates/{candidate_id}/status",
        headers=auth_headers,
        json={"status": "interview"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "interview"


@pytest.mark.asyncio
async def test_delete_candidate(client: AsyncClient, auth_headers, test_user):
    """Test deleting a candidate."""
    # Create a candidate
    create_response = await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={
            "full_name": "To Delete",
            "email": "delete@example.com"
        }
    )
    candidate_id = create_response.json()["id"]
    
    # Delete
    response = await client.delete(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify deleted
    get_response = await client.get(f"/api/candidates/{candidate_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_search_candidates(client: AsyncClient, auth_headers, test_user):
    """Test searching candidates."""
    # Create candidates
    await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={"full_name": "Search Test 1", "email": "search1@example.com"}
    )
    await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={"full_name": "Search Test 2", "email": "search2@example.com"}
    )
    
    # Search
    response = await client.get(
        "/api/candidates",
        headers=auth_headers,
        params={"search": "Search Test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_filter_candidates_by_status(client: AsyncClient, auth_headers, test_user):
    """Test filtering candidates by status."""
    # Create candidates with different statuses
    await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={"full_name": "New Candidate", "email": "new@example.com", "status": "new"}
    )
    await client.post(
        "/api/candidates",
        headers=auth_headers,
        json={"full_name": "Interview Candidate", "email": "interview@example.com", "status": "interview"}
    )
    
    # Filter by status
    response = await client.get(
        "/api/candidates",
        headers=auth_headers,
        params={"status": "new"}
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "new"
