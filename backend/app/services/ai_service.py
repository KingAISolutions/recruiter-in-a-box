from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings
import json


class AIService:
    """Service for AI-powered candidate scoring."""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def score_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score a candidate based on their data and optional job requirements.
        Returns detailed breakdown of scores.
        """
        # Default requirements if none provided
        if not job_requirements:
            job_requirements = {
                "required_skills": [],
                "preferred_skills": [],
                "min_experience_years": 0,
                "education_level": "Bachelor",
            }
        
        # Calculate base scores
        skills_score = self._calculate_skills_score(
            candidate_data.get("skills", []),
            job_requirements.get("required_skills", []),
            job_requirements.get("preferred_skills", [])
        )
        
        experience_score = self._calculate_experience_score(
            candidate_data.get("experience_years", 0),
            job_requirements.get("min_experience_years", 0)
        )
        
        education_score = self._calculate_education_score(
            candidate_data.get("education_level"),
            job_requirements.get("education_level", "Bachelor")
        )
        
        # Calculate overall weighted score
        # Weights: Skills 40%, Experience 35%, Education 25%
        overall_score = int(
            (skills_score * 0.4) + 
            (experience_score * 0.35) + 
            (education_score * 0.25)
        )
        
        return {
            "skills_score": skills_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "overall_score": overall_score,
            "breakdown": {
                "skills_match": {
                    "score": skills_score,
                    "candidate_skills": candidate_data.get("skills", []),
                    "required_skills": job_requirements.get("required_skills", []),
                    "preferred_skills": job_requirements.get("preferred_skills", []),
                },
                "experience_match": {
                    "score": experience_score,
                    "candidate_years": candidate_data.get("experience_years", 0),
                    "required_years": job_requirements.get("min_experience_years", 0),
                },
                "education_match": {
                    "score": education_score,
                    "candidate_level": candidate_data.get("education_level"),
                    "required_level": job_requirements.get("education_level", "Bachelor"),
                },
            },
        }
    
    def _calculate_skills_score(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> int:
        """Calculate skills match score."""
        if not required_skills and not preferred_skills:
            return 100 if candidate_skills else 50
        
        candidate_lower = [s.lower() for s in candidate_skills]
        
        # Count required skills matches
        required_matches = sum(
            1 for skill in required_skills 
            if any(skill.lower() in cs for cs in candidate_lower)
        )
        required_score = (required_matches / len(required_skills)) * 100 if required_skills else 50
        
        # Count preferred skills matches
        preferred_matches = sum(
            1 for skill in preferred_skills 
            if any(skill.lower() in cs for cs in candidate_lower)
        )
        preferred_score = (preferred_matches / len(preferred_skills)) * 100 if preferred_skills else 50
        
        # Weighted average (required skills count more)
        if required_skills and preferred_skills:
            score = (required_score * 0.7) + (preferred_score * 0.3)
        else:
            score = max(required_score, preferred_score)
        
        return int(min(score, 100))
    
    def _calculate_experience_score(
        self,
        candidate_years: int,
        required_years: int
    ) -> int:
        """Calculate experience match score."""
        if required_years == 0:
            return 100 if candidate_years > 0 else 50
        
        if candidate_years >= required_years:
            # Meets or exceeds requirement - bonus points for excess
            excess_years = candidate_years - required_years
            # 20% overage is max bonus
            bonus = min((excess_years / required_years) * 20, 20)
            return int(min(100 + bonus, 100))
        
        # Below requirement - linear penalty
        shortfall_ratio = (required_years - candidate_years) / required_years
        score = 100 - (shortfall_ratio * 80)
        return max(int(score), 0)
    
    def _calculate_education_score(
        self,
        candidate_level: str,
        required_level: str
    ) -> int:
        """Calculate education level match score."""
        level_hierarchy = {
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
        }
        
        candidate_val = level_hierarchy.get(candidate_level.lower() if candidate_level else "", 0)
        required_val = level_hierarchy.get(required_level.lower(), 3)  # Default to Bachelor
        
        if required_val == 0:
            return 100
        
        if candidate_val >= required_val:
            return 100
        
        # Penalty for lower education
        ratio = candidate_val / required_val
        return max(int(ratio * 80), 0)
    
    async def generate_outreach_email(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate a personalized outreach email using AI."""
        if not self.client:
            # Fallback to template-based email if no AI available
            return self._generate_template_email(candidate_name, job_title, company_name)
        
        prompt = f"""Write a professional recruiting outreach email for a candidate named {candidate_name} 
        applying for the {job_title} position at {company_name}.
        
        Requirements:
        - Be professional but friendly
        - Keep it concise (under 200 words)
        - Include a clear call to action
        - Personalize based on the candidate's potential background
        
        {additional_context or ''}
        
        Return the response as a JSON object with 'subject' and 'body' fields."""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            email_data = json.loads(content)
            return {
                "subject": email_data.get("subject", f"Exciting Opportunity at {company_name}"),
                "body": email_data.get("body", "")
            }
        except Exception as e:
            # Fallback to template if AI fails
            return self._generate_template_email(candidate_name, job_title, company_name)
    
    def _generate_template_email(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str
    ) -> Dict[str, str]:
        """Generate a template-based email when AI is not available."""
        subject = f"Exciting Opportunity: {job_title} at {company_name}"
        body = f"""Dear {candidate_name},

I hope this email finds you well. I came across your profile and was impressed by your background.

We have an exciting opportunity for a {job_title} position at {company_name} that I believe would be a great fit for your skills and experience.

Would you be interested in learning more about this role? I would love to schedule a brief call to discuss how your background aligns with our needs.

Please let me know if you're interested, and I'll be happy to share more details.

Best regards,
Recruiting Team at {company_name}"""
        
        return {"subject": subject, "body": body}
    
    async def summarize_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an AI-powered summary of a candidate."""
        if not self.client:
            # Fallback to simple summary
            return self._generate_simple_summary(candidate_data)
        
        prompt = f"""Summarize the following candidate for a hiring manager:

Name: {candidate_data.get('full_name', 'Unknown')}
Email: {candidate_data.get('email', 'Unknown')}
Skills: {', '.join(candidate_data.get('skills', [])[:10])}
Experience: {candidate_data.get('experience_years', 0)} years
Education: {candidate_data.get('education_level', 'Not specified')}
Current Position: {candidate_data.get('current_position', 'Not specified')}
Current Company: {candidate_data.get('current_company', 'Not specified')}

{f"Job Requirements: {job_requirements}" if job_requirements else ""}

Provide a concise 2-3 sentence summary highlighting their key strengths and fit."""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200,
            )
            
            return response.choices[0].message.content
        except Exception:
            return self._generate_simple_summary(candidate_data)
    
    def _generate_simple_summary(self, candidate_data: Dict[str, Any]) -> str:
        """Generate a simple text summary."""
        skills = candidate_data.get("skills", [])[:5]
        return (
            f"{candidate_data.get('full_name', 'Candidate')} has "
            f"{candidate_data.get('experience_years', 0)} years of experience "
            f"with skills in {', '.join(skills) if skills else 'various technologies'}. "
            f"Education: {candidate_data.get('education_level', 'Not specified')}. "
            f"Currently working as {candidate_data.get('current_position', 'Not specified')} "
            f"at {candidate_data.get('current_company', 'Unknown')}."
        )


# Singleton instance
ai_service = AIService()
