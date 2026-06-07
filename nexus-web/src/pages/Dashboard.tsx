import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import SensorCard from '../components/SensorCard'

type Reading = {
  sensor: string
  value: number
}

const SENSOR_META: Record<string, { label: string; unit: string }> = {
  dht11_temp: { label: 'Temperatuur', unit: ' °C' },
  dht11_humidity: { label: 'Luchtvochtigheid', unit: '%' },
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

export default function Dashboard() {
  const [readings, setReadings] = useState<Record<string, Reading>>({})

  useEffect(() => {
    fetchLatest().then(setReadings)
    const interval = setInterval(() => fetchLatest().then(setReadings), 5000)
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
      </div>
    </div>
  )
}
