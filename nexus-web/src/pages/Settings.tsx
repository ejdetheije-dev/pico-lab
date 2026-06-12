import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

const DEFAULTS = {
  poll_interval_s: 60,
  temp_alert_threshold: 30,
  pushover_enabled: true,
}

async function fetchSettings() {
  const { data, error } = await supabase.from('settings').select('key, value')
  if (error || !data) return { ...DEFAULTS }
  const map: Record<string, string> = {}
  for (const row of data) map[row.key] = row.value
  return {
    poll_interval_s: map['poll_interval_s'] ? Number(map['poll_interval_s']) : DEFAULTS.poll_interval_s,
    temp_alert_threshold: map['temp_alert_threshold'] ? Number(map['temp_alert_threshold']) : DEFAULTS.temp_alert_threshold,
    pushover_enabled: map['pushover_enabled'] !== undefined ? map['pushover_enabled'] === 'true' : DEFAULTS.pushover_enabled,
  }
}

export default function Settings() {
  const [pollInterval, setPollInterval] = useState(DEFAULTS.poll_interval_s)
  const [tempDrempel, setTempDrempel] = useState(DEFAULTS.temp_alert_threshold)
  const [pushoverEnabled, setPushoverEnabled] = useState(DEFAULTS.pushover_enabled)
  const [bezig, setBezig] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    fetchSettings().then(s => {
      setPollInterval(s.poll_interval_s)
      setTempDrempel(s.temp_alert_threshold)
      setPushoverEnabled(s.pushover_enabled)
    })
  }, [])

  async function opslaan() {
    setBezig(true)
    setStatus('')

    const { error: upsertError } = await supabase.from('settings').upsert(
      [
        { key: 'poll_interval_s', value: pollInterval },
        { key: 'temp_alert_threshold', value: tempDrempel },
        { key: 'pushover_enabled', value: pushoverEnabled ? 'true' : 'false' },
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

        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-400">Pushover notificaties</label>
          <button
            onClick={() => setPushoverEnabled(v => !v)}
            className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
              pushoverEnabled ? 'bg-blue-600' : 'bg-gray-600'
            }`}
          >
            <span
              className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${
                pushoverEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
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
