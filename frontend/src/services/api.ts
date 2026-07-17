import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type {
  LoginRequest,
  SignupRequest,
  TokenResponse,
  User,
  Candidate,
  CandidateCreate,
  CandidateListResponse,
  JobPosition,
  JobPositionCreate,
  CandidateScore,
  EmailTemplate,
  EmailTemplateCreate,
  SentEmail,
  EmailStats,
  DashboardOverview,
  DashboardPipeline,
  HiringMetrics,
  ActivityItem,
  MessageResponse,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  signup: async (data: SignupRequest): Promise<User> => {
    const response = await api.post<User>('/auth/signup', data)
    return response.data
  },
  
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', data)
    return response.data
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
  
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },
  
  updateMe: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/auth/me', data)
    return response.data
  },
  
  resetPassword: async (email: string): Promise<MessageResponse> => {
    const response = await api.post<MessageResponse>('/auth/reset-password', { email })
    return response.data
  },
}

// Candidates API
export const candidatesApi = {
  list: async (params?: {
    page?: number
    page_size?: number
    search?: string
    status?: string
    source?: string
  }): Promise<CandidateListResponse> => {
    const response = await api.get<CandidateListResponse>('/candidates', { params })
    return response.data
  },
  
  get: async (id: string): Promise<Candidate> => {
    const response = await api.get<Candidate>(`/candidates/${id}`)
    return response.data
  },
  
  create: async (data: CandidateCreate): Promise<Candidate> => {
    const response = await api.post<Candidate>('/candidates', data)
    return response.data
  },
  
  update: async (id: string, data: Partial<CandidateCreate>): Promise<Candidate> => {
    const response = await api.put<Candidate>(`/candidates/${id}`, data)
    return response.data
  },
  
  delete: async (id: string): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/candidates/${id}`)
    return response.data
  },
  
  updateStatus: async (id: string, status: string): Promise<Candidate> => {
    const response = await api.put<Candidate>(`/candidates/${id}/status`, { status })
    return response.data
  },
  
  uploadResume: async (file: File): Promise<{ resume_url: string; resume_text: string; extracted_data: any }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/candidates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  
  parseResume: async (file: File): Promise<{ resume_text: string; extracted_data: any }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/candidates/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

// Jobs API
export const jobsApi = {
  list: async (params?: {
    page?: number
    page_size?: number
    search?: string
    status?: string
    department?: string
  }): Promise<{ items: JobPosition[]; total: number }> => {
    const response = await api.get('/jobs', { params })
    return response.data
  },
  
  get: async (id: string): Promise<JobPosition> => {
    const response = await api.get<JobPosition>(`/jobs/${id}`)
    return response.data
  },
  
  create: async (data: JobPositionCreate): Promise<JobPosition> => {
    const response = await api.post<JobPosition>('/jobs', data)
    return response.data
  },
  
  update: async (id: string, data: Partial<JobPositionCreate>): Promise<JobPosition> => {
    const response = await api.put<JobPosition>(`/jobs/${id}`, data)
    return response.data
  },
  
  delete: async (id: string): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/jobs/${id}`)
    return response.data
  },
}

// Scoring API
export const scoringApi = {
  scoreCandidate: async (candidateId: string, jobPositionId?: string): Promise<CandidateScore> => {
    const response = await api.post<CandidateScore>('/scoring/candidate/' + candidateId, {}, {
      params: { job_position_id: jobPositionId },
    })
    return response.data
  },
  
  bulkScore: async (candidateIds: string[], jobPositionId?: string): Promise<CandidateScore[]> => {
    const response = await api.post<CandidateScore[]>('/scoring/bulk', {
      candidate_ids: candidateIds,
      job_position_id: jobPositionId,
    })
    return response.data
  },
  
  getHistory: async (candidateId: string): Promise<CandidateScore[]> => {
    const response = await api.get<CandidateScore[]>(`/scoring/${candidateId}/history`)
    return response.data
  },
}

