import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { interviewsApi, candidatesApi } from '@/services/api'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Input, Select } from '@/components/common/Input'
import { Modal } from '@/components/common/Modal'
import { LoadingSpinner, EmptyState } from '@/components/common/Badge'
import { Plus, Calendar, Clock, Video, Phone, MapPin, Trash2, Check, Star } from 'lucide-react'
import { formatDate, cn } from '@/utils'

interface Interview {
  id: string
  candidate_id: string
  title?: string
  interview_type: string
  scheduled_at: string
  duration_minutes: number
  location?: string
  status: string
  notes?: string
  feedback?: string
  rating?: number
}

interface InterviewListResponse {
  interviews: Interview[]
  total: number
  upcoming: number
  completed: number
}

const INTERVIEW_TYPES = [
  { value: 'phone', label: 'Phone Screen', icon: Phone },
  { value: 'video', label: 'Video Call', icon: Video },
  { value: 'onsite', label: 'On-site', icon: MapPin },
  { value: 'technical', label: 'Technical', icon: Calendar },
]

export default function InterviewsPage() {
  const queryClient = useQueryClient()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('upcoming')

  const { data: interviewsData, isLoading } = useQuery({
    queryKey: ['interviews', filter],
    queryFn: () => {
      if (filter === 'upcoming') return interviewsApi.list({ upcoming_only: true })
      if (filter === 'completed') return interviewsApi.list({ status: 'completed' })
      return interviewsApi.list()
    },
  }) as { data: InterviewListResponse | undefined; isLoading: boolean }

  const deleteMutation = useMutation({
    mutationFn: (id: string) => interviewsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] })
    },
  })

  const completeMutation = useMutation({
    mutationFn: ({ id, feedback, rating }: { id: string; feedback?: string; rating?: number }) =>
      interviewsApi.complete(id, feedback, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const interviews = interviewsData?.interviews || []
  const stats = {
    total: interviewsData?.total || 0,
    upcoming: interviewsData?.upcoming || 0,
    completed: interviewsData?.completed || 0,
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interviews</h1>
          <p className="text-gray-500 mt-1">Schedule and manage candidate interviews</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Schedule Interview
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Total" value={stats.total} />
        <StatCard title="Upcoming" value={stats.upcoming} color="primary" />
        <StatCard title="Completed" value={stats.completed} color="success" />
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['upcoming', 'completed', 'all'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              filter === f
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100'
            )}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Interviews List */}
      {interviews.length > 0 ? (
        <div className="space-y-4">
          {interviews.map((interview) => (
            <InterviewCard
              key={interview.id}
              interview={interview}
              onDelete={() => deleteMutation.mutate(interview.id)}
              onComplete={(feedback, rating) =>
                completeMutation.mutate({ id: interview.id, feedback, rating })
              }
            />
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Calendar className="w-12 h-12" />}
            title="No interviews scheduled"
            description="Schedule your first interview with a candidate"
            action={
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Schedule Interview
              </Button>
            }
          />
        </Card>
      )}

      {/* Create Modal */}
      <CreateInterviewModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['interviews'] })
          setIsCreateModalOpen(false)
        }}
      />
    </div>
  )
}

function StatCard({ title, value, color = 'default' }: {
  title: string
  value: number
  color?: 'default' | 'primary' | 'success'
}) {
  const colors = {
    default: 'bg-gray-100 text-gray-600',
    primary: 'bg-primary-100 text-primary-600',
    success: 'bg-success-100 text-success-600',
  }

  return (
    <Card padding="sm">
      <div className="text-center">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        <p className={cn('text-sm mt-1', colors[color].split(' ')[1])}>{title}</p>
      </div>
    </Card>
  )
}

