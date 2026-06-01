import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Navbar from '../components/Navbar'
import ProgressTracker from '../components/ProgressTracker'

export default function Dashboard() {
  const navigate = useNavigate()
  const [regions, setRegions] = useState<string[]>([])
  const [selectedRegion, setSelectedRegion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    api.getRegions()
      .then(data => {
        setRegions(data.regions)
        if (data.regions.length > 0) setSelectedRegion(data.regions[0])
      })
      .catch(() => setError('Failed to load AWS regions. Check your AWS credentials.'))
  }, [])

  async function runAnalysis() {
    if (!selectedRegion) return
    setLoading(true)
    setError('')
    setProgress([])

    try {
      const { analysis_id, result } = await api.analyze(selectedRegion, (msg: string) => {
        setProgress(prev => [...prev, msg])
      })
      navigate(`/report/${analysis_id}`, { state: { result } })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
      wsRef.current?.close()
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold mb-2">AWS Cost Analysis</h2>
        <p className="text-gray-400 mb-8">Select an AWS region to scan for cost issues.</p>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">AWS Region</label>
            <select
              value={selectedRegion}
              onChange={e => setSelectedRegion(e.target.value)}
              disabled={loading}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {regions.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {error && <p className="text-red-400 text-sm bg-red-900/20 border border-red-800 rounded-lg p-3">{error}</p>}

          <button
            onClick={runAnalysis}
            disabled={loading || !selectedRegion}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition"
          >
            {loading ? 'Running Analysis...' : 'Run Analysis'}
          </button>
        </div>

        {progress.length > 0 && (
          <div className="mt-8">
            <ProgressTracker steps={progress} />
          </div>
        )}
      </div>
    </div>
  )
}
