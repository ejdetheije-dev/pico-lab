import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Commands from './pages/Commands'
import Settings from './pages/Settings'
import Grafieken from './pages/Grafieken'
import Mood from './pages/Mood'

type Pagina = 'dashboard' | 'grafieken' | 'commands' | 'settings' | 'mood'

const NAV: { id: Pagina; label: string }[] = [
  { id: 'dashboard',  label: 'Dashboard' },
  { id: 'grafieken',  label: 'Grafieken' },
  { id: 'commands',   label: 'Commands' },
  { id: 'settings',   label: 'Settings' },
  { id: 'mood',       label: 'Mood' },
]

export default function App() {
  const [pagina, setPagina] = useState<Pagina>('dashboard')

  return (
    <div>
      <nav className="bg-gray-900 px-8 py-3 flex gap-4">
        {NAV.map(({ id, label }) => (
          <button
            key={id}
            className={`text-sm ${pagina === id ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}`}
            onClick={() => setPagina(id)}
          >
            {label}
          </button>
        ))}
      </nav>
      {pagina === 'dashboard'  && <Dashboard />}
      {pagina === 'grafieken'  && <Grafieken />}
      {pagina === 'commands'   && <Commands />}
      {pagina === 'settings'   && <Settings />}
      {pagina === 'mood'       && <Mood />}
    </div>
  )
}
