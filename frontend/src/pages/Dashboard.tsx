import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/services/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card'
import { LoadingSpinner } from '@/components/common/Badge'
import { Users, Briefcase, Mail, TrendingUp, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { cn } from '@/utils'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444']

export default function DashboardPage() {
  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => dashboardApi.getOverview(),
  })

  const { data: pipeline, isLoading: loadingPipeline } = useQuery({
    queryKey: ['dashboard-pipeline'],
    queryFn: () => dashboardApi.getPipeline(),
  })

  const { data: metrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => dashboardApi.getMetrics(30),
  })

  const { data: activity, isLoading: loadingActivity } = useQuery({
    queryKey: ['dashboard-activity'],
    queryFn: () => dashboardApi.getActivity({ page_size: 10 }),
  })

  if (loadingOverview || loadingPipeline || loadingMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your recruitment activities</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Candidates"
          value={overview?.total_candidates || 0}
          icon={Users}
          trend={12}
          trendLabel="vs last month"
          color="primary"
        />
        <StatCard
          title="Active Jobs"
          value={overview?.open_jobs || 0}
          subtitle={`of ${overview?.total_jobs || 0} total`}
          icon={Briefcase}
          trend={-5}
          trendLabel="vs last month"
          color="secondary"
        />
        <StatCard
          title="Emails Sent"
          value={overview?.total_emails_sent || 0}
          icon={Mail}
          trend={23}
          trendLabel="vs last month"
          color="success"
        />
        <StatCard
          title="Open Rate"
          value={`${overview?.email_open_rate || 0}%`}
          icon={TrendingUp}
          trend={8}
          trendLabel="vs last month"
          color="warning"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Candidate Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pipeline?.stages || []}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                    nameKey="label"
                  >
                    {(pipeline?.stages || []).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {(pipeline?.stages || []).map((stage, index) => (
                <div key={stage.status} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm text-gray-600">{stage.label}</span>
                  <span className="text-sm font-medium text-gray-900 ml-auto">{stage.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Hiring Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Hiring Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <MetricRow
                label="Avg. Time to Hire"
                value={`${metrics?.avg_time_to_hire || 0} days`}
              />
              <MetricRow
                label="Total Hired"
                value={metrics?.total_hired || 0}
                color="success"
              />
              <MetricRow
                label="Total Rejected"
                value={metrics?.total_rejected || 0}
                color="danger"
              />
              <MetricRow
                label="Offer Acceptance Rate"
                value={`${metrics?.offer_acceptance_rate || 0}%`}
              />
              <MetricRow
                label="Candidates per Position"
                value={metrics?.candidates_per_position?.toFixed(1) || '0'}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingActivity ? (
            <LoadingSpinner />
          ) : (
            <div className="space-y-3">
              {(activity?.items || []).map((item) => (
                <div key={item.id} className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0">
                  <div className="w-2 h-2 rounded-full bg-primary-500" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium capitalize">{item.action.replace(/_/g, ' ')}</span>
                      {item.entity_type && (
                        <>
                          {' '}
                          <span className="text-gray-500">{item.entity_type}</span>
                        </>
                      )}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
              {(!activity?.items || activity.items.length === 0) && (
                <p className="text-sm text-gray-500 text-center py-4">No recent activity</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ElementType
  trend?: number
  trendLabel?: string
  color?: 'primary' | 'secondary' | 'success' | 'warning'
}

function StatCard({ title, value, subtitle, icon: Icon, trend, trendLabel, color = 'primary' }: StatCardProps) {
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
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          {trend !== undefined && (
            <div className={cn('flex items-center gap-1 mt-2', trend >= 0 ? 'text-success-600' : 'text-danger-600')}>
              {trend >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span className="text-xs font-medium">{Math.abs(trend)}%</span>
              <span className="text-xs text-gray-500">{trendLabel}</span>
            </div>
          )}
        </div>
        <div className={cn('p-3 rounded-xl', colors[color])}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </Card>
  )
}

interface MetricRowProps {
  label: string
  value: string | number
  color?: 'success' | 'danger' | 'warning'
}

function MetricRow({ label, value, color }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={cn('text-sm font-semibold', color && `text-${color}-600`)}>{value}</span>
    </div>
  )
}
