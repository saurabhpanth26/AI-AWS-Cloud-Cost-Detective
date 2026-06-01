interface Props {
  steps: string[]
}

export default function ProgressTracker({ steps }: Props) {
  const allSteps = [
    'Scanning resources in region...',
    'Analyzing costs with Claude AI...',
    'Storing results...',
    'Analysis complete',
  ]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">Progress</h3>
      <div className="space-y-3">
        {allSteps.map((step, i) => {
          const done = steps.some(s => s.includes(step.split('...')[0].trim()) || s === step)
          const active = !done && steps.length === i
          return (
            <div key={i} className="flex items-center gap-3">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold transition-all ${
                done
                  ? 'bg-green-500 text-white'
                  : active
                  ? 'bg-blue-500 text-white animate-pulse'
                  : 'bg-gray-700 text-gray-500'
              }`}>
                {done ? '✓' : i + 1}
              </div>
              <span className={`text-sm transition-colors ${
                done ? 'text-green-300' : active ? 'text-blue-300' : 'text-gray-500'
              }`}>
                {step}
              </span>
            </div>
          )
        })}
      </div>
      {steps.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <p className="text-xs text-gray-500 font-mono">{steps[steps.length - 1]}</p>
        </div>
      )}
    </div>
  )
}
