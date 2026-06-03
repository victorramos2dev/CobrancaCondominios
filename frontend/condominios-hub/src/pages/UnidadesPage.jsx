import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { fetchUnidades, createUnidade, updateUnidade, deleteUnidade, fetchCondominios, fetchUnidadeResumo } from '../services/condominioService'
import Modal from '../components/ui/Modal'
import { formatCurrency } from '../utils/format'

const EMPTY = { numero: '', bloco: '', responsavel: '', status_unidade: 'OCUPADO', condominio: '' }

export default function UnidadesPage() {
  const { isAdmin } = useAuth()
  const [items, setItems]       = useState([])
  const [condominios, setCondominios] = useState([])
  const [loading, setLoading]   = useState(true)
  const [filter, setFilter]     = useState({ condominio: '' })
  const [modal, setModal]       = useState(null)
  const [form, setForm]         = useState(EMPTY)
  const [saving, setSaving]     = useState(false)
  const [resumo, setResumo]     = useState(null)
  const [err, setErr]           = useState('')

  const load = () => {
    setLoading(true)
    const params = {}
    if (filter.condominio) params.condominio = filter.condominio
    fetchUnidades(params)
      .then(d => setItems(Array.isArray(d) ? d : d.results ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchCondominios().then(d => setCondominios(Array.isArray(d) ? d : d.results ?? []))
  }, [])
  useEffect(() => { load() }, [filter])

  function openCreate() { setForm(EMPTY); setErr(''); setModal('create'); setResumo(null) }
  function openEdit(item) {
    setForm({ numero: item.numero, bloco: item.bloco || '', responsavel: item.responsavel || '', status_unidade: item.status_unidade, condominio: item.condominio })
    setErr(''); setModal(item); setResumo(null)
  }
  async function openResumo(item) {
    const r = await fetchUnidadeResumo(item.id)
    setResumo(r); setModal('resumo')
  }

  async function handleSave(e) {
    e.preventDefault(); setSaving(true); setErr('')
    try {
      if (modal === 'create') await createUnidade(form)
      else await updateUnidade(modal.id, form)
      setModal(null); load()
    } catch (e) {
      setErr(JSON.stringify(e.response?.data || 'Erro'))
    } finally { setSaving(false) }
  }

  async function handleDelete(id) {
    if (!confirm('Excluir esta unidade?')) return
    await deleteUnidade(id); load()
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Unidades</h1>
          <p className="text-sm text-slate-500 mt-0.5">Apartamentos e unidades por condomínio</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Nova Unidade
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <select className="select w-52" value={filter.condominio} onChange={e => setFilter(f => ({ ...f, condominio: e.target.value }))}>
          <option value="">Todos os condomínios</option>
          {condominios.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse" />)}</div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Número</th><th>Bloco</th><th>Responsável</th><th>Condomínio</th><th>Status</th><th className="text-right">Ações</th></tr>
            </thead>
            <tbody>
              {items.length === 0 && <tr><td colSpan={7} className="text-center text-slate-400 py-8">Nenhuma unidade encontrada</td></tr>}
              {items.map(item => (
                <tr key={item.id}>
                  <td className="text-slate-400">{item.id}</td>
                  <td className="font-medium">{item.numero}</td>
                  <td>{item.bloco || '—'}</td>
                  <td>{item.responsavel || '—'}</td>
                  <td className="text-slate-500">{item.condominio_nome || item.condominio}</td>
                  <td>
                    <span className={item.status_unidade === 'OCUPADO' ? 'badge-ocupado' : 'badge-vago'}>
                      {item.status_unidade}
                    </span>
                  </td>
                  <td className="text-right">
                    <div className="flex justify-end gap-1">
                      <button onClick={() => openResumo(item)} className="btn-ghost btn-sm">Resumo</button>
                      {isAdmin && <>
                        <button onClick={() => openEdit(item)} className="btn-ghost btn-sm">Editar</button>
                        <button onClick={() => handleDelete(item.id)} className="btn-sm text-red-500 hover:bg-red-50">Excluir</button>
                      </>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create / Edit Modal */}
      {modal && modal !== 'resumo' && (
        <Modal title={modal === 'create' ? 'Nova Unidade' : 'Editar Unidade'} onClose={() => setModal(null)}>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Número *</label>
                <input className="input" value={form.numero} onChange={e => setForm(f => ({ ...f, numero: e.target.value }))} required />
              </div>
              <div>
                <label className="label">Bloco</label>
                <input className="input" value={form.bloco} onChange={e => setForm(f => ({ ...f, bloco: e.target.value }))} />
              </div>
            </div>
            <div>
              <label className="label">Responsável / Morador</label>
              <input className="input" value={form.responsavel} onChange={e => setForm(f => ({ ...f, responsavel: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Status</label>
                <select className="select" value={form.status_unidade} onChange={e => setForm(f => ({ ...f, status_unidade: e.target.value }))}>
                  <option value="OCUPADO">Ocupado</option>
                  <option value="VAGO">Vago</option>
                </select>
              </div>
              <div>
                <label className="label">Condomínio *</label>
                <select className="select" value={form.condominio} onChange={e => setForm(f => ({ ...f, condominio: e.target.value }))} required>
                  <option value="">Selecione…</option>
                  {condominios.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                </select>
              </div>
            </div>
            {err && <p className="text-xs text-red-600 bg-red-50 rounded p-2">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setModal(null)} className="btn-secondary">Cancelar</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Salvando…' : 'Salvar'}</button>
            </div>
          </form>
        </Modal>
      )}

      {/* Resumo financeiro modal */}
      {modal === 'resumo' && resumo && (
        <Modal title={`Resumo Financeiro — Unidade ${resumo.unidade}`} onClose={() => setModal(null)}>
          <div className="space-y-4">
            <p className="text-sm text-slate-600">Responsável: <strong>{resumo.responsavel}</strong></p>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Total', value: resumo.total_cobrancas, cls: '' },
                { label: 'Pagas', value: resumo.total_pagas, cls: 'text-emerald-600' },
                { label: 'Vencidas', value: resumo.total_vencidas, cls: 'text-red-600' },
              ].map(({ label, value, cls }) => (
                <div key={label} className="card p-3 text-center">
                  <p className={`text-2xl font-serif ${cls}`}>{value}</p>
                  <p className="text-xs text-slate-500">{label}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
              <span className="text-sm text-amber-700 font-medium">Valor em Aberto</span>
              <span className="text-lg font-serif text-amber-700">{formatCurrency(resumo.valor_em_aberto)}</span>
            </div>
            {resumo.possui_acordo && (
              <div className="text-xs bg-brand-50 text-brand-700 border border-brand-200 rounded-lg px-3 py-2">
                Esta unidade possui acordo de parcelamento ativo.
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
