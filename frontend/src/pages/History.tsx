import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Navbar from '../components/Navbar'

interface HistoryItem {
  id: number
  resource_group: string
  resources_scanned: number
  issues_found: number
  estimated_savings: string
  status: string
  created_at: string
}

export default function History() {
  const navigate = useNavigate()
  const [items, setItems] = useState<HistoryItem[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.getHistory()
      .then(setItems)
      .catch(() => setError('Failed to load history'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold mb-8">Analysis History</h2>

        {error && <p className="text-red-400">{error}</p>}

        {items.length === 0 && !error && (
          <p className="text-gray-400">No analyses yet. Run your first analysis from the Dashboard.</p>
        )}

        <div className="space-y-3">
          {items.map(item => (
            <button
              key={item.id}
              onClick={() => navigate(`/report/${item.id}`)}
              className="w-full bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-5 text-left transition"
            >
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <p className="font-semibold text-white">{item.resource_group}</p>
                  <p className="text-gray-400 text-sm mt-0.5">{new Date(item.created_at).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-300">{item.resources_scanned} resources</span>
                  <span className="text-red-400 font-medium">{item.issues_found} issues</span>
                  <span className="text-green-400 font-medium">{item.estimated_savings}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    item.status === 'complete' ? 'bg-green-900/40 text-green-300' : 'bg-yellow-900/40 text-yellow-300'
                  }`}>
                    {item.status}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