// Templates API
export const templatesApi = {
  list: async (params?: {
    page?: number
    page_size?: number
    search?: string
  }): Promise<{ items: EmailTemplate[]; total: number }> => {
    const response = await api.get('/templates', { params })
    return response.data
  },
  
  get: async (id: string): Promise<EmailTemplate> => {
    const response = await api.get<EmailTemplate>(`/templates/${id}`)
    return response.data
  },
  
  create: async (data: EmailTemplateCreate): Promise<EmailTemplate> => {
    const response = await api.post<EmailTemplate>('/templates', data)
    return response.data
  },
  
  update: async (id: string, data: Partial<EmailTemplateCreate>): Promise<EmailTemplate> => {
    const response = await api.put<EmailTemplate>(`/templates/${id}`, data)
    return response.data
  },
  
  delete: async (id: string): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/templates/${id}`)
    return response.data
  },
}

// Outreach API
export const outreachApi = {
  sendEmail: async (data: {
    candidate_id: string
    template_id?: string
    job_position_id?: string
    subject?: string
    body?: string
  }): Promise<SentEmail> => {
    const response = await api.post<SentEmail>('/outreach/send', data)
    return response.data
  },
  
  bulkSend: async (data: {
    candidate_ids: string[]
    template_id?: string
    job_position_id?: string
  }): Promise<SentEmail[]> => {
    const response = await api.post<SentEmail[]>('/outreach/bulk', data)
    return response.data
  },
  
  listEmails: async (params?: {
    page?: number
    page_size?: number
    status?: string
    candidate_id?: string
  }): Promise<{ items: SentEmail[]; total: number }> => {
    const response = await api.get('/outreach/emails', { params })
    return response.data
  },
  
  getEmail: async (id: string): Promise<SentEmail> => {
    const response = await api.get<SentEmail>(`/outreach/emails/${id}`)
    return response.data
  },
  
  getStats: async (): Promise<EmailStats> => {
    const response = await api.get<EmailStats>('/outreach/stats')
    return response.data
  },
}

// Dashboard API
export const dashboardApi = {
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await api.get<DashboardOverview>('/dashboard/overview')
    return response.data
  },
  
  getPipeline: async (): Promise<DashboardPipeline> => {
    const response = await api.get<DashboardPipeline>('/dashboard/pipeline')
    return response.data
  },
  
  getMetrics: async (days?: number): Promise<HiringMetrics> => {
    const response = await api.get<HiringMetrics>('/dashboard/metrics', { params: { days } })
    return response.data
  },
  
  getActivity: async (params?: {
    page?: number
    page_size?: number
    entity_type?: string
  }): Promise<{ items: ActivityItem[]; total: number }> => {
    const response = await api.get('/dashboard/activity', { params })
    return response.data
  },
  
  getCandidatesOverTime: async (days?: number): Promise<{ data: { date: string; count: number }[] }> => {
    const response = await api.get('/dashboard/chart/candidates-over-time', { params: { days } })
    return response.data
  },
  
  getEmailPerformance: async (days?: number): Promise<{ data: any[] }> => {
    const response = await api.get('/dashboard/chart/email-performance', { params: { days } })
    return response.data
  },
}

// Subscriptions API
export const subscriptionsApi = {
  getStatus: async () => {
    const response = await api.get('/subscriptions/status')
    return response.data
  },
  
  createCheckout: async (plan: string) => {
    const response = await api.post('/subscriptions/checkout', { plan })
    return response.data
  },
  
  createPortal: async () => {
    const response = await api.post('/subscriptions/portal')
    return response.data
  },
  
  cancel: async (cancel_now: boolean = false) => {
    const response = await api.post('/subscriptions/cancel', { cancel_now })
    return response.data
  },
}

// Team API
export const teamApi = {
  list: async () => {
    const response = await api.get('/teams')
    return response.data
  },
  
  invite: async (data: { email: string; name?: string; role: string }) => {
    const response = await api.post('/teams/invite', data)
    return response.data
  },
  
  update: async (memberId: string, data: { role: string }) => {
    const response = await api.put(`/teams/${memberId}`, data)
    return response.data
  },
  
  remove: async (memberId: string) => {
    const response = await api.delete(`/teams/${memberId}`)
    return response.data
  },
  
  acceptInvite: async (token: string) => {
    const response = await api.post('/teams/accept', null, { params: { token } })
    return response.data
  },
}

// Interviews API
export const interviewsApi = {
  list: async (params?: {
    status?: string
    candidate_id?: string
    upcoming_only?: boolean
  }) => {
    const response = await api.get('/interviews', { params })
    return response.data
  },
  
  get: async (id: string) => {
    const response = await api.get(`/interviews/${id}`)
    return response.data
  },
  
  create: async (data: {
    candidate_id: string
    title?: string
    interview_type: string
    scheduled_at: string
    duration_minutes: number
    location?: string
    notes?: string
  }) => {
    const response = await api.post('/interviews', data)
    return response.data
  },
  
  update: async (id: string, data: any) => {
    const response = await api.put(`/interviews/${id}`, data)
    return response.data
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/interviews/${id}`)
    return response.data
  },
  
  complete: async (id: string, feedback?: string, rating?: number) => {
    const response = await api.post(`/interviews/${id}/complete`, { feedback, rating })
    return response.data
  },
}

// Onboarding API
export const onboardingApi = {
  getProgress: async () => {
    const response = await api.get('/onboarding')
    return response.data
  },
  
  completeStep: async (step: string) => {
    const response = await api.post('/onboarding/complete-step', { step })
    return response.data
  },
  
  checkSteps: async () => {
    const response = await api.post('/onboarding/check-step')
    return response.data
  },
  
  dismissTour: async () => {
    const response = await api.post('/onboarding/dismiss-tour')
    return response.data
  },
  
  reset: async () => {
    const response = await api.post('/onboarding/reset')
    return response.data
  },
}

export default api
