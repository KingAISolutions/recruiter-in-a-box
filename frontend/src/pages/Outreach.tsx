import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { outreachApi, candidatesApi, templatesApi, jobsApi } from '@/services/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Select } from '@/components/common/Input'
import { StatusBadge, LoadingSpinner } from '@/components/common/Badge'
import { Modal } from '@/components/common/Modal'
import { Send, Mail, TrendingUp, CheckCircle, Eye } from 'lucide-react'
import { formatDateTime, cn } from '@/utils'

export default function OutreachPage() {
  const queryClient = useQueryClient()
  const [page] = useState(1)
  const [isSendModalOpen, setIsSendModalOpen] = useState(false)

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['outreach-stats'],
    queryFn: () => outreachApi.getStats(),
  })

  const { data: emails, isLoading: loadingEmails } = useQuery({
    queryKey: ['sent-emails', page],
    queryFn: () => outreachApi.listEmails({ page, page_size: 20 }),
  })

  const sendMutation = useMutation({
    mutationFn: outreachApi.bulkSend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sent-emails'] })
      queryClient.invalidateQueries({ queryKey: ['outreach-stats'] })
      setIsSendModalOpen(false)
    },
  })

  if (loadingStats || loadingEmails) {
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
          <h1 className="text-2xl font-bold text-gray-900">Outreach</h1>
          <p className="text-gray-500 mt-1">Manage your candidate communications</p>
        </div>
        <Button onClick={() => setIsSendModalOpen(true)}>
          <Send className="w-4 h-4 mr-2" />
          Send Bulk Email
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Sent"
          value={stats?.total_sent || 0}
          icon={Send}
          color="primary"
        />
        <StatCard
          title="Delivered"
          value={stats?.total_delivered || 0}
          subtitle={`${stats?.delivery_rate || 0}% delivery rate`}
          icon={CheckCircle}
          color="success"
        />
        <StatCard
          title="Opened"
          value={stats?.total_opened || 0}
          subtitle={`${stats?.open_rate || 0}% open rate`}
          icon={Eye}
          color="secondary"
        />
        <StatCard
          title="Replied"
          value={stats?.total_replied || 0}
          subtitle={`${stats?.reply_rate || 0}% reply rate`}
          icon={TrendingUp}
          color="warning"
        />
      </div>

      {/* Email Performance Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Email Funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-8 bg-gray-100 rounded-lg overflow-hidden flex">
              {stats && stats.total_sent > 0 && (
                <>
                  <div
                    className="bg-success-500 h-full flex items-center justify-center text-white text-xs font-medium"
                    style={{ width: `${(stats.total_delivered / stats.total_sent) * 100}%` }}
                    title={`Delivered: ${stats.total_delivered}`}
                  >
                    {stats.total_delivered > 0 && stats.total_delivered > stats.total_sent * 0.1 && 'Delivered'}
                  </div>
                  <div
                    className="bg-secondary-500 h-full flex items-center justify-center text-white text-xs font-medium"
                    style={{ width: `${((stats.total_opened - stats.total_replied) / stats.total_sent) * 100}%` }}
                    title={`Opened: ${stats.total_opened}`}
                  >
                    {(stats.total_opened - stats.total_replied) > 0 && (stats.total_opened - stats.total_replied) > stats.total_sent * 0.1 && 'Opened'}
                  </div>
                  <div
                    className="bg-warning-500 h-full flex items-center justify-center text-white text-xs font-medium"
                    style={{ width: `${(stats.total_replied / stats.total_sent) * 100}%` }}
                    title={`Replied: ${stats.total_replied}`}
                  >
                    {stats.total_replied > 0 && stats.total_replied > stats.total_sent * 0.1 && 'Replied'}
                  </div>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between mt-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-success-500 rounded" />
              <span className="text-gray-600">Delivered ({stats?.total_delivered || 0})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-secondary-500 rounded" />
              <span className="text-gray-600">Opened ({stats?.total_opened || 0})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-warning-500 rounded" />
              <span className="text-gray-600">Replied ({stats?.total_replied || 0})</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sent Emails */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Sent Emails</CardTitle>
        </CardHeader>
        <CardContent>
          {emails?.items && emails.items.length > 0 ? (
            <div className="divide-y divide-gray-100">
              {emails.items.map((email) => (
                <div key={email.id} className="py-4 first:pt-0 last:pb-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{email.subject}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        Sent to candidate • {formatDateTime(email.sent_at || email.created_at)}
                      </p>
                    </div>
                    <StatusBadge status={email.status} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Mail className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No emails sent yet</p>
              <p className="text-sm text-gray-400 mt-1">Start by sending your first outreach email</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Send Bulk Email Modal */}
      <BulkEmailModal
        isOpen={isSendModalOpen}
        onClose={() => setIsSendModalOpen(false)}
        onSend={(data) => sendMutation.mutate(data)}
        isLoading={sendMutation.isPending}
      />
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  subtitle?: string
  icon: React.ElementType
  color?: 'primary' | 'secondary' | 'success' | 'warning'
}

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary' }: StatCardProps) {
  const colors = {
    primary: 'bg-primary-100 text-primary-600',
    secondary: 'bg-secondary-100 text-secondary-600',
    success: 'bg-success-100 text-success-600',
    warning: 'bg-warning-100 text-warning-600',
  }

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value.toLocaleString()}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={cn('p-3 rounded-xl', colors[color])}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </Card>
  )
}

interface BulkEmailModalProps {
  isOpen: boolean
  onClose: () => void
  onSend: (data: { candidate_ids: string[]; template_id?: string; job_position_id?: string }) => void
  isLoading: boolean
}

function BulkEmailModal({ isOpen, onClose, onSend, isLoading }: BulkEmailModalProps) {
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([])
  const [templateId, setTemplateId] = useState('')
  const [jobId, setJobId] = useState('')

  const { data: candidates } = useQuery({
    queryKey: ['candidates-list'],
    queryFn: () => candidatesApi.list({ page: 1, page_size: 100 }),
  })

  const { data: templates } = useQuery({
    queryKey: ['templates-list'],
    queryFn: () => templatesApi.list({ page: 1, page_size: 100 }),
  })

  const { data: jobs } = useQuery({
    queryKey: ['jobs-list'],
    queryFn: () => jobsApi.list({ page: 1, page_size: 100 }),
  })

  const handleSend = () => {
    onSend({
      candidate_ids: selectedCandidates,
      template_id: templateId || undefined,
      job_position_id: jobId || undefined,
    })
  }

  const toggleCandidate = (id: string) => {
    setSelectedCandidates((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    )
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Send Bulk Email" size="lg">
      <div className="space-y-4">
        {/* Template Selection */}
        <Select
          label="Email Template"
          options={[
            { value: '', label: 'Select a template...' },
            ...(templates?.items || []).map((t) => ({ value: t.id, label: t.name })),
          ]}
          value={templateId}
          onChange={(e) => setTemplateId(e.target.value)}
        />

        {/* Job Position */}
        <Select
          label="Related Job Position (optional)"
          options={[
            { value: '', label: 'Select a position...' },
            ...(jobs?.items || []).map((j) => ({ value: j.id, label: j.title })),
          ]}
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
        />

        {/* Candidate Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Candidates ({selectedCandidates.length} selected)
          </label>
          <div className="border border-gray-200 rounded-lg max-h-64 overflow-y-auto">
            {(candidates?.items || []).map((candidate) => (
              <label
                key={candidate.id}
                className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0"
              >
                <input
                  type="checkbox"
                  checked={selectedCandidates.includes(candidate.id)}
                  onChange={() => toggleCandidate(candidate.id)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{candidate.full_name}</p>
                  <p className="text-sm text-gray-500">{candidate.email}</p>
                </div>
                <StatusBadge status={candidate.status} />
              </label>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            isLoading={isLoading}
            disabled={selectedCandidates.length === 0}
          >
            <Send className="w-4 h-4 mr-2" />
            Send to {selectedCandidates.length} Candidate{selectedCandidates.length !== 1 ? 's' : ''}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
