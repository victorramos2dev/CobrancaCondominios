import { useEffect, useState } from 'react'
import { fetchDashboard, fetchInadimplenciaResumo } from '../services/condominioService'
import { formatCurrency } from '../utils/format'

function StatCard({ label, value, sub, accent, delay = 0 }) {
  return (
    <div
      className="card p-5 animate-fade-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-serif mt-1 ${accent || 'text-slate-900'}`}>{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const [data, setData]   = useState(null)
  const [inad, setInad]   = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([fetchDashboard(), fetchInadimplenciaResumo()])
      .then(([d, i]) => { setData(d); setInad(i) })
      .catch(() => setError('Erro ao carregar dados do dashboard.'))
  }, [])

  if (error) return (
    <div className="rounded-xl bg-red-50 border border-red-200 p-6 text-red-700 text-sm">{error}</div>
  )

  if (!data) return <DashboardSkeleton />

  const pctPago = data.total_cobrancas ? Math.round((data.total_pagas / data.total_cobrancas) * 100) : 0

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard Financeiro</h1>
          <p className="text-sm text-slate-500 mt-0.5">Visão geral da arrecadação condominial</p>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Condomínios"     value={data.total_condominios}           delay={0} />
        <StatCard label="Unidades"        value={data.total_unidades}              delay={50} />
        <StatCard label="Total Cobranças" value={data.total_cobrancas}             delay={100} />
        <StatCard label="Acordos Ativos"  value={data.total_acordos}               delay={150} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <StatCard
          label="Valor Recebido"
          value={formatCurrency(data.valor_total_recebido)}
          accent="text-emerald-600"
          sub={`${data.total_pagas} cobranças pagas`}
          delay={200}
        />
        <StatCard
          label="Em Aberto"
          value={formatCurrency(data.valor_total_em_aberto)}
          accent="text-amber-600"
          sub={`${data.total_pendentes} pendentes · ${data.total_vencidas} vencidas`}
          delay={250}
        />
        <div className="card p-5 animate-fade-up" style={{ animationDelay: '300ms' }}>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">Taxa de Adimplência</p>
          <div className="flex items-end gap-2 mb-2">
            <span className="text-3xl font-serif text-slate-900">{pctPago}%</span>
            <span className="text-xs text-slate-400 mb-1">das cobranças pagas</span>
          </div>
          <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${pctPago}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>0%</span><span>100%</span>
          </div>
        </div>
      </div>

      {/* Status breakdown */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Pagas',     count: data.total_pagas,     cls: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
          { label: 'Pendentes', count: data.total_pendentes, cls: 'bg-amber-100 text-amber-700 border-amber-200' },
          { label: 'Vencidas',  count: data.total_vencidas,  cls: 'bg-red-100 text-red-700 border-red-200' },
        ].map(({ label, count, cls }, i) => (
          <div key={label} className={`rounded-xl border px-4 py-3 ${cls} animate-fade-up`} style={{ animationDelay: `${350 + i * 50}ms` }}>
            <p className="text-2xl font-serif">{count}</p>
            <p className="text-xs font-medium uppercase tracking-wide">{label}</p>
          </div>
        ))}
      </div>

      {/* Inadimplência por condomínio */}
      {inad.length > 0 && (
        <div className="card p-0 overflow-hidden animate-fade-up" style={{ animationDelay: '500ms' }}>
          <div className="px-5 py-4 border-b border-slate-100">
            <h2 className="font-serif text-lg text-slate-900">Inadimplência por Condomínio</h2>
          </div>
          <div className="divide-y divide-slate-50">
            {inad.map((row, i) => (
              <div key={i} className="flex items-center justify-between px-5 py-3 hover:bg-slate-50/70 transition-colors">
                <div>
                  <p className="text-sm font-medium text-slate-800">{row.condominio}</p>
                  <p className="text-xs text-slate-400">{row.qtd_cobrancas_vencidas} cobranças vencidas</p>
                </div>
                <span className="text-sm font-semibold text-red-600">{formatCurrency(row.valor_total_vencido)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-slate-200 rounded w-48" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-slate-200 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => <div key={i} className="h-28 bg-slate-200 rounded-xl" />)}
      </div>
    </div>
  )
}
