import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { fetchCondominios, createCondominio, updateCondominio, deleteCondominio } from '../services/condominioService'
import Modal from '../components/ui/Modal'

const EMPTY = { nome: '', cnpj: '', endereco: '' }

export default function CondominiosPage() {
  const { isAdmin } = useAuth()
  const [items, setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal]   = useState(null)  // null | 'create' | {id, ...}
  const [form, setForm]     = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [err, setErr]       = useState('')

  const load = () => {
    setLoading(true)
    fetchCondominios()
      .then(d => setItems(Array.isArray(d) ? d : d.results ?? []))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  function openCreate() { setForm(EMPTY); setErr(''); setModal('create') }
  function openEdit(item) { setForm({ nome: item.nome, cnpj: item.cnpj || '', endereco: item.endereco || '' }); setErr(''); setModal(item) }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true); setErr('')
    try {
      if (modal === 'create') {
        await createCondominio(form)
      } else {
        await updateCondominio(modal.id, form)
      }
      setModal(null)
      load()
    } catch (e) {
      setErr(JSON.stringify(e.response?.data || 'Erro ao salvar'))
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Excluir este condomínio?')) return
    await deleteCondominio(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div>
          <h1 className="page-title">Condomínios</h1>
          <p className="text-sm text-slate-500 mt-0.5">Gerencie os empreendimentos cadastrados</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary">
            <PlusIcon /> Novo Condomínio
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse" />)}
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th><th>Nome</th><th>CNPJ</th><th>Endereço</th>
                {isAdmin && <th className="text-right">Ações</th>}
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && (
                <tr><td colSpan={5} className="text-center text-slate-400 py-8">Nenhum condomínio cadastrado</td></tr>
              )}
              {items.map(item => (
                <tr key={item.id}>
                  <td className="text-slate-400">{item.id}</td>
                  <td className="font-medium text-slate-800">{item.nome}</td>
                  <td>{item.cnpj || '—'}</td>
                  <td className="max-w-xs truncate text-slate-500">{item.endereco || '—'}</td>
                  {isAdmin && (
                    <td className="text-right">
                      <div className="flex justify-end gap-1">
                        <button onClick={() => openEdit(item)} className="btn-ghost btn-sm">Editar</button>
                        <button onClick={() => handleDelete(item.id)} className="btn-sm text-red-500 hover:bg-red-50">Excluir</button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title={modal === 'create' ? 'Novo Condomínio' : 'Editar Condomínio'} onClose={() => setModal(null)}>
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="label">Nome *</label>
              <input className="input" value={form.nome} onChange={e => setForm(f => ({ ...f, nome: e.target.value }))} required />
            </div>
            <div>
              <label className="label">CNPJ</label>
              <input className="input" value={form.cnpj} onChange={e => setForm(f => ({ ...f, cnpj: e.target.value }))} placeholder="00.000.000/0001-00" />
            </div>
            <div>
              <label className="label">Endereço</label>
              <input className="input" value={form.endereco} onChange={e => setForm(f => ({ ...f, endereco: e.target.value }))} />
            </div>
            {err && <p className="text-xs text-red-600 bg-red-50 rounded p-2">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setModal(null)} className="btn-secondary">Cancelar</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Salvando…' : 'Salvar'}</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

function PlusIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  )
}
