import { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function Commands() {
  const [regel1, setRegel1] = useState('')
  const [regel2, setRegel2] = useState('')
  const [bezig, setBezig] = useState(false)
  const [status, setStatus] = useState('')

  async function verstuur() {
    if (!regel1) return
    setBezig(true)
    setStatus('')
    const { error } = await supabase.from('commands').insert({
      command: 'display_message',
      payload: { regel1, regel2 },
    })
    setBezig(false)
    if (error) {
      setStatus('Fout: ' + error.message)
    } else {
      setStatus('Verstuurd')
      setRegel1('')
      setRegel2('')
    }
  }

  async function piep() {
    setBezig(true)
    setStatus('')
    const { error } = await supabase.from('commands').insert({
      command: 'buzzer',
      payload: { freq: 880, duur_ms: 300 },
    })
    setBezig(false)
    setStatus(error ? 'Fout: ' + error.message : 'Verstuurd')
  }

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
        <button
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded px-4 py-2 text-sm font-medium"
          onClick={verstuur}
          disabled={bezig || !regel1}
        >
          Verstuur naar LCD
        </button>

        <hr className="border-gray-700" />

        <button
          className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded px-4 py-2 text-sm font-medium"
          onClick={piep}
          disabled={bezig}
        >
          Buzzer piep
        </button>

        {status && <p className="text-sm text-gray-400">{status}</p>}
      </div>
    </div>
  )
}
