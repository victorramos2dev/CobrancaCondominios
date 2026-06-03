import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { fetchAcordos, createAcordo, fetchParcelasByAcordo, fetchCobrancas, fetchUnidades } from '../services/condominioService'
import Modal from '../components/ui/Modal'
import { formatCurrency, formatDate } from '../utils/format'

export default function AcordosPage() {
  const { isAdmin } = useAuth()
  const [acordos, setAcordos]   = useState([])
  const [unidades, setUnidades] = useState([])
  const [loading, setLoading]   = useState(true)
  const [filter, setFilter]     = useState({ unidade: '' })
  const [modal, setModal]       = useState(null)   // null | 'create' | 'parcelas'
  const [parcelas, setParcelas] = useState([])
  const [cobrancasVencidas, setCobrancasVencidas] = useState([])
  const [form, setForm]         = useState({ unidade: '', cobrancas: [], qtd_parcelas: 3 })
  const [saving, setSaving]     = useState(false)
  const [err, setErr]           = useState('')

  const load = () => {
    setLoading(true)
    const params = {}
    if (filter.unidade) params.unidade = filter.unidade
    fetchAcordos(params)
      .then(d => setAcordos(Array.isArray(d) ? d : d.results ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchUnidades().then(d => setUnidades(Array.isArray(d) ? d : d.results ?? [])) }, [])
  useEffect(() => { load() }, [filter])

  async function openCreate() {
    setForm({ unidade: '', cobrancas: [], qtd_parcelas: 3 })
    setCobrancasVencidas([])
    setErr('')
    setModal('create')
  }

  async function loadCobrancasVencidas(unidadeId) {
    if (!unidadeId) { setCobrancasVencidas([]); return }
    const d = await fetchCobrancas({ unidade: unidadeId, status: 'VENCIDO' })
    setCobrancasVencidas(Array.isArray(d) ? d : d.results ?? [])
  }

  function toggleCobranca(id) {
    setForm(f => ({
      ...f,
      cobrancas: f.cobrancas.includes(id) ? f.cobrancas.filter(c => c !== id) : [...f.cobrancas, id]
    }))
  }

  async function handleSave(e) {
    e.preventDefault(); setSaving(true); setErr('')
    try {
      await createAcordo({ unidade: form.unidade, cobrancas: form.cobrancas, qtd_parcelas: Number(form.qtd_parcelas) })
      setModal(null); load()
    } catch (e) {
      setErr(JSON.stringify(e.response?.data || 'Erro ao criar acordo'))
    } finally { setSaving(false) }
  }

  async function openParcelas(acordo) {
    const p = await fetchParcelasByAcordo(acordo.id)
    setParcelas(Array.isArray(p) ? p : p.results ?? [])
    setModal({ type: 'parcelas', acordo })
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Acordos de Parcelamento</h1>
          <p className="text-sm text-slate-500 mt-0.5">Negociação de cobranças vencidas em parcelas</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Novo Acordo
          </button>
        )}
      </div>

      {/* Filter */}
      <div className="flex gap-3">
        <select className="select w-52" value={filter.unidade} onChange={e => setFilter(f => ({ ...f, unidade: e.target.value }))}>
          <option value="">Todas as unidades</option>
          {unidades.map(u => <option key={u.id} value={u.id}>{u.numero}{u.bloco ? ` Bl.${u.bloco}` : ''}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(4)].map((_, i) => <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse"/>)}</div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Unidade</th><th>Qtd Parcelas</th><th>Criado em</th><th>Status</th><th className="text-right">Ações</th></tr>
            </thead>
            <tbody>
              {acordos.length === 0 && <tr><td colSpan={6} className="text-center text-slate-400 py-8">Nenhum acordo encontrado</td></tr>}
              {acordos.map(item => (
                <tr key={item.id}>
                  <td className="text-slate-400">{item.id}</td>
                  <td className="font-medium">{item.unidade_numero || item.unidade}</td>
                  <td>{item.qtd_parcelas || item.parcelas_count || '—'}</td>
                  <td>{formatDate(item.criado_em?.split('T')[0])}</td>
                  <td>
                    <span className={`badge ${item.status === 'ATIVO' ? 'badge-ocupado' : 'badge-vago'}`}>
                      {item.status || 'ATIVO'}
                    </span>
                  </td>
                  <td className="text-right">
                    <button onClick={() => openParcelas(item)} className="btn-ghost btn-sm">Ver Parcelas</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {modal === 'create' && (
        <Modal title="Novo Acordo de Parcelamento" onClose={() => setModal(null)} size="lg">
          <form onSubmit={handleSave} className="space-y-5">
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="label">Unidade *</label>
                <select
                  className="select"
                  value={form.unidade}
                  onChange={e => {
                    setForm(f => ({ ...f, unidade: e.target.value, cobrancas: [] }))
                    loadCobrancasVencidas(e.target.value)
                  }}
                  required
                >
                  <option value="">Selecione uma unidade…</option>
                  {unidades.map(u => <option key={u.id} value={u.id}>{u.numero}{u.bloco ? ` Bl.${u.bloco}` : ''} — {u.responsavel}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Quantidade de Parcelas *</label>
                <input type="number" min="1" max="24" className="input" value={form.qtd_parcelas} onChange={e => setForm(f => ({ ...f, qtd_parcelas: e.target.value }))} required />
              </div>
            </div>

            {form.unidade && (
              <div>
                <label className="label">Cobranças Vencidas *</label>
                {cobrancasVencidas.length === 0 ? (
                  <p className="text-sm text-slate-400 py-3 text-center border rounded-lg">Nenhuma cobrança vencida para esta unidade</p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto border rounded-xl p-2 bg-slate-50">
                    {cobrancasVencidas.map(c => (
                      <label key={c.id} className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${form.cobrancas.includes(c.id) ? 'bg-brand-50 border border-brand-200' : 'bg-white border border-slate-200 hover:bg-slate-100'}`}>
                        <input
                          type="checkbox"
                          checked={form.cobrancas.includes(c.id)}
                          onChange={() => toggleCobranca(c.id)}
                          className="accent-brand-600"
                        />
                        <div className="flex-1 text-sm">
                          <span className="font-medium">#{c.id}</span>
                          <span className="text-slate-500 ml-2">Venc. {formatDate(c.data_vencimento)}</span>
                        </div>
                        <span className="font-medium text-red-600">{formatCurrency(Number(c.valor) + Number(c.multa || 0) + Number(c.juros || 0))}</span>
                      </label>
                    ))}
                  </div>
                )}
                {form.cobrancas.length > 0 && (
                  <p className="text-xs text-slate-500 mt-1">{form.cobrancas.length} cobrança(s) selecionada(s)</p>
                )}
              </div>
            )}

            {err && <p className="text-xs text-red-600 bg-red-50 rounded p-2">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setModal(null)} className="btn-secondary">Cancelar</button>
              <button type="submit" className="btn-primary" disabled={saving || form.cobrancas.length === 0}>
                {saving ? 'Criando…' : 'Criar Acordo'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Parcelas Modal */}
      {modal?.type === 'parcelas' && (
        <Modal title={`Parcelas — Acordo #${modal.acordo.id}`} onClose={() => setModal(null)} size="md">
          <div className="space-y-2">
            {parcelas.length === 0 && <p className="text-sm text-slate-400 text-center py-4">Nenhuma parcela encontrada</p>}
            {parcelas.map((p, i) => (
              <div key={p.id} className="flex items-center justify-between px-4 py-3 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 flex items-center justify-center rounded-full bg-brand-100 text-brand-700 text-xs font-bold">{i + 1}</span>
                  <span className="text-sm text-slate-600">{formatDate(p.data_vencimento)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-medium">{formatCurrency(p.valor)}</span>
                  <span className={`badge ${p.pago ? 'badge-pago' : 'badge-pendente'}`}>{p.pago ? 'Pago' : 'Pendente'}</span>
                </div>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </div>
  )
}
