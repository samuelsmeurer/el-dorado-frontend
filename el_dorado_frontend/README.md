# El Dorado Influencer Management - Frontend

Frontend React para gerenciamento de influenciadores El Dorado.

## 🚀 Tecnologias

- **React 18** + **Vite**
- **Tailwind CSS** para styling
- **React Router** para navegação
- **Axios** para API calls
- **Lucide React** para ícones
- **React Hot Toast** para notificações

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

## 🏗️ Estrutura do Projeto

```
src/
├── components/          # Componentes reutilizáveis
│   ├── Navbar.jsx
│   ├── StatsCard.jsx
│   └── InfluencerModal.jsx
├── pages/              # Páginas principais
│   ├── Dashboard.jsx
│   ├── Influencers.jsx
│   └── Analytics.jsx
├── services/           # Integração com API
│   └── api.js
├── App.jsx            # Componente principal
├── main.jsx           # Entry point
└── index.css          # Estilos globais
```

## 🔗 API Integration

O frontend se conecta com a API FastAPI em:
`https://web-production-b9838.up.railway.app/api/v1`

## 🎨 Funcionalidades

- ✅ **Dashboard** com estatísticas
- ✅ **CRUD de Influencers** completo
- ✅ **Busca e filtros**
- ✅ **Interface responsiva**
- ✅ **Notificações toast**
- 🔄 **Analytics** (em desenvolvimento)

## 🚀 Deploy

Recomendado para deploy:
- **Vercel** (automático com GitHub)
- **Netlify**
- **Railway** (caso prefira)

```bash
# Build
npm run build

# Pasta dist/ estará pronta para deploy
```

## 🔧 Configuração

Para alterar a URL da API, edite:
`src/services/api.js`

```javascript
const API_BASE_URL = 'sua-api-url-aqui'
```