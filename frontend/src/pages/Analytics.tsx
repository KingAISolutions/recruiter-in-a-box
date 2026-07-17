import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/services/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card'
import { StatusBadge, LoadingSpinner } from '@/components/common/Badge'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { Users, TrendingUp, Clock, Target } from 'lucide-react'

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444']

export default function AnalyticsPage() {
  const { data: metrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => dashboardApi.getMetrics(30),
  })

  const { data: pipeline, isLoading: loadingPipeline } = useQuery({
    queryKey: ['dashboard-pipeline'],
    queryFn: () => dashboardApi.getPipeline(),
  })

  const { data: candidatesOverTime, isLoading: loadingOverTime } = useQuery({
    queryKey: ['candidates-over-time'],
    queryFn: () => dashboardApi.getCandidatesOverTime(30),
  })

  const { data: emailPerformance, isLoading: loadingEmailPerf } = useQuery({
    queryKey: ['email-performance'],
    queryFn: () => dashboardApi.getEmailPerformance(30),
  })

  if (loadingMetrics || loadingPipeline || loadingOverTime || loadingEmailPerf) {
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
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-500 mt-1">Recruitment performance insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Candidates"
          value={pipeline?.total || 0}
          icon={Users}
          trend={12}
          color="primary"
        />
        <MetricCard
          title="Avg. Time to Hire"
          value={`${metrics?.avg_time_to_hire || 0} days`}
          icon={Clock}
          trend={-8}
          color="secondary"
        />
        <MetricCard
          title="Offer Acceptance"
          value={`${metrics?.offer_acceptance_rate || 0}%`}
          icon={Target}
          trend={5}
          color="success"
        />
        <MetricCard
          title="Candidates per Position"
          value={metrics?.candidates_per_position?.toFixed(1) || '0'}
          icon={TrendingUp}
          trend={15}
          color="warning"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Candidates Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Candidates Added (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={candidatesOverTime?.data || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Candidate Pipeline Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pipeline?.stages || []}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                    nameKey="label"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {(pipeline?.stages || []).map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Email Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Email Performance (Last 30 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={emailPerformance?.data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Bar dataKey="sent" fill="#3b82f6" name="Sent" />
                <Bar dataKey="delivered" fill="#10b981" name="Delivered" />
                <Bar dataKey="opened" fill="#8b5cf6" name="Opened" />
                <Bar dataKey="replied" fill="#f59e0b" name="Replied" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-primary-500 rounded" />
              <span className="text-sm text-gray-600">Sent</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-success-500 rounded" />
              <span className="text-sm text-gray-600">Delivered</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-secondary-500 rounded" />
              <span className="text-sm text-gray-600">Opened</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-warning-500 rounded" />
              <span className="text-sm text-gray-600">Replied</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hiring Funnel */}
      <Card>
        <CardHeader>
          <CardTitle>Hiring Funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(pipeline?.stages || []).map((stage, index) => {
              const percentage = pipeline?.total ? (stage.count / pipeline.total) * 100 : 0
              return (
                <div key={stage.status}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-700">{stage.label}</span>
                      <StatusBadge status={stage.status} />
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {stage.count} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-4">
                    <div
                      className="h-4 rounded-full transition-all duration-500"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: COLORS[index % COLORS.length],
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  trend?: number
  color?: 'primary' | 'secondary' | 'success' | 'warning'
}

function MetricCard({ title, value, icon: Icon, trend, color = 'primary' }: MetricCardProps) {
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
          {trend !== undefined && (
            <p className={`text-xs mt-1 ${trend >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
              {trend >= 0 ? '+' : ''}{trend}% vs last period
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </Card>
  )
}
