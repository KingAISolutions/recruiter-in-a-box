import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { candidatesApi } from '@/services/api'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Input, Select } from '@/components/common/Input'
import { StatusBadge, Avatar, EmptyState, LoadingSpinner } from '@/components/common/Badge'
import { Modal } from '@/components/common/Modal'
import { ConfirmDialog } from '@/components/common/Modal'
import { Plus, Search, Upload, Trash2, Edit, Eye } from 'lucide-react'
import { formatRelativeTime } from '@/utils'
import type { Candidate, CandidateCreate } from '@/types'

const STATUS_OPTIONS = [
  { value: '', label: 'All Status' },
  { value: 'new', label: 'New' },
  { value: 'screening', label: 'Screening' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'hired', label: 'Hired' },
  { value: 'rejected', label: 'Rejected' },
]

export default function CandidatesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [deleteCandidate, setDeleteCandidate] = useState<Candidate | null>(null)
  const [uploadedData, setUploadedData] = useState<any>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['candidates', page, search, status],
    queryFn: () => candidatesApi.list({ page, page_size: 20, search: search || undefined, status: status || undefined }),
  })

  const createMutation = useMutation({
    mutationFn: (data: CandidateCreate) => candidatesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      setIsAddModalOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => candidatesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      setDeleteCandidate(null)
    },
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => candidatesApi.uploadResume(file),
    onSuccess: (data) => {
      setUploadedData(data.extracted_data)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type === 'application/pdf') {
      uploadMutation.mutate(file)
    }
  }

  const handleCreateCandidate = (data: CandidateCreate) => {
    createMutation.mutate(data)
  }

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
          <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
          <p className="text-gray-500 mt-1">{data?.total || 0} total candidates</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => setIsUploadModalOpen(true)}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Resume
          </Button>
          <Button onClick={() => setIsAddModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Candidate
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card padding="sm">
        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search candidates..."
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

      {/* Candidates List */}
      {data?.items && data.items.length > 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Candidate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Skills
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Experience
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Added
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.items.map((candidate) => (
                <tr key={candidate.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Avatar name={candidate.full_name} size="md" />
                      <div>
                        <p className="font-medium text-gray-900">{candidate.full_name}</p>
                        <p className="text-sm text-gray-500">{candidate.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={candidate.status} />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {(candidate.skills || []).slice(0, 3).map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {skill}
                        </span>
                      ))}
                      {(candidate.skills || []).length > 3 && (
                        <span className="text-xs text-gray-500">+{candidate.skills.length - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {candidate.experience_years} years
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatRelativeTime(candidate.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => navigate(`/candidates/${candidate.id}`)}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => navigate(`/candidates/${candidate.id}/edit`)}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteCandidate(candidate)}
                        className="p-2 text-gray-400 hover:text-danger-600 rounded-lg hover:bg-danger-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<Users className="w-12 h-12" />}
            title="No candidates yet"
            description="Start by adding your first candidate or uploading resumes"
            action={
              <div className="flex gap-3 justify-center">
                <Button variant="secondary" onClick={() => setIsUploadModalOpen(true)}>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Resume
                </Button>
                <Button onClick={() => setIsAddModalOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Candidate
                </Button>
              </div>
            }
          />
        </Card>
      )}

      {/* Pagination */}
      {data && data.total > 20 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, data.total)} of {data.total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page * 20 >= data.total}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Add Candidate Modal */}
      <AddCandidateModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleCreateCandidate}
        isLoading={createMutation.isPending}
        prefillData={uploadedData}
      />

      {/* Upload Resume Modal */}
      <UploadResumeModal
        isOpen={isUploadModalOpen}
        onClose={() => {
          setIsUploadModalOpen(false)
          setUploadedData(null)
        }}
        onFileChange={handleFileChange}
        isLoading={uploadMutation.isPending}
        uploadedData={uploadedData}
        onUseData={(data) => {
          setUploadedData(data)
          setIsUploadModalOpen(false)
          setIsAddModalOpen(true)
        }}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteCandidate}
        onClose={() => setDeleteCandidate(null)}
        onConfirm={() => deleteCandidate && deleteMutation.mutate(deleteCandidate.id)}
        title="Delete Candidate"
        message={`Are you sure you want to delete ${deleteCandidate?.full_name}? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

interface AddCandidateModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CandidateCreate) => void
  isLoading: boolean
  prefillData?: any
}

function AddCandidateModal({ isOpen, onClose, onSubmit, isLoading, prefillData }: AddCandidateModalProps) {
  const [formData, setFormData] = useState<CandidateCreate>({
    full_name: '',
    email: '',
    phone: '',
    skills: [],
    experience_years: 0,
    education_level: '',
    current_position: '',
    current_company: '',
    status: 'new',
  })

  // Update form when prefillData changes
  useState(() => {
    if (prefillData) {
      setFormData((prev) => ({
        ...prev,
        full_name: prefillData.full_name || prev.full_name,
        email: prefillData.email || prev.email,
        phone: prefillData.phone || prev.phone,
        skills: prefillData.skills || prev.skills,
        experience_years: prefillData.experience_years || prev.experience_years,
        education_level: prefillData.education_level || prev.education_level,
        current_position: prefillData.current_position || prev.current_position,
        current_company: prefillData.current_company || prev.current_company,
      }))
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Candidate" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
          />
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Phone"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
          <Input
            label="Current Position"
            value={formData.current_position}
            onChange={(e) => setFormData({ ...formData, current_position: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Current Company"
            value={formData.current_company}
            onChange={(e) => setFormData({ ...formData, current_company: e.target.value })}
          />
          <Input
            label="Experience (years)"
            type="number"
            min="0"
            value={formData.experience_years}
            onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
          />
        </div>

        <Select
          label="Education Level"
          options={[
            { value: '', label: 'Select...' },
            { value: 'high_school', label: 'High School' },
            { value: 'associate', label: 'Associate' },
            { value: 'bachelor', label: "Bachelor's" },
            { value: 'master', label: "Master's" },
            { value: 'phd', label: 'PhD' },
          ]}
          value={formData.education_level}
          onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
        />

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Add Candidate
          </Button>
        </div>
      </form>
    </Modal>
  )
}

interface UploadResumeModalProps {
  isOpen: boolean
  onClose: () => void
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  isLoading: boolean
  uploadedData: any
  onUseData: (data: any) => void
}

function UploadResumeModal({
  isOpen,
  onClose,
  onFileChange,
  isLoading,
  uploadedData,
  onUseData,
}: UploadResumeModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Upload Resume" size="md">
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            type="file"
            accept=".pdf"
            onChange={onFileChange}
            className="hidden"
            id="resume-upload"
          />
          <label htmlFor="resume-upload" className="cursor-pointer">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              <span className="text-primary-600 font-medium">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-gray-500 mt-1">PDF files only, max 10MB</p>
          </label>
        </div>

        {isLoading && (
          <div className="text-center py-4">
            <LoadingSpinner />
            <p className="text-sm text-gray-500 mt-2">Parsing resume...</p>
          </div>
        )}

        {uploadedData && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Extracted Information</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              {uploadedData.full_name && (
                <p className="text-sm">
                  <span className="font-medium">Name:</span> {uploadedData.full_name}
                </p>
              )}
              {uploadedData.email && (
                <p className="text-sm">
                  <span className="font-medium">Email:</span> {uploadedData.email}
                </p>
              )}
              {uploadedData.phone && (
                <p className="text-sm">
                  <span className="font-medium">Phone:</span> {uploadedData.phone}
                </p>
              )}
              {uploadedData.skills && uploadedData.skills.length > 0 && (
                <p className="text-sm">
                  <span className="font-medium">Skills:</span> {uploadedData.skills.join(', ')}
                </p>
              )}
              {uploadedData.experience_years > 0 && (
                <p className="text-sm">
                  <span className="font-medium">Experience:</span> {uploadedData.experience_years} years
                </p>
              )}
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={() => onUseData(uploadedData)}>
                Use This Data
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}

function Users(props: React.SVGProps<SVGSVGElement> & { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  )
}
