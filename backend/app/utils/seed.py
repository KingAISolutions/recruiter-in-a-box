"""
Sample data seeder for development and testing.
Run with: python -m app.utils.seed
"""
import asyncio
from datetime import datetime, timedelta
import random
from uuid import uuid4

from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models import User, Candidate, JobPosition, EmailTemplate, SentEmail


SAMPLE_CANDIDATES = [
    {
        "full_name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1 (555) 123-4567",
        "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL"],
        "experience_years": 5,
        "education_level": "Master",
        "current_position": "Senior Software Engineer",
        "current_company": "TechCorp Inc.",
        "status": "interview",
    },
    {
        "full_name": "Bob Williams",
        "email": "bob.williams@example.com",
        "phone": "+1 (555) 234-5678",
        "skills": ["Java", "Spring Boot", "AWS", "Kubernetes", "Docker"],
        "experience_years": 8,
        "education_level": "Bachelor",
        "current_position": "Tech Lead",
        "current_company": "CloudScale Systems",
        "status": "new",
    },
    {
        "full_name": "Carol Davis",
        "email": "carol.davis@example.com",
        "phone": "+1 (555) 345-6789",
        "skills": ["Python", "Machine Learning", "TensorFlow", "Data Science", "SQL"],
        "experience_years": 4,
        "education_level": "PhD",
        "current_position": "ML Engineer",
        "current_company": "AI Dynamics",
        "status": "screening",
    },
    {
        "full_name": "David Martinez",
        "email": "david.martinez@example.com",
        "phone": "+1 (555) 456-7890",
        "skills": ["React", "TypeScript", "Vue.js", "CSS", "Figma"],
        "experience_years": 3,
        "education_level": "Bachelor",
        "current_position": "Frontend Developer",
        "current_company": "DesignHub",
        "status": "offer",
    },
    {
        "full_name": "Emma Thompson",
        "email": "emma.thompson@example.com",
        "phone": "+1 (555) 567-8901",
        "skills": ["Product Management", "Agile", "Scrum", "SQL", "Analytics"],
        "experience_years": 6,
        "education_level": "Master",
        "current_position": "Senior Product Manager",
        "current_company": "ProductLabs",
        "status": "hired",
    },
]

SAMPLE_JOBS = [
    {
        "title": "Senior Software Engineer",
        "description": "We are looking for a senior software engineer to join our growing team.",
        "department": "Engineering",
        "location": "San Francisco, CA",
        "salary_range": "$150k - $200k",
        "status": "open",
        "requirements": {
            "required_skills": ["Python", "JavaScript"],
            "preferred_skills": ["AWS", "Docker"],
            "min_experience_years": 5,
            "education_level": "bachelor",
        },
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Join our AI team to build cutting-edge machine learning solutions.",
        "department": "AI/ML",
        "location": "Remote",
        "salary_range": "$160k - $220k",
        "status": "open",
        "requirements": {
            "required_skills": ["Python", "Machine Learning"],
            "preferred_skills": ["TensorFlow", "PyTorch"],
            "min_experience_years": 3,
            "education_level": "master",
        },
    },
    {
        "title": "Frontend Developer",
        "description": "Create beautiful user interfaces for our web applications.",
        "department": "Engineering",
        "location": "New York, NY",
        "salary_range": "$120k - $160k",
        "status": "open",
        "requirements": {
            "required_skills": ["React", "TypeScript", "CSS"],
            "preferred_skills": ["Vue.js", "Figma"],
            "min_experience_years": 2,
            "education_level": "bachelor",
        },
    },
]

SAMPLE_TEMPLATES = [
    {
        "name": "Initial Outreach",
        "subject": "Exciting Opportunity at {company_name} - {position}",
        "body": """Dear {first_name},

I came across your profile and was impressed by your experience in {position}. 

We have an exciting opportunity at {company_name} that I believe would be a great fit for your skills. Would you be interested in learning more?

The role involves working with {department} team on cutting-edge projects. Based on your background, I think you'd be a fantastic addition to our team.

Would you have 15-20 minutes this week for a brief call to discuss?

Best regards,
Recruiting Team""",
    },
    {
        "name": "Interview Invitation",
        "subject": "Interview Invitation - {position} at {company_name}",
        "body": """Hi {first_name},

Thank you for your interest in the {position} position at {company_name}. We've reviewed your application and would love to move forward with an interview.

The interview will be approximately 45 minutes and will focus on:
- Your technical experience
- Problem-solving abilities
- Cultural fit

Please let me know your availability for the coming week, and we'll find a time that works for you.

Looking forward to speaking with you!

Best,
Recruiting Team""",
    },
    {
        "name": "Offer Letter",
        "subject": "Offer: {position} at {company_name}",
        "body": """Dear {first_name},

We are thrilled to extend an offer for the position of {position} at {company_name}!

After our interviews, everyone was impressed by your skills and enthusiasm. We believe you'll be a valuable addition to our team.

Offer Details:
- Position: {position}
- Location: {location}
- Start Date: To be determined

Please review the attached offer letter for complete details. We're excited about the possibility of you joining us!

Let me know if you have any questions.

Best regards,
Recruiting Team""",
    },
]


async def seed_database():
    """Seed the database with sample data."""
    print("Initializing database...")
    await init_db()
    
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return
        
        print("Creating demo user...")
        demo_user = User(
            id=uuid4(),
            email="demo@recruiterbox.com",
            password_hash=get_password_hash("demo123"),
            full_name="Demo User",
            company_name="Recruiter In A Box Inc.",
            email_verified=True,
        )
        session.add(demo_user)
        await session.flush()
        
        print("Creating sample candidates...")
        candidates = []
        for candidate_data in SAMPLE_CANDIDATES:
            candidate = Candidate(
                id=uuid4(),
                user_id=demo_user.id,
                **candidate_data,
            )
            candidates.append(candidate)
            session.add(candidate)
        
        print("Creating sample jobs...")
        jobs = []
        for job_data in SAMPLE_JOBS:
            job = JobPosition(
                id=uuid4(),
                user_id=demo_user.id,
                **job_data,
            )
            jobs.append(job)
            session.add(job)
        
        print("Creating sample templates...")
        templates = []
        for template_data in SAMPLE_TEMPLATES:
            template = EmailTemplate(
                id=uuid4(),
                user_id=demo_user.id,
                **template_data,
            )
            templates.append(template)
            session.add(template)
        
        print("Creating sample sent emails...")
        for i in range(15):
            sent_email = SentEmail(
                id=uuid4(),
                user_id=demo_user.id,
                candidate_id=candidates[random.randint(0, len(candidates) - 1)].id,
                template_id=random.choice(templates).id,
                job_position_id=random.choice(jobs).id if random.random() > 0.3 else None,
                subject=f"Regarding your application - {random.choice(['Interview', 'Update', 'Opportunity'])}",
                body="This is a sample email body.",
                status=random.choice(['sent', 'delivered', 'opened', 'replied']),
                sent_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            )
            session.add(sent_email)
        
        await session.commit()
        print("Database seeded successfully!")
        print("\nDemo credentials:")
        print("  Email: demo@recruiterbox.com")
        print("  Password: demo123")


if __name__ == "__main__":
    asyncio.run(seed_database())
