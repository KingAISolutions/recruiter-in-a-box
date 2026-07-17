import re
from typing import Dict, List, Any, Optional
import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    return text


def parse_resume_text(text: str) -> Dict[str, Any]:
    """Parse extracted resume text to extract structured information."""
    result = {
        "full_name": None,
        "email": None,
        "phone": None,
        "skills": [],
        "experience_years": 0,
        "education_level": None,
        "current_position": None,
        "current_company": None,
        "linkedin_url": None,
    }

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        result["email"] = email_match.group(0)

    # Extract phone number
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        result["phone"] = phone_match.group(0)

    # Extract LinkedIn URL
    linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        result["linkedin_url"] = f"https://www.{linkedin_match.group(0)}"

    # Extract skills (common tech skills)
    skills_list = [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
        "Node.js", "Django", "Flask", "FastAPI", "Spring", "SQL", "PostgreSQL",
        "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
        "GCP", "Git", "CI/CD", "Agile", "Scrum", "Machine Learning", "AI",
        "Data Science", "TensorFlow", "PyTorch", "HTML", "CSS", "REST API",
        "GraphQL", "Linux", "DevOps", "Microservices", "AWS", "React Native",
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    result["skills"] = found_skills[:20]  # Limit to 20 skills

    # Extract years of experience
    exp_pattern = r'(\d+)\+?\s*(years?|yrs?)\s*(of)?\s*(experience|exp)'
    exp_match = re.search(exp_pattern, text, re.IGNORECASE)
    if exp_match:
        result["experience_years"] = int(exp_match.group(1))

    # Estimate experience from context if not explicitly stated
    if result["experience_years"] == 0:
        # Look for date ranges in work experience
        date_pattern = r'(19|20)\d{2}\s*[-–to]+\s*(19|20)\d{2}|present'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        if dates:
            # Calculate approximate years
            years = []
            for date_range in dates:
                start_year = int(date_range[0]) if date_range[0] else 2000
                end_year = int(date_range[1]) if date_range[1] else 2024
                years.append(end_year - start_year)
            if years:
                result["experience_years"] = max(years)

    # Extract education level
    education_patterns = {
        "PhD": r'\bPh\.?D\.?\b|\bDoctorate\b|\bDoctor of\b',
        "Master": r'\bM\.?S\.?\b|\bM\.?A\.?\b|\bMaster\'?s?\b|\bMBA\b|\bMaster of\b',
        "Bachelor": r'\bB\.?S\.?\b|\bB\.?A\.?\b|\bBachelor\'?s?\b|\bUndergraduate\b|\bBachelor of\b',
        "Associate": r'\bAssociate\b|\bA\.?S\.?\b|\bA\.?A\.?\b',
    }
    for level, pattern in education_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            result["education_level"] = level
            break

    # Try to extract name from first line
    lines = text.split('\n')
    if lines:
        first_line = lines[0].strip()
        # If first line looks like a name (short, no special chars)
        if first_line and len(first_line) < 50 and '@' not in first_line and not first_line.isdigit():
            # Check if it looks like a name pattern
            name_pattern = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$'
            if re.match(name_pattern, first_line):
                result["full_name"] = first_line

    return result


def calculate_similarity_score(candidate_skills: List[str], required_skills: List[str]) -> int:
    """Calculate similarity score between candidate skills and required skills."""
    if not required_skills:
        return 100  # No requirements means perfect match
    
    if not candidate_skills:
        return 0
    
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    required_skills_lower = [s.lower() for s in required_skills]
    
    matches = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
    return int((matches / len(required_skills)) * 100)


def calculate_experience_score(candidate_years: int, required_years: int) -> int:
    """Calculate score based on years of experience."""
    if required_years == 0:
        return 100
    
    if candidate_years >= required_years:
        # Candidate meets or exceeds requirement
        excess = candidate_years - required_years
        # Cap bonus at 20% over requirement
        bonus = min(excess / required_years, 0.2)
        return min(int(100 + (bonus * 20)), 100)
    
    # Candidate falls short
    shortfall = (required_years - candidate_years) / required_years
    return max(int(100 - (shortfall * 100)), 0)


def calculate_education_score(candidate_level: str, required_level: str) -> int:
    """Calculate score based on education level."""
    levels = {
        "PhD": 4,
        "Master": 3,
        "Bachelor": 2,
        "Associate": 1,
        None: 0,
    }
    
    candidate_val = levels.get(candidate_level, 0)
    required_val = levels.get(required_level, 0)
    
    if required_val == 0:
        return 100
    
    if candidate_val >= required_val:
        return 100
    
    # Penalize for lower education
    return max(int((candidate_val / required_val) * 100), 0)


def parse_template_variables(template_body: str) -> List[str]:
    """Extract variables from email template body."""
    pattern = r'\{([a-zA-Z_]+)\}'
    matches = re.findall(pattern, template_body)
    return list(set(matches))


def interpolate_template(template_body: str, variables: Dict[str, str]) -> str:
    """Replace template variables with actual values."""
    result = template_body
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", value)
    return result


def generate_filename(original_filename: str, user_id: str) -> str:
    """Generate unique filename for uploaded files."""
    import uuid
    extension = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:8]
    return f"{user_id}/{unique_id}{extension}"


def validate_file_type(filename: str) -> bool:
    """Validate that the file is a PDF."""
    allowed_extensions = {'.pdf'}
    extension = Path(filename).suffix.lower()
    return extension in allowed_extensions


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
