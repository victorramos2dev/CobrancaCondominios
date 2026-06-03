import { useEffect, useState } from 'react'
import { fetchCobrancas, fetchInadimplenciaResumo, fetchCondominios, fetchUnidades } from '../services/condominioService'
import { formatCurrency, formatDate, formatCompetencia } from '../utils/format'

export default function InadimplenciaPage() {
  const [resumo, setResumo]       = useState([])
  const [cobrancas, setCobrancas] = useState([])
  const [condominios, setCondominios] = useState([])
  const [unidades, setUnidades]   = useState([])
  const [filter, setFilter]       = useState({ condominio: '', unidade: '' })
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    fetchInadimplenciaResumo().then(setResumo).catch(() => {})
    fetchCondominios().then(d => setCondominios(Array.isArray(d) ? d : d.results ?? []))
    fetchUnidades().then(d => setUnidades(Array.isArray(d) ? d : d.results ?? []))
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = { status: 'VENCIDO' }
    if (filter.condominio) params.condominio = filter.condominio
    if (filter.unidade)    params.unidade    = filter.unidade
    fetchCobrancas(params)
      .then(d => setCobrancas(Array.isArray(d) ? d : d.results ?? []))
      .finally(() => setLoading(false))
  }, [filter])

  const totalVencido = cobrancas.reduce((acc, c) => acc + Number(c.valor) + Number(c.multa || 0) + Number(c.juros || 0), 0)

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Inadimplência</h1>
          <p className="text-sm text-slate-500 mt-0.5">Cobranças vencidas e controle de atrasos</p>
        </div>
      </div>

      {/* Summary cards */}
      {resumo.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumo.map((r, i) => (
            <div key={i} className="card p-4 border-l-4 border-red-400 animate-fade-up" style={{ animationDelay: `${i * 60}ms` }}>
              <p className="text-sm font-medium text-slate-700 truncate">{r.condominio}</p>
              <div className="flex items-end justify-between mt-2">
                <span className="text-xs text-slate-400">{r.qtd_cobrancas_vencidas} cobranças</span>
                <span className="text-lg font-serif text-red-600">{formatCurrency(r.valor_total_vencido)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <select className="select w-48" value={filter.condominio} onChange={e => setFilter(f => ({ ...f, condominio: e.target.value }))}>
          <option value="">Todos os condomínios</option>
          {condominios.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <select className="select w-48" value={filter.unidade} onChange={e => setFilter(f => ({ ...f, unidade: e.target.value }))}>
          <option value="">Todas as unidades</option>
          {unidades.map(u => <option key={u.id} value={u.id}>{u.numero}{u.bloco ? ` Bl.${u.bloco}` : ''}</option>)}
        </select>
        {(filter.condominio || filter.unidade) && (
          <button className="btn-ghost btn-sm" onClick={() => setFilter({ condominio: '', unidade: '' })}>Limpar</button>
        )}
        {cobrancas.length > 0 && (
          <div className="ml-auto text-sm text-red-600 font-medium">
            Total vencido: {formatCurrency(totalVencido)}
          </div>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse" />)}</div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Unidade</th><th>Competência</th><th>Vencimento</th><th>Valor</th><th>Multa</th><th>Juros</th><th>Total</th><th>Dias Atraso</th></tr>
            </thead>
            <tbody>
              {cobrancas.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center py-12">
                    <div className="flex flex-col items-center gap-2 text-slate-400">
                      <svg className="w-10 h-10 text-slate-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>
                      <span className="text-sm">Nenhuma cobrança vencida encontrada</span>
                    </div>
                  </td>
                </tr>
              )}
              {cobrancas.map(item => {
                const diasAtraso = item.data_vencimento
                  ? Math.max(0, Math.floor((Date.now() - new Date(item.data_vencimento)) / 86400000))
                  : 0
                const total = Number(item.valor) + Number(item.multa || 0) + Number(item.juros || 0)
                return (
                  <tr key={item.id} className="bg-red-50/30">
                    <td className="text-slate-400">{item.id}</td>
                    <td className="font-medium">{item.unidade_numero || item.unidade}</td>
                    <td>{formatCompetencia(item.competencia)}</td>
                    <td className="text-red-600 font-medium">{formatDate(item.data_vencimento)}</td>
                    <td>{formatCurrency(item.valor)}</td>
                    <td className="text-red-500">{formatCurrency(item.multa || 0)}</td>
                    <td className="text-red-500">{formatCurrency(item.juros || 0)}</td>
                    <td className="font-semibold text-red-700">{formatCurrency(total)}</td>
                    <td>
                      <span className={`badge ${diasAtraso > 30 ? 'bg-red-200 text-red-800' : 'bg-orange-100 text-orange-700'}`}>
                        {diasAtraso}d
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
