import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { teamApi } from '@/services/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card'
import { Button } from '@/components/common'
import { Input } from '@/components/common/Input'
import { Modal } from '@/components/common/Modal'
import { LoadingSpinner } from '@/components/common/Badge'
import { Plus, Mail, Trash2, Crown, User, Clock, CheckCircle } from 'lucide-react'
import { cn } from '@/utils'

interface TeamMember {
  id: string
  email: string
  name?: string
  role: string
  status: string
  invited_at?: string
  joined_at?: string
  last_active_at?: string
}

interface TeamListResponse {
  members: TeamMember[]
  total: number
  seats_used: number
  seats_total: number
}

export default function TeamPage() {
  const queryClient = useQueryClient()
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false)

  const { data: teamData, isLoading } = useQuery({
    queryKey: ['team-members'],
    queryFn: () => teamApi.list(),
  }) as { data: TeamListResponse | undefined; isLoading: boolean }

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; name?: string; role: string }) =>
      teamApi.invite(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['team-members'] })
      setIsInviteModalOpen(false)
      // Show invite URL in alert
      alert(`Invite link: ${data.invite_url}`)
    },
  })

  const removeMutation = useMutation({
    mutationFn: (memberId: string) => teamApi.remove(memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team-members'] })
    },
  })

  const updateRoleMutation = useMutation({
    mutationFn: ({ memberId, role }: { memberId: string; role: string }) =>
      teamApi.update(memberId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team-members'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const team = teamData || { members: [], seats_used: 0, seats_total: 1 }
  const availableSeats = team.seats_total - team.seats_used

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team</h1>
          <p className="text-gray-500 mt-1">
            Manage your recruitment team
          </p>
        </div>
        <Button onClick={() => setIsInviteModalOpen(true)} disabled={availableSeats <= 0}>
          <Plus className="w-4 h-4 mr-2" />
          Invite Member
        </Button>
      </div>

      {/* Seat Usage */}
      <Card>
        <CardContent className="flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-900">Team Seats</p>
            <p className="text-sm text-gray-500">
              {team.seats_used} of {team.seats_total} seats used
            </p>
          </div>
          <div className="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                team.seats_used >= team.seats_total ? 'bg-danger-500' : 'bg-success-500'
              )}
              style={{ width: `${(team.seats_used / team.seats_total) * 100}%` }}
            />
          </div>
          {availableSeats <= 0 && (
            <p className="text-sm text-danger-600">
              Upgrade to add more seats
            </p>
          )}
        </CardContent>
      </Card>

      {/* Team Members */}
      <Card>
        <CardHeader>
          <CardTitle>Team Members</CardTitle>
        </CardHeader>
        <CardContent>
          {team.members && team.members.length > 0 ? (
            <div className="divide-y divide-gray-100">
              {team.members.map((member) => (
                <div key={member.id} className="py-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                      {member.name ? (
                        <span className="text-primary-600 font-medium">
                          {member.name.charAt(0).toUpperCase()}
                        </span>
                      ) : (
                        <User className="w-5 h-5 text-primary-600" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900">
                          {member.name || 'Unnamed'}
                        </p>
                        {member.role === 'owner' && (
                          <Crown className="w-4 h-4 text-warning-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-500">{member.email}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* Status Badge */}
                    <StatusBadge status={member.status} />

                    {/* Role Selector */}
                    {member.role !== 'owner' && (
                      <select
                        value={member.role}
                        onChange={(e) =>
                          updateRoleMutation.mutate({
                            memberId: member.id,
                            role: e.target.value,
                          })
                        }
                        className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="admin">Admin</option>
                        <option value="member">Member</option>
                      </select>
                    )}

                    {/* Remove Button */}
                    {member.role !== 'owner' && (
                      <button
                        onClick={() => removeMutation.mutate(member.id)}
                        className="p-2 text-gray-400 hover:text-danger-600 rounded-lg hover:bg-danger-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No team members yet</p>
              <p className="text-sm text-gray-400 mt-1">
                Invite your first team member to collaborate
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Invite Modal */}
      <InviteModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        onInvite={(data) => inviteMutation.mutate(data)}
        isLoading={inviteMutation.isPending}
      />
    </div>
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

function StatusBadge({ status }: { status: string }) {
  const config = {
    active: { color: 'bg-success-100 text-success-700', icon: CheckCircle },
    pending: { color: 'bg-warning-100 text-warning-700', icon: Clock },
    removed: { color: 'bg-gray-100 text-gray-600', icon: User },
  }

  const { color, icon: Icon } = config[status as keyof typeof config] || config.pending

  return (
    <span className={cn('inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium', color)}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

interface InviteModalProps {
  isOpen: boolean
  onClose: () => void
  onInvite: (data: { email: string; name?: string; role: string }) => void
  isLoading: boolean
}

function InviteModal({ isOpen, onClose, onInvite, isLoading }: InviteModalProps) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('member')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onInvite({ email, name: name || undefined, role })
    setEmail('')
    setName('')
    setRole('member')
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Team Member" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Email Address"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="colleague@company.com"
          required
        />

        <Input
          label="Name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="John Doe"
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
          <div className="space-y-2">
            <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="role"
                value="member"
                checked={role === 'member'}
                onChange={(e) => setRole(e.target.value)}
                className="text-primary-600 focus:ring-primary-500"
              />
              <div>
                <p className="font-medium text-gray-900">Member</p>
                <p className="text-sm text-gray-500">Can view and manage candidates and jobs</p>
              </div>
            </label>
            <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="role"
                value="admin"
                checked={role === 'admin'}
                onChange={(e) => setRole(e.target.value)}
                className="text-primary-600 focus:ring-primary-500"
              />
              <div>
                <p className="font-medium text-gray-900">Admin</p>
                <p className="text-sm text-gray-500">Can manage team settings and billing</p>
              </div>
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            <Mail className="w-4 h-4 mr-2" />
            Send Invitation
          </Button>
        </div>
      </form>
    </Modal>
  )
}
