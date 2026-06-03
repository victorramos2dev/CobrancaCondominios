// ─── Formatting ───────────────────────────────────────────────────────────────
export const formatCurrency = (v) =>
  Number(v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export const formatDate = (d) => {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}

export const formatCompetencia = (d) => {
  if (!d) return '—'
  const [y, m] = d.split('-')
  const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
  return `${months[parseInt(m, 10) - 1]}/${y}`
}

// ─── Status helpers ───────────────────────────────────────────────────────────
export const statusBadgeClass = (status) => ({
  PENDENTE:   'badge-pendente',
  PAGO:       'badge-pago',
  VENCIDO:    'badge-vencido',
  CANCELADO:  'badge-cancelado',
}[status] ?? 'badge')

export const statusLabel = (status) => ({
  PENDENTE:  'Pendente',
  PAGO:      'Pago',
  VENCIDO:   'Vencido',
  CANCELADO: 'Cancelado',
}[status] ?? status)

// ─── Date helpers ─────────────────────────────────────────────────────────────
export const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date(new Date().toDateString())
}

export const today = () => new Date().toISOString().split('T')[0]
