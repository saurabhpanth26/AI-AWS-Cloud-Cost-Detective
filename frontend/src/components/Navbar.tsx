import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()
  const email = localStorage.getItem('email')

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    navigate('/login')
  }

  return (
    <nav className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/dashboard" className="text-white font-bold text-lg tracking-tight">
          Cloud Cost Detective
        </Link>
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className="text-gray-400 hover:text-white text-sm transition">Dashboard</Link>
          <Link to="/history" className="text-gray-400 hover:text-white text-sm transition">History</Link>
          <div className="flex items-center gap-3">
            <span className="text-gray-500 text-sm">{email}</span>
            <button
              onClick={logout}
              className="text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
