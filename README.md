# 🚀 El Dorado Influencer API

Sistema completo de gerenciamento de vídeos patrocinados de influenciadores da El Dorado, com integração automatizada ao TikTok via RapidAPI ScrapTik.

## 📋 Visão Geral

Esta API permite:
- ✅ **Cadastro de influenciadores** pela equipe de recrutamento
- ✅ **Sincronização automática** de IDs do TikTok
- ✅ **Coleta seletiva** de vídeos com menção `@El Dorado P2P`
- ✅ **Analytics avançados** com rankings e métricas
- ✅ **Controle de duplicação** (UPDATE vs INSERT)

## 🏗️ Arquitetura

```
├── app/
│   ├── core/           # Configuração e database
│   ├── models/         # SQLAlchemy models (3 tabelas)
│   ├── routes/         # FastAPI endpoints
│   ├── services/       # ScrapTik API integration
│   └── schemas.py      # Pydantic schemas
├── alembic/           # Database migrations
└── tests/             # Unit tests
```

## 🗄️ Estrutura do Banco

### 3 Tabelas Especializadas:

1. **`influencers`** - Dados pessoais e empresariais
2. **`influencer_ids`** - IDs das plataformas sociais  
3. **`tiktok_videos`** - Apenas vídeos patrocinados (@El Dorado P2P)

## 🚀 Instalação e Setup

### 1. Instalar Dependências
```bash
cd el_dorado_api
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Setup PostgreSQL no Railway
1. Criar projeto no Railway
2. Adicionar PostgreSQL addon
3. Copiar DATABASE_URL para .env

### 4. Executar Migrações
```bash
alembic upgrade head
```

### 5. Iniciar API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 Endpoints Principais

### Influenciadores
```http
GET    /api/v1/influencers/                    # Listar todos
POST   /api/v1/influencers/                    # Cadastrar novo
GET    /api/v1/influencers/{eldorado_username} # Buscar específico
POST   /api/v1/influencers/{eldorado_username}/sync-tiktok-id # Sincronizar ID
```

### Vídeos Patrocinados
```http
GET    /api/v1/videos/                         # Listar vídeos
POST   /api/v1/videos/sync/{eldorado_username} # Sync individual
POST   /api/v1/videos/sync/all                 # Sync todos
```

### Analytics
```http
GET    /api/v1/analytics/dashboard             # Dashboard geral
GET    /api/v1/analytics/top-videos/likes      # Top 10 por likes
GET    /api/v1/analytics/influencer/{username} # Stats por influencer
GET    /api/v1/analytics/monthly-summary       # Resumo mensal
```

## 🔧 Configuração das APIs

### RapidAPI ScrapTik
Adicione no `.env`:
```env
RAPIDAPI_KEY=sua_chave_rapidapi
RAPIDAPI_HOST=scraptik.p.rapidapi.com
```

### PostgreSQL Railway
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
```

## 📊 Fluxo de Uso

### 1. Cadastrar Influenciador
```bash
curl -X POST "http://localhost:8000/api/v1/influencers/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "João Silva",
    "eldorado_username": "joao_eldorado", 
    "phone": "+5511999999999",
    "country": "Brazil",
    "owner": "users",
    "tiktok_username": "joaosilva"
  }'
```

### 2. Sincronizar ID TikTok
```bash
curl -X POST "http://localhost:8000/api/v1/influencers/joao_eldorado/sync-tiktok-id"
```

### 3. Buscar Vídeos Patrocinados
```bash
curl -X POST "http://localhost:8000/api/v1/videos/sync/joao_eldorado"
```

### 4. Ver Analytics
```bash
curl "http://localhost:8000/api/v1/analytics/dashboard"
curl "http://localhost:8000/api/v1/analytics/top-videos/likes"
```

## 🎯 Lógica de Negócio

### Filtro de Vídeos
- ✅ Busca apenas vídeos com menção `@El Dorado P2P`
- ✅ Ignora vídeos não patrocinados
- ✅ Controla duplicação via `tiktok_video_id`
- ✅ UPDATE métricas se existe, INSERT se novo

### Métricas Importantes
- **Views, Likes, Comments, Shares**
- **Engagement Rate** = (Likes + Comments + Shares) / Views * 100
- **Rankings** por performance
- **Análises temporais** por mês/período

## 📈 Deploy no Railway

1. **Push para GitHub**
2. **Conectar no Railway**
3. **Adicionar PostgreSQL service**
4. **Configurar variáveis de ambiente**
5. **Deploy automático**

### Variáveis Railway:
```
DATABASE_URL=<gerado_automaticamente>
RAPIDAPI_KEY=sua_chave
SECRET_KEY=chave_secreta_qualquer
```

## 🧪 Testando a API

```bash
# Health check
curl http://localhost:8000/health

# Documentação interativa
# Acesse: http://localhost:8000/docs
```

## 🔄 Próximos Passos

- [ ] Implementar Celery para sync automático
- [ ] Adicionar autenticação JWT
- [ ] Dashboard frontend React
- [ ] Suporte Instagram/Facebook
- [ ] Notificações vídeos virais

## 📞 Suporte

- **Documentação**: `/docs` (Swagger UI)
- **Health Check**: `/health`
- **Logs**: Verificar console da aplicação