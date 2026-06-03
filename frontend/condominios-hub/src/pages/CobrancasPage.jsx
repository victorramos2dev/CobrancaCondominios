import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import {
  fetchCobrancas, createCobranca, updateCobranca, deleteCobranca,
  fetchUnidades, fetchCondominios,
} from '../services/condominioService'
import Modal from '../components/ui/Modal'
import { formatCurrency, formatDate, formatCompetencia, statusBadgeClass, statusLabel, today } from '../utils/format'

const EMPTY_FORM = {
  unidade: '', competencia: '', data_vencimento: '', valor: '', status: 'PENDENTE',
  data_pagamento: '', forma_pagamento: '', multa: '0', juros: '0',
}

export default function CobrancasPage() {
  const { isAdmin } = useAuth()
  const [items, setItems]       = useState([])
  const [unidades, setUnidades] = useState([])
  const [condominios, setCondominios] = useState([])
  const [loading, setLoading]   = useState(true)
  const [filter, setFilter]     = useState({ unidade: '', status: '', competencia: '', condominio: '' })
  const [modal, setModal]       = useState(null)
  const [baixaModal, setBaixaModal] = useState(null)
  const [form, setForm]         = useState(EMPTY_FORM)
  const [baixaForm, setBaixaForm] = useState({ data_pagamento: today(), forma_pagamento: 'PIX' })
  const [saving, setSaving]     = useState(false)
  const [err, setErr]           = useState('')

  const load = () => {
    setLoading(true)
    const params = {}
    if (filter.unidade)    params.unidade    = filter.unidade
    if (filter.status)     params.status     = filter.status
    if (filter.competencia) params.competencia = filter.competencia
    if (filter.condominio) params.condominio = filter.condominio
    fetchCobrancas(params)
      .then(d => setItems(Array.isArray(d) ? d : d.results ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchUnidades().then(d => setUnidades(Array.isArray(d) ? d : d.results ?? []))
    fetchCondominios().then(d => setCondominios(Array.isArray(d) ? d : d.results ?? []))
  }, [])
  useEffect(() => { load() }, [filter])

  function openCreate() { setForm(EMPTY_FORM); setErr(''); setModal('create') }
  function openEdit(item) {
    setForm({
      unidade: item.unidade, competencia: item.competencia, data_vencimento: item.data_vencimento,
      valor: item.valor, status: item.status, data_pagamento: item.data_pagamento || '',
      forma_pagamento: item.forma_pagamento || '', multa: item.multa || '0', juros: item.juros || '0',
    })
    setErr(''); setModal(item)
  }

  async function handleSave(e) {
    e.preventDefault(); setSaving(true); setErr('')
    const payload = { ...form }
    if (payload.status !== 'PAGO') { payload.data_pagamento = null; payload.forma_pagamento = '' }
    try {
      if (modal === 'create') await createCobranca(payload)
      else await updateCobranca(modal.id, payload)
      setModal(null); load()
    } catch (e) {
      setErr(JSON.stringify(e.response?.data || 'Erro'))
    } finally { setSaving(false) }
  }

  async function handleBaixa(e) {
    e.preventDefault(); setSaving(true); setErr('')
    try {
      await updateCobranca(baixaModal.id, { status: 'PAGO', ...baixaForm })
      setBaixaModal(null); load()
    } catch (e) {
      setErr(JSON.stringify(e.response?.data || 'Erro'))
    } finally { setSaving(false) }
  }

  async function handleDelete(id) {
    if (!confirm('Excluir esta cobrança?')) return
    await deleteCobranca(id); load()
  }

  const isRowOverdue = (item) => item.status === 'VENCIDO'

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Cobranças</h1>
          <p className="text-sm text-slate-500 mt-0.5">Emissão e acompanhamento de receitas condominiais</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Nova Cobrança
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select className="select w-48" value={filter.condominio} onChange={e => setFilter(f => ({ ...f, condominio: e.target.value }))}>
          <option value="">Todos os condomínios</option>
          {condominios.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <select className="select w-48" value={filter.unidade} onChange={e => setFilter(f => ({ ...f, unidade: e.target.value }))}>
          <option value="">Todas as unidades</option>
          {unidades.map(u => <option key={u.id} value={u.id}>{u.numero}{u.bloco ? ` - Bloco ${u.bloco}` : ''}</option>)}
        </select>
        <select className="select w-36" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
          <option value="">Todos status</option>
          {['PENDENTE','PAGO','VENCIDO','CANCELADO'].map(s => <option key={s} value={s}>{statusLabel(s)}</option>)}
        </select>
        <input
          type="month" className="input w-40"
          value={filter.competencia ? filter.competencia.slice(0, 7) : ''}
          onChange={e => setFilter(f => ({ ...f, competencia: e.target.value ? e.target.value + '-01' : '' }))}
        />
        {Object.values(filter).some(Boolean) && (
          <button className="btn-ghost btn-sm" onClick={() => setFilter({ unidade:'', status:'', competencia:'', condominio:'' })}>
            Limpar filtros
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(6)].map((_, i) => <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse"/>)}</div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Unidade</th><th>Competência</th><th>Vencimento</th><th>Valor</th><th>Multa+Juros</th><th>Status</th><th>Pagamento</th><th className="text-right">Ações</th></tr>
            </thead>
            <tbody>
              {items.length === 0 && <tr><td colSpan={9} className="text-center text-slate-400 py-8">Nenhuma cobrança encontrada</td></tr>}
              {items.map(item => (
                <tr key={item.id} className={isRowOverdue(item) ? 'bg-red-50/50' : ''}>
                  <td className="text-slate-400">{item.id}</td>
                  <td className="font-medium">{item.unidade_numero || item.unidade}</td>
                  <td>{formatCompetencia(item.competencia)}</td>
                  <td className={isRowOverdue(item) ? 'text-red-600 font-medium' : ''}>{formatDate(item.data_vencimento)}</td>
                  <td className="font-medium">{formatCurrency(item.valor)}</td>
                  <td className={Number(item.multa) + Number(item.juros) > 0 ? 'text-red-500 text-xs' : 'text-slate-300 text-xs'}>
                    {Number(item.multa) + Number(item.juros) > 0
                      ? `+${formatCurrency(Number(item.multa) + Number(item.juros))}`
                      : '—'}
                  </td>
                  <td><span className={statusBadgeClass(item.status)}>{statusLabel(item.status)}</span></td>
                  <td className="text-slate-500 text-xs">
                    {item.data_pagamento ? `${formatDate(item.data_pagamento)} · ${item.forma_pagamento || ''}` : '—'}
                  </td>
                  <td className="text-right">
                    <div className="flex justify-end gap-1">
                      {isAdmin && item.status !== 'PAGO' && item.status !== 'CANCELADO' && (
                        <button
                          onClick={() => { setBaixaForm({ data_pagamento: today(), forma_pagamento: 'PIX' }); setErr(''); setBaixaModal(item) }}
                          className="btn-sm bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200"
                        >
                          Dar Baixa
                        </button>
                      )}
                      {isAdmin && <button onClick={() => openEdit(item)} className="btn-ghost btn-sm">Editar</button>}
                      {isAdmin && <button onClick={() => handleDelete(item.id)} className="btn-sm text-red-500 hover:bg-red-50">×</button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create/Edit Modal */}
      {modal && modal !== 'baixa' && (
        <Modal title={modal === 'create' ? 'Nova Cobrança' : 'Editar Cobrança'} onClose={() => setModal(null)} size="lg">
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Unidade *</label>
                <select className="select" value={form.unidade} onChange={e => setForm(f => ({ ...f, unidade: e.target.value }))} required>
                  <option value="">Selecione…</option>
                  {unidades.map(u => <option key={u.id} value={u.id}>{u.numero}{u.bloco ? ` Bl.${u.bloco}` : ''}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Valor (R$) *</label>
                <input type="number" step="0.01" min="0" className="input" value={form.valor} onChange={e => setForm(f => ({ ...f, valor: e.target.value }))} required />
              </div>
              <div>
                <label className="label">Competência *</label>
                <input type="date" className="input" value={form.competencia} onChange={e => setForm(f => ({ ...f, competencia: e.target.value }))} required />
              </div>
              <div>
                <label className="label">Data de Vencimento *</label>
                <input type="date" className="input" value={form.data_vencimento} onChange={e => setForm(f => ({ ...f, data_vencimento: e.target.value }))} required />
              </div>
              <div>
                <label className="label">Status</label>
                <select className="select" value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                  {['PENDENTE','PAGO','VENCIDO','CANCELADO'].map(s => <option key={s} value={s}>{statusLabel(s)}</option>)}
                </select>
              </div>
              {form.status === 'PAGO' && (
                <div>
                  <label className="label">Forma de Pagamento</label>
                  <select className="select" value={form.forma_pagamento} onChange={e => setForm(f => ({ ...f, forma_pagamento: e.target.value }))}>
                    <option value="PIX">Pix</option>
                    <option value="BOLETO">Boleto</option>
                    <option value="CARTAO">Cartão</option>
                  </select>
                </div>
              )}
            </div>
            {form.status === 'PAGO' && (
              <div>
                <label className="label">Data de Pagamento *</label>
                <input type="date" className="input" value={form.data_pagamento} onChange={e => setForm(f => ({ ...f, data_pagamento: e.target.value }))} required />
              </div>
            )}
            {err && <p className="text-xs text-red-600 bg-red-50 rounded p-2">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setModal(null)} className="btn-secondary">Cancelar</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Salvando…' : 'Salvar'}</button>
            </div>
          </form>
        </Modal>
      )}

      {/* Baixa Modal */}
      {baixaModal && (
        <Modal title={`Dar Baixa — Cobrança #${baixaModal.id}`} onClose={() => setBaixaModal(null)} size="sm">
          <div className="mb-4 p-3 bg-slate-50 rounded-lg text-sm space-y-1">
            <div className="flex justify-between"><span className="text-slate-500">Valor base</span><span className="font-medium">{formatCurrency(baixaModal.valor)}</span></div>
            {Number(baixaModal.multa) > 0 && <div className="flex justify-between text-red-600"><span>Multa</span><span>{formatCurrency(baixaModal.multa)}</span></div>}
            {Number(baixaModal.juros) > 0 && <div className="flex justify-between text-red-600"><span>Juros</span><span>{formatCurrency(baixaModal.juros)}</span></div>}
          </div>
          <form onSubmit={handleBaixa} className="space-y-4">
            <div>
              <label className="label">Data de Pagamento *</label>
              <input type="date" className="input" value={baixaForm.data_pagamento} onChange={e => setBaixaForm(f => ({ ...f, data_pagamento: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Forma de Pagamento</label>
              <select className="select" value={baixaForm.forma_pagamento} onChange={e => setBaixaForm(f => ({ ...f, forma_pagamento: e.target.value }))}>
                <option value="PIX">Pix</option>
                <option value="BOLETO">Boleto</option>
                <option value="CARTAO">Cartão</option>
              </select>
            </div>
            {err && <p className="text-xs text-red-600 bg-red-50 rounded p-2">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setBaixaModal(null)} className="btn-secondary">Cancelar</button>
              <button type="submit" className="btn-primary bg-emerald-600 hover:bg-emerald-700" disabled={saving}>
                {saving ? 'Registrando…' : 'Confirmar Pagamento'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
