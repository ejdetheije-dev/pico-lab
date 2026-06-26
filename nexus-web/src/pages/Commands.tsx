import { useState } from 'react'
import { supabase } from '../lib/supabase'

type Status = 'idle' | 'loading' | 'ok' | 'error'

function useCommand() {
  const [status, setStatus] = useState<Status>('idle')

  async function stuur(command: string, payload: object = {}) {
    setStatus('loading')
    const { error } = await supabase.from('commands').insert({ command, payload })
    if (error) {
      setStatus('error')
    } else {
      setStatus('ok')
      setTimeout(() => setStatus('idle'), 2000)
    }
  }

  return { status, stuur }
}

function ActionButton({
  label,
  onClick,
  status,
  color = 'gray',
}: {
  label: string
  onClick: () => void
  status: Status
  color?: 'gray' | 'green' | 'red' | 'blue'
}) {
  const base = 'rounded px-4 py-2 text-sm font-medium transition-all duration-150 w-full'
  const colors = {
    gray: 'bg-gray-700 hover:bg-gray-600',
    green: 'bg-green-700 hover:bg-green-600',
    red: 'bg-red-700 hover:bg-red-600',
    blue: 'bg-blue-600 hover:bg-blue-500',
  }
  const stateClass =
    status === 'loading' ? 'opacity-60 cursor-wait scale-95' :
    status === 'ok' ? 'bg-green-600 scale-95' :
    status === 'error' ? 'bg-red-600' :
    colors[color]

  return (
    <button
      className={`${base} ${stateClass}`}
      onClick={onClick}
      disabled={status === 'loading'}
    >
      {status === 'loading' ? '...' : status === 'ok' ? 'Verstuurd' : label}
    </button>
  )
}

export default function Commands() {
  const [regel1, setRegel1] = useState('')
  const [regel2, setRegel2] = useState('')
  const lcd = useCommand()
  const buzzerCmd = useCommand()
  const fanOn = useCommand()
  const fanOff = useCommand()
  const ota = useCommand()

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-xl font-semibold mb-6">Commands</h1>

      <div className="bg-gray-900 rounded-xl p-6 max-w-sm flex flex-col gap-4">

        <h2 className="text-sm text-gray-400 uppercase tracking-wide">Bericht op LCD</h2>
        <input
          className="bg-gray-800 rounded px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Regel 1 (max 16 tekens)"
          maxLength={16}
          value={regel1}
          onChange={e => setRegel1(e.target.value)}
        />
        <input
          className="bg-gray-800 rounded px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Regel 2 (optioneel)"
          maxLength={16}
          value={regel2}
          onChange={e => setRegel2(e.target.value)}
        />
        <ActionButton
          label="Verstuur naar LCD"
          status={!regel1 ? 'idle' : lcd.status}
          color="blue"
          onClick={() => regel1 && lcd.stuur('display_message', { regel1, regel2 })}
        />

        <hr className="border-gray-700" />

        <h2 className="text-sm text-gray-400 uppercase tracking-wide">Buzzer</h2>
        <ActionButton
          label="Piep"
          status={buzzerCmd.status}
          color="gray"
          onClick={() => buzzerCmd.stuur('buzzer', { freq: 880, duur_ms: 300 })}
        />

        <hr className="border-gray-700" />

        <h2 className="text-sm text-gray-400 uppercase tracking-wide">Ventilator</h2>
        <div className="flex gap-2">
          <ActionButton
            label="Aan"
            status={fanOn.status}
            color="green"
            onClick={() => fanOn.stuur('fan_on')}
          />
          <ActionButton
            label="Uit"
            status={fanOff.status}
            color="red"
            onClick={() => fanOff.stuur('fan_off')}
          />
        </div>

        <hr className="border-gray-700" />

        <h2 className="text-sm text-gray-400 uppercase tracking-wide">Firmware</h2>
        <ActionButton
          label="Software update"
          status={ota.status}
          color="blue"
          onClick={() => ota.stuur('ota_update')}
        />

      </div>
    </div>
  )
}
