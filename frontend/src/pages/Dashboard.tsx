import { useQuery } from '@tanstack/react-query'
import { Activity, Timer, Flame, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { metricsService } from '@/services/metricsService'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { formatTSS } from '@/lib/utils'

export function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: metricsService.getLatest,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="h-20 bg-muted" />
              <CardContent className="h-16 bg-muted" />
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const latest = metrics?.[metrics.length - 1]
  const previous = metrics?.[metrics.length - 2]

  const getTrend = (current: number, prev: number) => {
    if (!prev) return { icon: Minus, color: 'text-muted-foreground' }
    if (current > prev) return { icon: TrendingUp, color: 'text-success' }
    if (current < prev) return { icon: TrendingDown, color: 'text-danger' }
    return { icon: Minus, color: 'text-muted-foreground' }
  }

  const stats = latest ? [
    {
      title: 'Fitness (CTL)',
      value: latest.ctl.toFixed(1),
      description: 'Chronic Training Load',
      icon: Activity,
      trend: getTrend(latest.ctl, previous?.ctl || 0),
    },
    {
      title: 'Fatigue (ATL)',
      value: latest.atl.toFixed(1),
      description: 'Acute Training Load',
      icon: Flame,
      trend: getTrend(latest.atl, previous?.atl || 0),
    },
    {
      title: 'Form (TSB)',
      value: latest.tsb.toFixed(1),
      description: 'Training Stress Balance',
      icon: TrendingUp,
      trend: getTrend(latest.tsb, previous?.tsb || 0),
      color: latest.tsb > 0 ? 'text-success' : latest.tsb < -10 ? 'text-danger' : 'text-warning',
    },
    {
      title: 'Daily TSS',
      value: formatTSS(latest.daily_tss),
      description: 'Training Stress Score',
      icon: Timer,
      trend: getTrend(latest.daily_tss, previous?.daily_tss || 0),
    },
  ] : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your training metrics and performance.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">{stat.value}</div>
                <stat.trend.icon className={`h-4 w-4 ${stat.trend.color}`} />
              </div>
              <p className="text-xs text-muted-foreground">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* PMC Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Management Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center bg-muted rounded-lg">
            <p className="text-muted-foreground">PMC Chart - Coming Soon</p>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">
            Workout history will be displayed here.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
