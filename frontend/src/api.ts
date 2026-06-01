// In dev (npm run dev) this hits localhost:8000 directly.
// In Docker the nginx proxy forwards /api/ and /ws/ to the backend service.
const BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

function token() {
  return localStorage.getItem('token')
}

function authHeaders() {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options)
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Request failed')
  return data as T
}

export const api = {
  signup(email: string, password: string) {
    return request<{ token: string; email: string }>('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
  },

  login(email: string, password: string) {
    return request<{ token: string; email: string }>('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
  },

  getRegions() {
    return request<{ regions: string[] }>('/api/resource-groups', { headers: authHeaders() })
  },

  async analyze(region: string, onProgress: (msg: string) => void) {
    // Start analysis
    const { analysis_id, result } = await request<{ analysis_id: number; result: unknown }>(
      '/api/analyze',
      {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ resource_group: region }),
      }
    )

    // Connect WebSocket for live progress (best-effort)
    try {
      const wsBase = import.meta.env.DEV ? 'ws://localhost:8000' : `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}`
      const ws = new WebSocket(`${wsBase}/ws/progress/${analysis_id}`)
      ws.onmessage = e => onProgress(e.data)
    } catch {}

    return { analysis_id, result }
  },

  getHistory() {
    return request<{ id: number; resource_group: string; resources_scanned: number; issues_found: number; estimated_savings: string; status: string; created_at: string }[]>(
      '/api/history',
      { headers: authHeaders() }
    )
  },

  getAnalysis(id: number) {
    return request<{ analysis_result: unknown }>(`/api/history/${id}`, { headers: authHeaders() })
  },
}
