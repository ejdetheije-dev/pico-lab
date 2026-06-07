import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Commands from './pages/Commands'

type Pagina = 'dashboard' | 'commands'

export default function App() {
  const [pagina, setPagina] = useState<Pagina>('dashboard')

  return (
    <div>
      <nav className="bg-gray-900 px-8 py-3 flex gap-4">
        <button
          className={`text-sm ${pagina === 'dashboard' ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}`}
          onClick={() => setPagina('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`text-sm ${pagina === 'commands' ? 'text-white font-medium' : 'text-gray-400 hover:text-white'}`}
          onClick={() => setPagina('commands')}
        >
          Commands
        </button>
      </nav>
      {pagina === 'dashboard' ? <Dashboard /> : <Commands />}
    </div>
  )
}
