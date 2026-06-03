import api from './api'

// ─── Dashboard ────────────────────────────────────────────────────────────────
export const fetchDashboard = () => api.get('/api/dashboard/').then(r => r.data)
export const fetchInadimplenciaResumo = () => api.get('/api/inadimplencia/resumo/').then(r => r.data)

// ─── Condomínios ──────────────────────────────────────────────────────────────
export const fetchCondominios = (params) => api.get('/api/condominios/', { params }).then(r => r.data)
export const createCondominio = (data) => api.post('/api/condominios/', data).then(r => r.data)
export const updateCondominio = (id, data) => api.patch(`/api/condominios/${id}/`, data).then(r => r.data)
export const deleteCondominio = (id) => api.delete(`/api/condominios/${id}/`)

// ─── Unidades ─────────────────────────────────────────────────────────────────
export const fetchUnidades = (params) => api.get('/api/unidades/', { params }).then(r => r.data)
export const createUnidade = (data) => api.post('/api/unidades/', data).then(r => r.data)
export const updateUnidade = (id, data) => api.patch(`/api/unidades/${id}/`, data).then(r => r.data)
export const deleteUnidade = (id) => api.delete(`/api/unidades/${id}/`)
export const fetchUnidadeResumo = (id) => api.get(`/api/unidades/${id}/resumo-financeiro/`).then(r => r.data)

// ─── Cobranças ────────────────────────────────────────────────────────────────
export const fetchCobrancas = (params) => api.get('/api/cobrancas/', { params }).then(r => r.data)
export const createCobranca = (data) => api.post('/api/cobrancas/', data).then(r => r.data)
export const updateCobranca = (id, data) => api.patch(`/api/cobrancas/${id}/`, data).then(r => r.data)
export const deleteCobranca = (id) => api.delete(`/api/cobrancas/${id}/`)

// ─── Acordos ──────────────────────────────────────────────────────────────────
export const fetchAcordos = (params) => api.get('/api/acordos/', { params }).then(r => r.data)
export const createAcordo = (data) => api.post('/api/acordos/', data).then(r => r.data)
export const fetchParcelasByAcordo = (acordoId) =>
  api.get('/api/parcelas-acordo/', { params: { acordo: acordoId } }).then(r => r.data)

// ─── Usuários ─────────────────────────────────────────────────────────────────
export const fetchUsuarios = () => api.get('/api/usuarios/').then(r => r.data)
