import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

type MoodWaarde = 'fijn' | 'matig' | 'slecht'
type MoodRecord = { user_name: string; mood: string; tekst: string; created_at: string }

const MOOD_STIJL: Record<MoodWaarde, string> = {
  fijn:   'bg-green-700 hover:bg-green-600',
  matig:  'bg-yellow-700 hover:bg-yellow-600',
  slecht: 'bg-red-700 hover:bg-red-600',
}

const MOOD_TEKST_KLEUR: Record<string, string> = {
  fijn:   'text-green-400',
  matig:  'text-yellow-400',
  slecht: 'text-red-400',
}

async function fetchOverzicht(): Promise<MoodRecord[]> {
  const { data } = await supabase
    .from('moods')
    .select('user_name, mood, tekst, created_at')
    .order('created_at', { ascending: false })
    .limit(200)
  if (!data) return []
  const gezien = new Set<string>()
  return data.filter(r => {
    if (gezien.has(r.user_name)) return false
    gezien.add(r.user_name)
    return true
  })
}

export default function Mood() {
  const [naam, setNaam] = useState('')
  const [code, setCode] = useState('')
  const [tekst, setTekst] = useState('')
  const [bezig, setBezig] = useState(false)
  const [fout, setFout] = useState<string | null>(null)
  const [succes, setSucces] = useState<string | null>(null)
  const [overzicht, setOverzicht] = useState<MoodRecord[]>([])

  useEffect(() => {
    fetchOverzicht().then(setOverzicht)
  }, [])

  async function verstuurMood(mood: MoodWaarde) {
    if (!naam.trim() || code.length !== 3) return
    setBezig(true)
    setFout(null)
    setSucces(null)

    const { data: bestaand } = await supabase
      .from('mood_users')
      .select('code')
      .eq('name', naam.trim())
      .maybeSingle()

    if (bestaand) {
      if (bestaand.code !== code) {
        setFout('Verkeerde code.')
        setBezig(false)
        return
      }
    } else {
      const { error } = await supabase
        .from('mood_users')
        .insert({ name: naam.trim(), code })
      if (error) {
        setFout('Fout bij aanmaken gebruiker.')
        setBezig(false)
        return
      }
    }

    await supabase.from('moods').insert({
      user_name: naam.trim(),
      mood,
      tekst: tekst.trim(),
    })

    if (mood === 'slecht' || mood === 'fijn') {
      await supabase.from('commands').insert({
        command: 'mood_alert',
        payload: { naam: naam.trim(), tekst: tekst.trim(), mood },
      })
    }

    setSucces(`Mood "${mood}" opgeslagen.`)
    setTekst('')
    setBezig(false)
    fetchOverzicht().then(setOverzicht)
  }

  const klaarVoorMood = naam.trim().length > 0 && code.length === 3

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-xl font-semibold mb-6">Mood</h1>

      <div className="max-w-sm space-y-4 mb-10">
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="text-xs text-gray-400 mb-1 block">Naam</label>
            <input
              className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-gray-600"
              value={naam}
              onChange={e => setNaam(e.target.value)}
              placeholder="Jouw naam"
              maxLength={20}
            />
          </div>
          <div className="w-24">
            <label className="text-xs text-gray-400 mb-1 block">Code</label>
            <input
              className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-gray-600 tracking-widest text-center"
              value={code}
              onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 3))}
              placeholder="•••"
              inputMode="numeric"
            />
          </div>
        </div>

        <div>
          <label className="text-xs text-gray-400 mb-1 block">Boodschap (optioneel)</label>
          <input
            className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-gray-600"
            value={tekst}
            onChange={e => setTekst(e.target.value.slice(0, 32))}
            placeholder="Korte boodschap..."
          />
        </div>

        <div className="flex gap-3">
          {(['fijn', 'matig', 'slecht'] as MoodWaarde[]).map(m => (
            <button
              key={m}
              disabled={!klaarVoorMood || bezig}
              onClick={() => verstuurMood(m)}
              className={`flex-1 py-3 rounded-xl text-sm font-medium transition-colors ${MOOD_STIJL[m]} disabled:opacity-30 disabled:cursor-not-allowed`}
            >
              {m}
            </button>
          ))}
        </div>

        {fout   && <p className="text-sm text-red-400">{fout}</p>}
        {succes && <p className="text-sm text-green-400">{succes}</p>}
      </div>

      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Overzicht</h2>
      {overzicht.length === 0 ? (
        <p className="text-sm text-gray-600">Nog geen moods geregistreerd.</p>
      ) : (
        <div className="space-y-2 max-w-sm">
          {overzicht.map(r => (
            <div key={r.user_name} className="bg-gray-900 rounded-xl px-4 py-3 flex items-center justify-between">
              <div>
                <span className="text-sm font-medium">{r.user_name}</span>
                {r.tekst && <span className="text-xs text-gray-400 ml-2">"{r.tekst}"</span>}
              </div>
              <div className="text-right">
                <span className={`text-sm font-bold ${MOOD_TEKST_KLEUR[r.mood] ?? 'text-gray-400'}`}>{r.mood}</span>
                <div className="text-xs text-gray-500">
                  {new Date(r.created_at).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
