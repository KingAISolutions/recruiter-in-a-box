// User types
export interface User {
  id: string
  email: string
  full_name: string
  company_name?: string
  email_verified: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  full_name: string
  company_name?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Candidate types
export interface Candidate {
  id: string
  user_id: string
  full_name: string
  email: string
  phone?: string
  resume_url?: string
  resume_text?: string
  skills: string[]
  experience_years: number
  education_level?: string
  current_position?: string
  current_company?: string
  linkedin_url?: string
  status: CandidateStatus
  source?: string
  notes?: string
  created_at: string
  updated_at: string
}

export type CandidateStatus = 'new' | 'screening' | 'interview' | 'offer' | 'hired' | 'rejected'

export interface CandidateCreate {
  full_name: string
  email: string
  phone?: string
  skills?: string[]
  experience_years?: number
  education_level?: string
  current_position?: string
  current_company?: string
  linkedin_url?: string
  status?: CandidateStatus
  source?: string
  notes?: string
}

export interface CandidateListResponse {
  items: Candidate[]
  total: number
  page: number
  page_size: number
}

// Job Position types
export interface JobPosition {
  id: string
  user_id: string
  title: string
  description?: string
  requirements: JobRequirements
  department?: string
  location?: string
  salary_range?: string
  status: JobStatus
  created_at: string
  updated_at: string
}

export interface JobRequirements {
  required_skills?: string[]
  preferred_skills?: string[]
  min_experience_years?: number
  education_level?: string
}

export type JobStatus = 'open' | 'closed' | 'on_hold'

export interface JobPositionCreate {
  title: string
  description?: string
  requirements?: JobRequirements
  department?: string
  location?: string
  salary_range?: string
  status?: JobStatus
}

// Scoring types
export interface CandidateScore {
  id: string
  candidate_id: string
  job_position_id?: string
  skills_score: number
  experience_score: number
  education_score: number
  overall_score: number
  breakdown: ScoreBreakdown
  created_at: string
}

export interface ScoreBreakdown {
  skills_match: {
    score: number
    candidate_skills: string[]
    required_skills: string[]
    preferred_skills: string[]
  }
  experience_match: {
    score: number
    candidate_years: number
    required_years: number
  }
  education_match: {
    score: number
    candidate_level?: string
    required_level?: string
  }
}

// Email Template types
export interface EmailTemplate {
  id: string
  user_id: string
  name: string
  subject: string
  body: string
  variables: string[]
  created_at: string
  updated_at: string
}

export interface EmailTemplateCreate {
  name: string
  subject: string
  body: string
  variables?: string[]
}

// Sent Email types
export interface SentEmail {
  id: string
  user_id: string
  candidate_id: string
  template_id?: string
  job_position_id?: string
  subject: string
  body: string
  status: EmailStatus
  sent_at?: string
  delivered_at?: string
  opened_at?: string
  replied_at?: string
  created_at: string
}

export type EmailStatus = 'pending' | 'sent' | 'delivered' | 'opened' | 'replied' | 'failed'

export interface EmailStats {
  total_sent: number
  total_delivered: number
  total_opened: number
  total_replied: number
  total_failed: number
  delivery_rate: number
  open_rate: number
  reply_rate: number
}

// Dashboard types
export interface DashboardOverview {
  total_candidates: number
  active_candidates: number
  total_jobs: number
  open_jobs: number
  total_emails_sent: number
  email_open_rate: number
}

export interface PipelineStage {
  status: string
  count: number
  label: string
}

export interface DashboardPipeline {
  stages: PipelineStage[]
  total: number
}

export interface HiringMetrics {
  avg_time_to_hire: number | null
  total_hired: number
  total_rejected: number
  offer_acceptance_rate: number
  candidates_per_position: number
}

export interface ActivityItem {
  id: string
  action: string
  entity_type?: string
  entity_id?: string
  details: Record<string, any>
  created_at: string
}

// API Response types
export interface ApiError {
  detail: string
}

export interface MessageResponse {
  message: string
  success: boolean
}
