import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts'
import { supabase } from '../lib/supabase'

// ── types ────────────────────────────────────────────────────────────────────

type Punt = { nr: number; waarde: number }
type Event = { id: number; type: string; payload: Record<string, unknown> }
type SensorConf = { sensor: string; label: string; unit: string; kleur: string }

// ── config ────────────────────────────────────────────────────────────────────

const SENSOREN: SensorConf[] = [
  { sensor: 'dht11_temp',      label: 'Temperatuur',      unit: '°C',  kleur: '#f97316' },
  { sensor: 'dht11_humidity',  label: 'Luchtvochtigheid', unit: '%',   kleur: '#3b82f6' },
  { sensor: 'ldr_light',       label: 'Licht',            unit: '%',   kleur: '#eab308' },
  { sensor: 'bmp180_pressure', label: 'Luchtdruk',        unit: 'hPa', kleur: '#8b5cf6' },
]

const EVENT_FILTERS = [
  { value: '',                label: 'Alles' },
  { value: 'motion_detected', label: 'Beweging' },
  { value: 'motion_absent',   label: 'Geen beweging' },
  { value: 'pushover_sent',   label: 'Pushover' },
]

// ── data fetchers ─────────────────────────────────────────────────────────────

async function fetchHistorie(sensor: string): Promise<Punt[]> {
  const { data } = await supabase
    .from('sensor_readings')
    .select('id, value')
    .eq('sensor', sensor)
    .order('id', { ascending: false })
    .limit(50)
  if (!data) return []
  return data.reverse().map((r, i) => ({ nr: i + 1, waarde: r.value }))
}

async function fetchEvents(filter: string): Promise<Event[]> {
  let query = supabase
    .from('events')
    .select('id, type, payload')
    .order('id', { ascending: false })
    .limit(30)
  if (filter) query = query.eq('type', filter)
  const { data } = await query
  return (data ?? []) as Event[]
}

// ── sub-components ────────────────────────────────────────────────────────────

function SensorGrafiek({ sensor, label, unit, kleur }: SensorConf) {
  const [data, setData] = useState<Punt[]>([])

  useEffect(() => {
    fetchHistorie(sensor).then(setData)
    const t = setInterval(() => fetchHistorie(sensor).then(setData), 30_000)
    return () => clearInterval(t)
  }, [sensor])

  return (
    <div className="bg-gray-900 rounded-xl p-4 flex flex-col gap-2">
      <span className="text-sm text-gray-400">{label} ({unit})</span>
      {data.length === 0 ? (
        <span className="text-xs text-gray-600 py-8 text-center">Geen data</span>
      ) : (
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="nr" tick={{ fontSize: 10, fill: '#9ca3af' }} interval="preserveStartEnd" />
            <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <Tooltip
              contentStyle={{ background: '#111827', border: 'none', fontSize: 12 }}
              formatter={(v) => [`${Number(v)} ${unit}`, label]}
              labelFormatter={(n) => `meting ${n}`}
            />
            <Line
              type="monotone"
              dataKey="waarde"
              stroke={kleur}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

function EventTypeLabel({ type }: { type: string }) {
  const kleuren: Record<string, string> = {
    motion_detected: 'bg-orange-500',
    motion_absent:   'bg-gray-500',
    pushover_sent:   'bg-blue-500',
  }
  const kleur = kleuren[type] ?? 'bg-gray-600'
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full text-white ${kleur}`}>
      {type}
    </span>
  )
}

// ── page ──────────────────────────────────────────────────────────────────────

export default function Grafieken() {
  const [filter, setFilter] = useState('')
  const [events, setEvents] = useState<Event[]>([])

  useEffect(() => {
    fetchEvents(filter).then(setEvents)
    const t = setInterval(() => fetchEvents(filter).then(setEvents), 10_000)
    return () => clearInterval(t)
  }, [filter])

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8 flex flex-col gap-8">

      <section>
        <h2 className="text-lg font-semibold mb-4">Grafieken</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SENSOREN.map(s => <SensorGrafiek key={s.sensor} {...s} />)}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Event log</h2>
        <div className="flex gap-2 mb-4 flex-wrap">
          {EVENT_FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                filter === f.value
                  ? 'bg-blue-600 border-blue-600 text-white'
                  : 'border-gray-600 text-gray-400 hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="flex flex-col gap-2">
          {events.length === 0 && (
            <p className="text-sm text-gray-600">Geen events gevonden.</p>
          )}
          {events.map(e => (
            <div key={e.id} className="bg-gray-900 rounded-lg px-4 py-3 flex items-start gap-3">
              <EventTypeLabel type={e.type} />
              <span className="text-xs text-gray-400 font-mono break-all">
                {Object.keys(e.payload ?? {}).length > 0
                  ? JSON.stringify(e.payload)
                  : '—'}
              </span>
            </div>
          ))}
        </div>
      </section>

    </div>
  )
}
