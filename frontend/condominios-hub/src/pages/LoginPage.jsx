import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.username, form.password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Credenciais inválidas. Verifique usuário e senha.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex w-[45%] bg-brand-950 flex-col justify-between p-12 relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-700/20 rounded-full blur-3xl" />
          <div className="absolute bottom-24 -left-12 w-72 h-72 bg-brand-600/20 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] border border-brand-800/40 rounded-full" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-brand-800/20 rounded-full" />
        </div>

        <div className="relative z-10">
          <span className="font-serif text-3xl text-white">Condo<span className="text-brand-300">Gest</span></span>
          <p className="text-brand-400 text-xs tracking-widest uppercase mt-1 font-light">Sistema de Gestão Condominial</p>
        </div>

        <div className="relative z-10">
          <blockquote className="font-serif text-2xl text-white/90 leading-snug italic mb-4">
            "Automatize a arrecadação.<br />Elimine a inadimplência."
          </blockquote>
          <div className="flex gap-6 text-center">
            {[['Dashboard', 'Financeiro'], ['Controle de', 'Inadimplência'], ['Acordos de', 'Parcelamento']].map(([a, b]) => (
              <div key={a} className="text-xs text-brand-300">
                <div className="font-semibold">{a}</div>
                <div className="text-brand-400">{b}</div>
              </div>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-brand-500 text-xs">© 2025 CondoGest · SENAI Roberto Mange</p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-sm animate-fade-up">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8 text-center">
            <span className="font-serif text-3xl text-brand-950">Condo<span className="text-brand-500">Gest</span></span>
          </div>

          <div className="card p-8">
            <h1 className="font-serif text-2xl text-slate-900 mb-1">Bem-vindo de volta</h1>
            <p className="text-sm text-slate-500 mb-6">Entre com suas credenciais para continuar</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Usuário</label>
                <input
                  className="input"
                  type="text"
                  placeholder="seu.usuario"
                  value={form.username}
                  onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                  required
                  autoFocus
                />
              </div>
              <div>
                <label className="label">Senha</label>
                <input
                  className="input"
                  type="password"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  required
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 animate-fade-in">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="btn-primary w-full justify-center py-2.5 mt-2"
                disabled={loading}
              >
                {loading ? (
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                  </svg>
                ) : 'Entrar'}
              </button>
            </form>
          </div>

          <p className="text-center text-xs text-slate-400 mt-6">
            Problemas para acessar? Contate o administrador.
          </p>
        </div>
      </div>
    </div>
  )
}
