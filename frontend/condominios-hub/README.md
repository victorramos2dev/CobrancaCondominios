# CondoGest — Frontend

Frontend React + Vite + Tailwind CSS para o Sistema de Cobrança Condominial.

## Pré-requisitos

- Node.js 18+
- Backend Django rodando em `http://127.0.0.1:8000`

## Como rodar

```bash
# 1. Instale as dependências
npm install

# 2. Inicie em modo desenvolvimento
npm run dev
# → Acesse http://localhost:5173
```

> O Vite está configurado com proxy: qualquer requisição para `/api/*`
> é encaminhada automaticamente ao Django em `:8000`.

## Estrutura de pastas

```
src/
├── context/
│   └── AuthContext.jsx        # JWT: login, logout, refresh automático, role (isAdmin)
├── services/
│   ├── api.js                 # Instância Axios com Authorization header global
│   └── condominioService.js   # Todas as chamadas à API REST
├── components/
│   ├── layout/
│   │   └── AppLayout.jsx      # Sidebar + navegação principal
│   ├── shared/
│   │   └── ProtectedRoute.jsx # Guarda rotas — redireciona para /login se sem token
│   └── ui/
│       └── Modal.jsx          # Modal reutilizável (ESC fecha, clique fora fecha)
├── pages/
│   ├── LoginPage.jsx          # Tela de login com armazenamento JWT
│   ├── DashboardPage.jsx      # KPIs + gráfico adimplência + resumo por condomínio
│   ├── CondominiosPage.jsx    # CRUD de condomínios
│   ├── UnidadesPage.jsx       # CRUD de unidades + resumo financeiro individual
│   ├── CobrancasPage.jsx      # Listagem filtrada + dar baixa + CRUD
│   ├── InadimplenciaPage.jsx  # Cobranças VENCIDAS + resumo por condomínio
│   └── AcordosPage.jsx        # Criação de acordos + visualização de parcelas
├── utils/
│   └── format.js              # formatCurrency, formatDate, statusBadgeClass…
├── App.jsx                    # Roteamento com React Router DOM v6
└── index.css                  # Tailwind base + componentes utilitários
```

## Endpoints consumidos

| Endpoint                              | Usado em                    |
|---------------------------------------|-----------------------------|
| `POST /api/token/`                    | Login                       |
| `POST /api/token/refresh/`            | Refresh automático (401)    |
| `GET  /api/dashboard/`                | Dashboard                   |
| `GET  /api/inadimplencia/resumo/`     | Dashboard + Inadimplência   |
| `GET/POST/PATCH/DELETE /api/condominios/` | CondominiosPage         |
| `GET/POST/PATCH/DELETE /api/unidades/`    | UnidadesPage            |
| `GET /api/unidades/:id/resumo-financeiro/`| UnidadesPage (modal)    |
| `GET/POST/PATCH/DELETE /api/cobrancas/`   | CobrancasPage           |
| `GET/POST /api/acordos/`              | AcordosPage                 |
| `GET /api/parcelas-acordo/`           | AcordosPage (modal)         |

## Autenticação JWT

- O token `access` é salvo em `localStorage` na chave `access_token`.
- O token `refresh` é salvo em `localStorage` na chave `refresh_token`.
- Em todas as requisições autenticadas, o header `Authorization: Bearer <token>` é injetado globalmente via Axios.
- Ao receber um erro 401, o interceptor tenta renovar o token via `/api/token/refresh/` automaticamente. Se falhar, o usuário é redirecionado para o login.

## Níveis de acesso

O JWT inclui o campo `tipo` no payload (adicionado pelo `CustomTokenSerializer` do backend):

- `administrador` → pode criar, editar e excluir. Botões de ação ficam visíveis.
- `usuario` → somente visualização. Botões de edição/criação são ocultados pela UI.

## Build para produção

```bash
npm run build
# Arquivos gerados em /dist — sirva com Nginx ou similar
```