function InterviewCard({
  interview,
  onDelete,
  onComplete,
}: {
  interview: Interview
  onDelete: () => void
  onComplete: (feedback: string | undefined, rating: number | undefined) => void
}) {
  const [showFeedback, setShowFeedback] = useState(false)
  const [feedbackText, setFeedbackText] = useState('')
  const [rating, setRating] = useState(0)

  const typeConfig = INTERVIEW_TYPES.find((t) => t.value === interview.interview_type) || INTERVIEW_TYPES[0]
  const TypeIcon = typeConfig.icon

  const statusColors: Record<string, string> = {
    scheduled: 'bg-primary-100 text-primary-700',
    confirmed: 'bg-success-100 text-success-700',
    completed: 'bg-gray-100 text-gray-600',
    canceled: 'bg-danger-100 text-danger-700',
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className={cn('p-3 rounded-xl', statusColors[interview.status]?.split(' ')[0])}>
            <TypeIcon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{interview.title}</h3>
            <p className="text-sm text-gray-500 mt-1">{typeConfig.label}</p>

            <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {formatDate(interview.scheduled_at)}
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {interview.scheduled_at.split('T')[1].substring(0, 5)} ({interview.duration_minutes} min)
              </div>
            </div>

            {interview.location && (
              <div className="flex items-center gap-1 mt-2 text-sm text-gray-500">
                <MapPin className="w-4 h-4" />
                {interview.location}
              </div>
            )}

            {interview.feedback && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700">{interview.feedback}</p>
                {interview.rating && (
                  <div className="flex items-center gap-1 mt-2">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <Star
                        key={n}
                        className={cn(
                          'w-4 h-4',
                          n <= interview.rating! ? 'fill-warning-400 text-warning-400' : 'text-gray-300'
                        )}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={cn('px-2 py-1 rounded-full text-xs font-medium', statusColors[interview.status])}>
            {interview.status}
          </span>

          {interview.status !== 'completed' && interview.status !== 'canceled' && (
            <>
              {showFeedback ? (
                <div className="flex flex-col gap-2">
                  <textarea
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    placeholder="Add feedback notes..."
                    className="text-sm border rounded px-2 py-1 w-full"
                    rows={2}
                  />
                  <div className="flex items-center gap-2">
                    <select
                      value={rating}
                      onChange={(e) => setRating(Number(e.target.value))}
                      className="text-sm border rounded px-2 py-1"
                    >
                      <option value={0}>No rating</option>
                      {[1, 2, 3, 4, 5].map((n) => (
                        <option key={n} value={n}>{n} star{n > 1 ? 's' : ''}</option>
                      ))}
                    </select>
                    <Button
                      size="sm"
                      onClick={() => {
                        onComplete(feedbackText || undefined, rating || undefined)
                        setShowFeedback(false)
                      }}
                    >
                      <Check className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowFeedback(true)}
                >
                  Complete
                </Button>
              )}
            </>
          )}

          <button
            onClick={onDelete}
            className="p-2 text-gray-400 hover:text-danger-600 rounded-lg hover:bg-danger-50"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </Card>
  )
}

interface CreateInterviewModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

function CreateInterviewModal({ isOpen, onClose, onSuccess }: CreateInterviewModalProps) {
  const [candidateId, setCandidateId] = useState('')
  const [title, setTitle] = useState('')
  const [interviewType, setInterviewType] = useState('video')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [duration, setDuration] = useState(60)
  const [location, setLocation] = useState('')
  const [notes, setNotes] = useState('')

  const { data: candidatesData } = useQuery({
    queryKey: ['candidates-list'],
    queryFn: () => candidatesApi.list({ page: 1, page_size: 100 }),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => interviewsApi.create(data),
    onSuccess: () => {
      onSuccess()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const scheduled_at = new Date(`${date}T${time}`).toISOString()
    createMutation.mutate({
      candidate_id: candidateId,
      title: title || undefined,
      interview_type: interviewType,
      scheduled_at,
      duration_minutes: duration,
      location: location || undefined,
      notes: notes || undefined,
    })
  }

  const candidates = candidatesData?.items || []

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Schedule Interview" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Candidate</label>
          <select
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select a candidate...</option>
            {candidates.map((c: any) => (
              <option key={c.id} value={c.id}>{c.full_name}</option>
            ))}
          </select>
        </div>

        <Input
          label="Interview Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., First Round Interview"
        />

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <div className="grid grid-cols-2 gap-2">
              {INTERVIEW_TYPES.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setInterviewType(type.value)}
                    className={cn(
                      'flex items-center gap-2 p-3 border rounded-lg transition-colors',
                      interviewType === type.value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:bg-gray-50'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{type.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <Input
              label="Time"
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Duration"
            value={String(duration)}
            onChange={(e) => setDuration(Number(e.target.value))}
            options={[
              { value: '30', label: '30 minutes' },
              { value: '45', label: '45 minutes' },
              { value: '60', label: '60 minutes' },
              { value: '90', label: '90 minutes' },
              { value: '120', label: '2 hours' },
            ]}
          />
          <Input
            label="Location/Meeting Link"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="https://zoom.us/j/..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Any preparation notes or talking points..."
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={createMutation.isPending}>
            Schedule Interview
          </Button>
        </div>
      </form>
    </Modal>
  )
}
