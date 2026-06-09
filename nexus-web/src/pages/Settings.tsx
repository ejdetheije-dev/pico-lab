import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

const DEFAULTS = {
  poll_interval_s: 60,
  temp_alert_threshold: 30,
}

async function fetchSettings(): Promise<typeof DEFAULTS> {
  const { data, error } = await supabase.from('settings').select('key, value')
  if (error || !data) return { ...DEFAULTS }
  const map: Record<string, number> = {}
  for (const row of data) map[row.key] = Number(row.value)
  return {
    poll_interval_s: map['poll_interval_s'] ?? DEFAULTS.poll_interval_s,
    temp_alert_threshold: map['temp_alert_threshold'] ?? DEFAULTS.temp_alert_threshold,
  }
}

export default function Settings() {
  const [pollInterval, setPollInterval] = useState(DEFAULTS.poll_interval_s)
  const [tempDrempel, setTempDrempel] = useState(DEFAULTS.temp_alert_threshold)
  const [bezig, setBezig] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    fetchSettings().then(s => {
      setPollInterval(s.poll_interval_s)
      setTempDrempel(s.temp_alert_threshold)
    })
  }, [])

  async function opslaan() {
    setBezig(true)
    setStatus('')

    const { error: upsertError } = await supabase.from('settings').upsert(
      [
        { key: 'poll_interval_s', value: pollInterval },
        { key: 'temp_alert_threshold', value: tempDrempel },
      ],
      { onConflict: 'key' }
    )

    if (upsertError) {
      setBezig(false)
      setStatus('Fout: ' + upsertError.message)
      return
    }

    const { error: cmdError } = await supabase.from('commands').insert({
      command: 'set_setting',
      payload: {},
    })

    setBezig(false)
    setStatus(cmdError ? 'Fout: ' + cmdError.message : 'Opgeslagen')
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-xl font-semibold mb-6">Settings</h1>

      <div className="bg-gray-900 rounded-xl p-6 max-w-sm flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">Poll interval (seconden)</label>
          <input
            type="number"
            min={10}
            max={3600}
            className="bg-gray-800 rounded px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500"
            value={pollInterval}
            onChange={e => setPollInterval(Number(e.target.value))}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">Temperatuur drempel (°C)</label>
          <input
            type="number"
            min={0}
            max={60}
            className="bg-gray-800 rounded px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500"
            value={tempDrempel}
            onChange={e => setTempDrempel(Number(e.target.value))}
          />
        </div>

        <button
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-4 py-2 text-sm font-medium"
          onClick={opslaan}
          disabled={bezig}
        >
          Opslaan
        </button>

        {status && <p className="text-sm text-gray-400">{status}</p>}
      </div>
    </div>
  )
}
