import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi } from '@/services/api'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Input, Select, Textarea } from '@/components/common/Input'
import { StatusBadge, EmptyState, LoadingSpinner } from '@/components/common/Badge'
import { Modal } from '@/components/common/Modal'
import { ConfirmDialog } from '@/components/common/Modal'
import { Plus, Search, MapPin, DollarSign, Briefcase, Trash2, Edit } from 'lucide-react'
import { formatDate } from '@/utils'
import type { JobPosition, JobPositionCreate } from '@/types'

const STATUS_OPTIONS = [
  { value: '', label: 'All Status' },
  { value: 'open', label: 'Open' },
  { value: 'closed', label: 'Closed' },
  { value: 'on_hold', label: 'On Hold' },
]

export default function JobsPage() {
  const queryClient = useQueryClient()
  const [page] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editJob, setEditJob] = useState<JobPosition | null>(null)
  const [deleteJob, setDeleteJob] = useState<JobPosition | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['jobs', page, search, status],
    queryFn: () => jobsApi.list({ page, page_size: 20, search: search || undefined, status: status || undefined }),
  })

  const createMutation = useMutation({
    mutationFn: (data: JobPositionCreate) => jobsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setIsAddModalOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<JobPositionCreate> }) => 
      jobsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setEditJob(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => jobsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setDeleteJob(null)
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Positions</h1>
          <p className="text-gray-500 mt-1">{data?.total || 0} total positions</p>
        </div>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Position
        </Button>
      </div>

      {/* Filters */}
      <Card padding="sm">
        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search positions..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <Select
            options={STATUS_OPTIONS}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-40"
          />
        </div>
      </Card>

      {/* Jobs Grid */}
      {data?.items && data.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((job) => (
            <Card key={job.id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Briefcase className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{job.title}</h3>
                    {job.department && (
                      <p className="text-sm text-gray-500">{job.department}</p>
                    )}
                  </div>
                </div>
                <StatusBadge status={job.status} />
              </div>

              {job.description && (
                <p className="text-sm text-gray-600 line-clamp-2 mb-4">{job.description}</p>
              )}

              <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                {job.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {job.location}
                  </div>
                )}
                {job.salary_range && (
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-4 h-4" />
                    {job.salary_range}
                  </div>
                )}
              </div>

              {job.requirements?.required_skills && job.requirements.required_skills.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {job.requirements.required_skills.slice(0, 3).map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {skill}
                    </span>
                  ))}
                  {job.requirements.required_skills.length > 3 && (
                    <span className="text-xs text-gray-500">+{job.requirements.required_skills.length - 3}</span>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <p className="text-xs text-gray-500">
                  Created {formatDate(job.created_at)}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setEditJob(job)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setDeleteJob(job)}
                    className="p-2 text-gray-400 hover:text-danger-600 rounded-lg hover:bg-danger-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Briefcase className="w-12 h-12" />}
            title="No job positions yet"
            description="Create your first job position to start recruiting"
            action={
              <Button onClick={() => setIsAddModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Position
              </Button>
            }
          />
        </Card>
      )}

      {/* Add/Edit Job Modal */}
      <JobModal
        isOpen={isAddModalOpen || !!editJob}
        onClose={() => {
          setIsAddModalOpen(false)
          setEditJob(null)
        }}
        onSubmit={(jobData) => {
          if (editJob) {
            updateMutation.mutate({ id: editJob.id, data: jobData })
          } else {
            createMutation.mutate(jobData)
          }
        }}
        isLoading={createMutation.isPending || updateMutation.isPending}
        job={editJob}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteJob}
        onClose={() => setDeleteJob(null)}
        onConfirm={() => deleteJob && deleteMutation.mutate(deleteJob.id)}
        title="Delete Position"
        message={`Are you sure you want to delete "${deleteJob?.title}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

interface JobModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: JobPositionCreate) => void
  isLoading: boolean
  job?: JobPosition | null
}

function JobModal({ isOpen, onClose, onSubmit, isLoading, job }: JobModalProps) {
  const [formData, setFormData] = useState<JobPositionCreate>({
    title: '',
    description: '',
    department: '',
    location: '',
    salary_range: '',
    status: 'open',
    requirements: {
      required_skills: [],
      preferred_skills: [],
      min_experience_years: 0,
      education_level: 'bachelor',
    },
  })

  // Update form when editing
  useState(() => {
    if (job) {
      setFormData({
        title: job.title,
        description: job.description,
        department: job.department,
        location: job.location,
        salary_range: job.salary_range,
        status: job.status,
        requirements: job.requirements || {},
      })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={job ? 'Edit Position' : 'Create Position'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Job Title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          required
        />

        <Textarea
          label="Description"
          rows={4}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Department"
            value={formData.department}
            onChange={(e) => setFormData({ ...formData, department: e.target.value })}
          />
          <Input
            label="Location"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Salary Range"
            placeholder="e.g., $80k - $100k"
            value={formData.salary_range}
            onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
          />
          <Select
            label="Status"
            options={[
              { value: 'open', label: 'Open' },
              { value: 'closed', label: 'Closed' },
              { value: 'on_hold', label: 'On Hold' },
            ]}
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
          />
        </div>

        <Input
          label="Required Skills (comma-separated)"
          placeholder="Python, JavaScript, React"
          onChange={(e) => {
            const skills = e.target.value.split(',').map(s => s.trim()).filter(Boolean)
            setFormData({
              ...formData,
              requirements: {
                ...formData.requirements,
                required_skills: skills,
              }
            })
          }}
        />

        <Input
          label="Preferred Skills (comma-separated)"
          placeholder="AWS, Docker, Machine Learning"
          onChange={(e) => {
            const skills = e.target.value.split(',').map(s => s.trim()).filter(Boolean)
            setFormData({
              ...formData,
              requirements: {
                ...formData.requirements,
                preferred_skills: skills,
              }
            })
          }}
        />

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {job ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
