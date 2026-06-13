import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import SensorCard from '../components/SensorCard'

type Reading = { sensor: string; value: number }
type Status = { beweging: string | null; geluid: string | null }

const SENSOR_META: Record<string, { label: string; unit: string }> = {
  dht11_temp: { label: 'Temperatuur', unit: ' °C' },
  dht11_humidity: { label: 'Luchtvochtigheid', unit: '%' },
  ldr_light: { label: 'Licht', unit: '%' },
  bmp180_pressure: { label: 'Luchtdruk', unit: ' hPa' },
}

async function fetchLatest(): Promise<Record<string, Reading>> {
  const { data, error } = await supabase
    .from('sensor_readings')
    .select('sensor, value')
    .order('id', { ascending: false })
    .limit(20)

  if (error) console.error('sensor_readings:', error)
  if (!data) return {}

  const latest: Record<string, Reading> = {}
  for (const row of data) {
    if (!latest[row.sensor]) latest[row.sensor] = row
  }
  return latest
}

async function fetchStatus(): Promise<Status> {
  const [{ data: m }, { data: s }] = await Promise.all([
    supabase.from('events').select('type')
      .in('type', ['motion_detected', 'motion_absent'])
      .order('id', { ascending: false }).limit(1),
    supabase.from('events').select('type')
      .in('type', ['sound_detected', 'sound_absent'])
      .order('id', { ascending: false }).limit(1),
  ])
  return { beweging: m?.[0]?.type ?? null, geluid: s?.[0]?.type ?? null }
}

function StatusCard({ label, actief }: { label: string; actief: boolean | null }) {
  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-2">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`text-4xl font-bold ${actief === null ? 'text-gray-600' : actief ? 'text-orange-400' : 'text-gray-500'}`}>
        {actief === null ? '—' : actief ? 'JA' : 'nee'}
      </span>
    </div>
  )
}

export default function Dashboard() {
  const [readings, setReadings] = useState<Record<string, Reading>>({})
  const [status, setStatus] = useState<Status>({ beweging: null, geluid: null })

  useEffect(() => {
    fetchLatest().then(setReadings)
    fetchStatus().then(setStatus)
    const interval = setInterval(() => {
      fetchLatest().then(setReadings)
      fetchStatus().then(setStatus)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-xl font-semibold mb-6">Nexus</h1>
      <div className="grid grid-cols-2 gap-4 max-w-sm">
        {Object.entries(SENSOR_META).map(([key, meta]) => {
          const r = readings[key]
          return (
            <SensorCard
              key={key}
              label={meta.label}
              value={r?.value ?? null}
              unit={meta.unit}
              updatedAt={null}
            />
          )
        })}
        <StatusCard label="Beweging" actief={status.beweging === null ? null : status.beweging === 'motion_detected'} />
        <StatusCard label="Geluid" actief={status.geluid === null ? null : status.geluid === 'sound_detected'} />
      </div>
    </div>
  )
}
