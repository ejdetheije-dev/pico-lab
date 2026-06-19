import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import SensorCard from '../components/SensorCard'

type Reading = { sensor: string; value: number }
type Status = { beweging: string | null; geluid: string | null }
type Weather = { temperature: number | null; humidity: number | null; pressure: number | null }

const LAT = 52.13
const LON = 4.45

const SENSOR_META: Record<string, { label: string; unit: string }> = {
  dht11_temp: { label: 'Temperatuur', unit: ' °C' },
  dht11_humidity: { label: 'Luchtvochtigheid', unit: '%' },
  ldr_light: { label: 'Licht', unit: '%' },
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

async function fetchWeather(): Promise<Weather> {
  const res = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}` +
    `&current=temperature_2m,relative_humidity_2m,surface_pressure&timezone=Europe/Amsterdam`
  )
  const json = await res.json()
  const c = json.current
  return {
    temperature: c?.temperature_2m ?? null,
    humidity: c?.relative_humidity_2m ?? null,
    pressure: c?.surface_pressure ?? null,
  }
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

function WeatherCard({ label, outdoor, nexus, unit }: {
  label: string
  outdoor: number | null
  nexus: number | null
  unit: string
}) {
  const diff = nexus !== null && outdoor !== null ? nexus - outdoor : null
  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-1">
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-3xl font-bold">
        {outdoor !== null ? `${outdoor.toFixed(1)}${unit}` : '—'}
      </span>
      {diff !== null && (
        <span className={`text-xs font-medium ${diff > 0.5 ? 'text-orange-400' : diff < -0.5 ? 'text-blue-400' : 'text-gray-500'}`}>
          Nexus {diff >= 0 ? '+' : ''}{diff.toFixed(1)} {unit}
        </span>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [readings, setReadings] = useState<Record<string, Reading>>({})
  const [status, setStatus] = useState<Status>({ beweging: null, geluid: null })
  const [weather, setWeather] = useState<Weather>({ temperature: null, humidity: null, pressure: null })

  useEffect(() => {
    fetchLatest().then(setReadings)
    fetchStatus().then(setStatus)
    fetchWeather().then(setWeather)

    const sensorInterval = setInterval(() => {
      fetchLatest().then(setReadings)
      fetchStatus().then(setStatus)
    }, 5000)

    const weatherInterval = setInterval(() => fetchWeather().then(setWeather), 60_000)

    return () => {
      clearInterval(sensorInterval)
      clearInterval(weatherInterval)
    }
  }, [])

  const nexusTemp = readings['dht11_temp']?.value ?? null
  const nexusHum = readings['dht11_humidity']?.value ?? null
  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-xl font-semibold mb-6">Nexus</h1>

      <div className="grid grid-cols-2 gap-4 max-w-sm mb-8">
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

      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Buiten — Voorschoten (Open-Meteo)
      </h2>
      <div className="grid grid-cols-3 gap-4 max-w-lg">
        <WeatherCard label="Temperatuur" outdoor={weather.temperature} nexus={nexusTemp} unit="°C" />
        <WeatherCard label="Vochtigheid" outdoor={weather.humidity} nexus={nexusHum} unit="%" />
      </div>
    </div>
  )
}
