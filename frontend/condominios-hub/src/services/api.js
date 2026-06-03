import axios from 'axios'

const api = axios.create({
  baseURL: '/',          // Vite proxies /api → Django on :8000
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

export default api
