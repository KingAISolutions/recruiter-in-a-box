import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { templatesApi } from '@/services/api'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Input, Textarea } from '@/components/common/Input'
import { EmptyState, LoadingSpinner } from '@/components/common/Badge'
import { Modal } from '@/components/common/Modal'
import { ConfirmDialog } from '@/components/common/Modal'
import { Plus, Search, Mail, Trash2, Edit, Eye } from 'lucide-react'
import { formatDate, truncate } from '@/utils'
import type { EmailTemplate, EmailTemplateCreate } from '@/types'

export default function TemplatesPage() {
  const queryClient = useQueryClient()
  const [page] = useState(1)
  const [search, setSearch] = useState('')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editTemplate, setEditTemplate] = useState<EmailTemplate | null>(null)
  const [viewTemplate, setViewTemplate] = useState<EmailTemplate | null>(null)
  const [deleteTemplate, setDeleteTemplate] = useState<EmailTemplate | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['templates', page, search],
    queryFn: () => templatesApi.list({ page, page_size: 20, search: search || undefined }),
  })

  const createMutation = useMutation({
    mutationFn: (data: EmailTemplateCreate) => templatesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setIsAddModalOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<EmailTemplateCreate> }) =>
      templatesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setEditTemplate(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => templatesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      setDeleteTemplate(null)
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
          <h1 className="text-2xl font-bold text-gray-900">Email Templates</h1>
          <p className="text-gray-500 mt-1">{data?.total || 0} templates</p>
        </div>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Search */}
      <Card padding="sm">
        <div className="max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {/* Templates Grid */}
      {data?.items && data.items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.items.map((template) => (
            <Card key={template.id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-secondary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    <p className="text-sm text-gray-500">{template.subject}</p>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                {truncate(template.body, 150)}
              </p>

              {template.variables && template.variables.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {template.variables.map((variable) => (
                    <span
                      key={variable}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-50 text-primary-700"
                    >
                      {`{${variable}}`}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <p className="text-xs text-gray-500">
                  Created {formatDate(template.created_at)}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewTemplate(template)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setEditTemplate(template)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setDeleteTemplate(template)}
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
            icon={<Mail className="w-12 h-12" />}
            title="No templates yet"
            description="Create your first email template for candidate outreach"
            action={
              <Button onClick={() => setIsAddModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Template
              </Button>
            }
          />
        </Card>
      )}

      {/* Add/Edit Template Modal */}
      <TemplateModal
        isOpen={isAddModalOpen || !!editTemplate}
        onClose={() => {
          setIsAddModalOpen(false)
          setEditTemplate(null)
        }}
        onSubmit={(templateData) => {
          if (editTemplate) {
            updateMutation.mutate({ id: editTemplate.id, data: templateData })
          } else {
            createMutation.mutate(templateData)
          }
        }}
        isLoading={createMutation.isPending || updateMutation.isPending}
        template={editTemplate}
      />

      {/* View Template Modal */}
      <Modal
        isOpen={!!viewTemplate}
        onClose={() => setViewTemplate(null)}
        title={viewTemplate?.name}
        size="lg"
      >
        {viewTemplate && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <p className="text-gray-900">{viewTemplate.subject}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Body</label>
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap text-gray-700">
                {viewTemplate.body}
              </div>
            </div>
            {viewTemplate.variables && viewTemplate.variables.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Variables</label>
                <div className="flex flex-wrap gap-2">
                  {viewTemplate.variables.map((variable) => (
                    <span
                      key={variable}
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-100 text-primary-700"
                    >
                      {`{${variable}}`}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteTemplate}
        onClose={() => setDeleteTemplate(null)}
        onConfirm={() => deleteTemplate && deleteMutation.mutate(deleteTemplate.id)}
        title="Delete Template"
        message={`Are you sure you want to delete "${deleteTemplate?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

interface TemplateModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: EmailTemplateCreate) => void
  isLoading: boolean
  template?: EmailTemplate | null
}

function TemplateModal({ isOpen, onClose, onSubmit, isLoading, template }: TemplateModalProps) {
  const [formData, setFormData] = useState<EmailTemplateCreate>({
    name: '',
    subject: '',
    body: '',
  })

  // Update form when editing
  useState(() => {
    if (template) {
      setFormData({
        name: template.name,
        subject: template.subject,
        body: template.body,
      })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const availableVariables = [
    { name: 'candidate_name', description: 'Full name of the candidate' },
    { name: 'first_name', description: 'First name of the candidate' },
    { name: 'email', description: 'Email address' },
    { name: 'position', description: 'Job position title' },
    { name: 'company_name', description: 'Your company name' },
    { name: 'job_title', description: 'Same as position' },
    { name: 'department', description: 'Department name' },
    { name: 'location', description: 'Job location' },
  ]

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={template ? 'Edit Template' : 'Create Template'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Template Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g., Initial Outreach"
          required
        />

        <Input
          label="Email Subject"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          placeholder="e.g., Exciting Opportunity at {company_name}"
          required
        />

        <Textarea
          label="Email Body"
          rows={10}
          value={formData.body}
          onChange={(e) => setFormData({ ...formData, body: e.target.value })}
          placeholder="Dear {candidate_name},

We came across your profile and were impressed by your experience...

Best regards,
{company_name}"
          required
        />

        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Available Variables</label>
          <div className="grid grid-cols-2 gap-2">
            {availableVariables.map((variable) => (
              <button
                key={variable.name}
                type="button"
                onClick={() => {
                  setFormData((prev) => ({
                    ...prev,
                    body: prev.body + `{${variable.name}}`,
                  }))
                }}
                className="text-left p-2 rounded hover:bg-gray-100 transition-colors"
              >
                <code className="text-sm text-primary-600">{`{${variable.name}}`}</code>
                <p className="text-xs text-gray-500">{variable.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {template ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
