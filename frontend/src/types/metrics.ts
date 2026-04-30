export interface FitnessMetrics {
  date: string
  ctl: number
  atl: number
  tsb: number
  daily_tss: number
}

export interface Workout {
  id: string
  activityName: string
  activityType: {
    typeKey: string
  }
  startTimeLocal: string
  duration: number
  distance?: number
  averageSpeed?: number
  averagePower?: number
  maxPower?: number
  averageHR?: number
  maxHR?: number
  calories?: number
  tss?: number
  elevationGain?: number
}

export interface ACWRResult {
  acute_load: number
  chronic_load: number
  ratio: number
  risk_level: string
  recommendation: string
}

export interface SportMetrics {
  sport: string
  ctl: number
  atl: number
  tsb: number
}

export interface MultiSportPMC {
  global_metrics: FitnessMetrics
  sport_metrics: Record<string, SportMetrics>
}

export interface PowerCurvePoint {
  duration_sec: number
  power: number
}

export interface CriticalPowerModel {
  cp: number
  w_prime: number
  r_squared: number
}

export interface ZoneDistribution {
  zone: number
  name: string
  time_sec: number
  percentage: number
  tss: number
}

export interface WeeklySummary {
  week_start: string
  week_end: string
  total_duration_hours: number
  total_distance_km: number
  total_tss: number
  activity_count: number
  by_sport: Record<string, {
    duration: number
    distance: number
    tss: number
    count: number
  }>
}
