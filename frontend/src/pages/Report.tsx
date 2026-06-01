import { useEffect, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import Navbar from '../components/Navbar'

interface Issue {
  resource_id: string
  resource_type: string
  issue_type: string
  severity: 'high' | 'medium' | 'low'
  explanation: string
  fix_command: string
}

interface AnalysisResult {
  summary: string
  total_resources: number
  issues_found: number
  estimated_monthly_savings: string
  issues: Issue[]
}

const severityColors: Record<string, string> = {
  high: 'bg-red-900/40 text-red-300 border border-red-700',
  medium: 'bg-yellow-900/40 text-yellow-300 border border-yellow-700',
  low: 'bg-green-900/40 text-green-300 border border-green-700',
}

export default function Report() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [result, setResult] = useState<AnalysisResult | null>((location.state?.result as AnalysisResult) ?? null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState<string | null>(null)

  useEffect(() => {
    if (!result && id) {
      api.getAnalysis(Number(id))
        .then(data => setResult(data.analysis_result as AnalysisResult))
        .catch(() => setError('Failed to load analysis'))
    }
  }, [id, result])

  function copyToClipboard(text: string, key: string) {
    navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  if (error) return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p className="text-red-400">{error}</p>
      </div>
    </div>
  )

  if (!result) return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-12">
        <p className="text-gray-400">Loading report...</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-12 space-y-8">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white text-sm">← Back</button>
          <h2 className="text-2xl font-bold">Analysis Report</h2>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-blue-400">{result.total_resources}</p>
            <p className="text-gray-400 text-sm mt-1">Resources Scanned</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-red-400">{result.issues_found}</p>
            <p className="text-gray-400 text-sm mt-1">Issues Found</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-green-400">{result.estimated_monthly_savings}</p>
            <p className="text-gray-400 text-sm mt-1">Est. Monthly Savings</p>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-2">Summary</h3>
          <p className="text-gray-300">{result.summary}</p>
        </div>

        {/* Issues */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Issues</h3>
          {result.issues.length === 0 && (
            <p className="text-gray-400">No issues found. Your AWS resources look well-optimized!</p>
          )}
          {result.issues.map((issue, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <span className="font-mono text-blue-300 text-sm">{issue.resource_id}</span>
                  <span className="text-gray-500 text-sm ml-2">· {issue.resource_type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded-full bg-gray-800 text-gray-300">{issue.issue_type}</span>
                  <span className={`text-xs px-2 py-1 rounded-full font-semibold ${severityColors[issue.severity]}`}>
                    {issue.severity.toUpperCase()}
                  </span>
                </div>
              </div>
              <p className="text-gray-300 text-sm">{issue.explanation}</p>
              <div className="relative">
                <pre className="bg-gray-950 border border-gray-700 rounded-lg p-4 text-sm text-green-300 overflow-x-auto">
                  {issue.fix_command}
                </pre>
                <button
                  onClick={() => copyToClipboard(issue.fix_command, `issue-${i}`)}
                  className="absolute top-2 right-2 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded transition"
                >
                  {copied === `issue-${i}` ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
