# El Dorado - Sistema de Gerenciamento de Vídeos de Influenciadores

Sistema completo para gerenciar e monitorar vídeos postados por influenciadores na El Dorado, incluindo contagem automática, métricas e relatórios.

## 📋 Visão Geral

Este sistema permite:
- Monitoramento automático de vídeos de influenciadores
- Contagem e análise de métricas de engagement
- Gerenciamento de campanhas e parcerias
- Relatórios detalhados de performance
- API para integração com outros sistemas

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   Dashboard     │◄──►│   (FastAPI)     │◄──►│   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   TikTok API    │              │
                        │   Integration   │              │
                        └─────────────────┘              │
                                 │                       │
                        ┌─────────────────┐              │
                        │   Scheduler     │──────────────┘
                        │   (Celery)      │
                        └─────────────────┘
```

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.9+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para interação com banco de dados
- **Alembic** - Migração de banco de dados
- **Celery** - Processamento assíncrono e agendamento
- **Redis** - Cache e message broker
- **Pydantic** - Validação de dados

### Database
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões

### Frontend (Opcional)
- **React/Next.js** - Interface web
- **TailwindCSS** - Estilização
- **Chart.js** - Gráficos e métricas

### Integração
- **RapidAPI ScrapTik** - Coleta de dados do TikTok
  - Username to ID conversion
  - User posts (últimos 20 vídeos)
- **Instagram API** - Suporte para Instagram (futuro)
- **Facebook API** - Suporte para Facebook (futuro)
- **X (Twitter) API** - Suporte para X (futuro)

## 📊 Estrutura do Banco de Dados

### Arquitetura de 3 Bancos Especializados

O sistema utiliza uma arquitetura com 3 tabelas principais, cada uma com responsabilidade específica:

#### 1. Tabela `influencers` - Dados Pessoais e Empresariais

```sql
-- Dados básicos dos influenciadores cadastrados pela equipe de recrutamento
CREATE TABLE influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(255) NOT NULL,
    eldorado_username VARCHAR(100) UNIQUE NOT NULL, -- Chave principal do sistema
    phone VARCHAR(20),
    country VARCHAR(100), -- País do influenciador
    owner VARCHAR(50) CHECK (owner IN ('users', 'cellphone', 'multiple')), -- Responsável pelo influenciador
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. Tabela `influencer_ids` - IDs das Plataformas Sociais

```sql
-- Armazena usernames e IDs únicos de cada plataforma social
CREATE TABLE influencer_ids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eldorado_username VARCHAR(100) REFERENCES influencers(eldorado_username) ON DELETE CASCADE,
    -- TikTok
    tiktok_username VARCHAR(100),
    tiktok_id VARCHAR(255), -- ID único obtido via API ScrapTik
    -- Instagram
    instagram_username VARCHAR(100),
    instagram_id VARCHAR(255), -- Para implementação futura
    -- Facebook
    facebook_username VARCHAR(100),
    facebook_id VARCHAR(255), -- Para implementação futura
    -- X (Twitter)
    x_username VARCHAR(100),
    x_id VARCHAR(255), -- Para implementação futura
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(eldorado_username) -- Um registro por influenciador
);
```

#### 3. Tabela `tiktok_videos` - Vídeos Patrocinados

```sql
-- Armazena APENAS vídeos que mencionam @El Dorado P2P
CREATE TABLE tiktok_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eldorado_username VARCHAR(100) REFERENCES influencers(eldorado_username),
    tiktok_username VARCHAR(100) NOT NULL,
    tiktok_video_id VARCHAR(255) UNIQUE NOT NULL, -- ID único do vídeo no TikTok
    description TEXT, -- Descrição completa do vídeo
    -- Métricas (atualizadas automaticamente)
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    -- URLs
    public_video_url VARCHAR(1000), -- Link público do vídeo
    watermark_free_url VARCHAR(1000), -- URL do CDN TikTok sem marca d'água
    -- Timestamps
    published_at TIMESTAMP, -- Data de publicação no TikTok
    created_at TIMESTAMP DEFAULT NOW(), -- Data de inserção no sistema
    updated_at TIMESTAMP DEFAULT NOW(), -- Última atualização das métricas
    
    INDEX idx_eldorado_username (eldorado_username),
    INDEX idx_published_date (published_at),
    INDEX idx_likes (like_count DESC),
    INDEX idx_views (view_count DESC)
);
```

### Tabelas de Apoio (Mantidas do Sistema Original)

```sql
-- Campanhas (opcional - para futuras expansões)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Parcerias (opcional - para futuras expansões)  
CREATE TABLE partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eldorado_username VARCHAR(100) REFERENCES influencers(eldorado_username),
    campaign_id UUID REFERENCES campaigns(id),
    contract_value DECIMAL(10,2),
    expected_videos INTEGER,
    delivered_videos INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Fluxo de Processamento de Dados

### 1. Cadastro de Influenciadores

**Processo Manual pela Equipe de Recrutamento:**
1. **Formulário de Cadastro** - Time de recrutamento preenche dados básicos:
   - Nome do influenciador
   - Username único da El Dorado 
   - Telefone para contato
   - País de origem
   - Responsável pela gestão (users/cellphone/multiple)
   - Username do TikTok

2. **Inserção no DB** - Dados são salvos na tabela `influencers`

### 2. Enriquecimento Automático

**Conversão Username → ID (RapidAPI ScrapTik):**
1. Sistema pega `tiktokUsername` da tabela `influencers`
2. Chama API "Username to ID" do ScrapTik
3. Salva `tiktokId` na tabela `influencer_ids`
4. Mantém relacionamento via `eldoradoUsername`

### 3. Coleta de Vídeos

**Busca de Vídeos Recentes:**
1. Sistema usa `tiktokId` para chamar API "User Posts" do ScrapTik
2. Recebe JSON com últimos 20 vídeos do influenciador
3. **Filtro Inteligente**: Processa apenas vídeos que contêm `@El Dorado P2P` na descrição
4. **Controle de Duplicação**: Verifica se `tiktok_video_id` já existe no DB
   - Se existe → **UPDATE** métricas (views, likes, etc.)
   - Se não existe → **INSERT** novo vídeo na tabela `tiktok_videos`

### 4. Agendamento

**Frequência de Atualização:**
- **Opção 1**: Execução diária automática (recomendado)
- **Opção 2**: Execução manual via botão/endpoint
- **Celery Task**: Processa todos influenciadores ativos

```python
@celery.task
def sync_influencer_videos():
    """Sincroniza vídeos de todos os influenciadores ativos"""
    influencers = get_active_influencers()
    for influencer in influencers:
        # 1. Get TikTok ID
        tiktok_id = get_or_create_tiktok_id(influencer.eldorado_username)
        
        # 2. Fetch recent videos
        videos = scrap_tik_api.get_user_posts(tiktok_id)
        
        # 3. Filter sponsored videos
        sponsored_videos = filter_eldorado_videos(videos)
        
        # 4. Insert or update
        process_sponsored_videos(sponsored_videos, influencer.eldorado_username)
```

## 🔧 Configuração do Projeto

### 1. Pré-requisitos
```bash
# Python 3.9+
# PostgreSQL 13+
# Redis 6+
```

### 2. Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd el-dorado-influencer-system

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
```

### 3. Configuração do Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Configure as variáveis
DATABASE_URL=postgresql://user:password@localhost:5432/eldorado_db
REDIS_URL=redis://localhost:6379
# RapidAPI ScrapTik Configuration
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=scraptik.p.rapidapi.com
SECRET_KEY=your_secret_key_here
```

### 4. Inicialização do Banco
```bash
# Execute migrações
alembic upgrade head

# (Opcional) Dados de exemplo
python scripts/seed_data.py
```

## 🔗 Integração com RapidAPI ScrapTik

### APIs Utilizadas

#### 1. Username to ID Converter
```http
GET https://scraptik.p.rapidapi.com/username-to-id
```
**Parâmetros:**
- `username`: Username do TikTok (sem @)

**Response:**
```json
{
  "id": "7234567890123456789",
  "username": "exemplo_usuario"
}
```

#### 2. User Posts
```http  
GET https://scraptik.p.rapidapi.com/user-posts
```
**Parâmetros:**
- `id`: ID único do usuário TikTok
- `count`: Número de vídeos (max 20)

**Response Estrutura:**
```json
{
  "data": [
    {
      "id": "7234567890123456789",
      "desc": "Descrição do vídeo com @El Dorado P2P #eldorado",
      "createTime": 1693526400,
      "video": {
        "id": "video_id_123",
        "downloadAddr": "https://v45.tiktokcdn-eu.com/..."
      },
      "stats": {
        "diggCount": 1250,
        "shareCount": 45,
        "commentCount": 123,
        "playCount": 15670
      },
      "webVideoUrl": "https://www.tiktok.com/@user/video/123"
    }
  ]
}
```

### 3. Processamento de Dados

**Filtro de Vídeos Patrocinados:**
```python
def filter_eldorado_videos(videos_data):
    """Filtra apenas vídeos que mencionam @El Dorado P2P"""
    sponsored_videos = []
    
    for video in videos_data.get('data', []):
        desc = video.get('desc', '').lower()
        if '@el dorado p2p' in desc:
            sponsored_videos.append({
                'tiktok_video_id': video['id'],
                'description': video['desc'],
                'published_at': datetime.fromtimestamp(video['createTime']),
                'view_count': video['stats']['playCount'],
                'like_count': video['stats']['diggCount'],
                'comment_count': video['stats']['commentCount'],
                'share_count': video['stats']['shareCount'],
                'public_video_url': video['webVideoUrl'],
                'watermark_free_url': video['video']['downloadAddr']
            })
    
    return sponsored_videos
```

## 🚀 API Endpoints

### Influenciadores
```http
GET    /api/v1/influencers/                    # Listar influenciadores
POST   /api/v1/influencers/                    # Criar influenciador
GET    /api/v1/influencers/{eldorado_username} # Buscar por username El Dorado
PUT    /api/v1/influencers/{eldorado_username} # Atualizar
DELETE /api/v1/influencers/{eldorado_username} # Remover
```

### Vídeos Patrocinados
```http
GET    /api/v1/videos/                         # Listar vídeos patrocinados
POST   /api/v1/videos/sync/{eldorado_username} # Sincronizar vídeos do influenciador
GET    /api/v1/videos/sync/all                 # Sincronizar todos os influenciadores
GET    /api/v1/videos/{video_id}               # Buscar vídeo específico
```

### Analytics e Relatórios
```http
GET    /api/v1/analytics/dashboard             # Dashboard geral
GET    /api/v1/analytics/influencer/{username} # Métricas por influenciador
GET    /api/v1/analytics/period                # Relatório por período
GET    /api/v1/analytics/top-videos            # Top 10 vídeos (likes, views, etc.)
GET    /api/v1/analytics/monthly-summary       # Resumo mensal
```

### ScrapTik Integration (Interno)
```http
POST   /api/v1/scraptik/get-user-id            # Converter username para ID
POST   /api/v1/scraptik/fetch-videos           # Buscar vídeos de um usuário
```

## 🎯 Lógica de Filtragem de Vídeos Patrocinados

### Critérios de Seleção

**Filtro Principal**: Menção obrigatória de `@El Dorado P2P` na descrição do vídeo

#### Processo de Filtragem:
1. **Recebimento**: Sistema recebe JSON com até 20 vídeos recentes do influenciador
2. **Análise da Descrição**: Para cada vídeo, verifica se contém a string `@El Dorado P2P` (case-insensitive)
3. **Descarte**: Vídeos sem a menção são ignorados completamente
4. **Verificação de Duplicação**: Vídeos com menção são verificados contra `tiktok_video_id` existente
5. **Ação**:
   - **Se EXISTS**: UPDATE das métricas (views, likes, comments, shares)
   - **Se NOT EXISTS**: INSERT novo registro completo

#### Exemplo de Código:
```python
def process_video_batch(videos_data, eldorado_username):
    """Processa lote de vídeos aplicando filtros El Dorado"""
    
    for video in videos_data.get('data', []):
        # 1. Filtro de menção obrigatória
        desc = video.get('desc', '').lower()
        if '@el dorado p2p' not in desc:
            continue  # Ignora vídeos não patrocinados
            
        # 2. Extrai dados relevantes
        video_data = {
            'tiktok_video_id': video['id'],
            'eldorado_username': eldorado_username,
            'description': video['desc'],
            'view_count': video['stats']['playCount'],
            'like_count': video['stats']['diggCount'],
            'comment_count': video['stats']['commentCount'],
            'share_count': video['stats']['shareCount'],
            'published_at': datetime.fromtimestamp(video['createTime'])
        }
        
        # 3. Verificação de duplicação e ação
        existing_video = db.query(TikTokVideo).filter_by(
            tiktok_video_id=video_data['tiktok_video_id']
        ).first()
        
        if existing_video:
            # UPDATE - Atualiza apenas métricas
            update_video_metrics(existing_video, video_data)
        else:
            # INSERT - Novo vídeo patrocinado
            create_new_sponsored_video(video_data)
```

### Validações Adicionais

#### Controle de Data:
- Verificar se `published_at` é consistente com dados existentes
- Evitar inserção de vídeos com datas futuras
- Garantir ordem cronológica dos dados

#### Controle de Qualidade:
- Verificar se campos obrigatórios estão presentes
- Validar URLs de vídeo
- Controlar métricas negativas ou inconsistentes

## 📈 Funcionalidades

### 1. Monitoramento de Vídeos Patrocinados
- Sincronização automática focada em conteúdo El Dorado
- Detecção de novos vídeos com menção `@El Dorado P2P`
- Atualização de métricas de engajamento
- Histórico de crescimento de views/likes

### 2. Analytics de Performance
- **Dashboard Geral**: Visão consolidada de todos os vídeos patrocinados
- **Top Rankings**: 
  - Top 10 vídeos por likes
  - Top 10 vídeos por views
  - Top 10 vídeos por engagement rate
- **Análise Temporal**:
  - Vídeos publicados por mês/período
  - Crescimento de métricas ao longo do tempo
  - Sazonalidade de campanhas

### 3. Relatórios Especializados
- **Por Influenciador**: Quantos vídeos cada um publicou
- **Por Período**: Performance mensal/trimestral
- **ROI Analysis**: Efetividade dos investimentos
- **Engagement Metrics**: Taxa de interação média

### 4. Insights de Negócio
- Identificação de influenciadores mais engajados
- Análise de horários/dias de maior performance
- Tracking de crescimento orgânico dos vídeos
- Comparativo de performance entre influenciadores

## 🔄 Tarefas Automatizadas

### Celery Tasks Especializadas

```python
# Sincronização completa diária
@celery.task
def sync_all_influencers():
    """Sincroniza vídeos patrocinados de todos os influenciadores ativos"""
    active_influencers = get_active_influencers()
    
    for influencer in active_influencers:
        # 1. Obter ou criar TikTok ID
        tiktok_id = ensure_tiktok_id(influencer.eldorado_username)
        
        # 2. Buscar vídeos recentes
        videos = scrap_tik_api.get_user_posts(tiktok_id, count=20)
        
        # 3. Processar apenas vídeos com @El Dorado P2P
        process_sponsored_videos(videos, influencer.eldorado_username)

# Atualização de métricas existentes
@celery.task  
def update_existing_videos_metrics():
    """Atualiza métricas de vídeos já catalogados"""
    existing_videos = get_existing_sponsored_videos()
    
    for video in existing_videos:
        # Busca métricas atualizadas
        fresh_data = scrap_tik_api.get_video_stats(video.tiktok_video_id)
        update_video_metrics(video, fresh_data)

# Geração de relatórios analíticos
@celery.task
def generate_analytics_reports():
    """Gera relatórios automáticos de performance"""
    
    # Relatório mensal
    monthly_report = generate_monthly_summary()
    
    # Top performers
    top_videos = get_top_performing_videos(limit=10)
    
    # Enviar por email/Slack
    send_analytics_report(monthly_report, top_videos)

# Limpeza e manutenção
@celery.task
def cleanup_old_data():
    """Remove dados antigos e desnecessários"""
    # Remove métricas antigas (manter apenas última)
    cleanup_duplicate_metrics()
    
    # Arquiva vídeos muito antigos
    archive_old_videos(days=365)
```

### Agendamento (Celery Beat)

```python
# schedule.py
CELERY_BEAT_SCHEDULE = {
    # Sincronização principal - diária às 6h
    'sync-influencers-daily': {
        'task': 'sync_all_influencers',
        'schedule': crontab(hour=6, minute=0),
    },
    
    # Atualização de métricas - a cada 4 horas
    'update-metrics': {
        'task': 'update_existing_videos_metrics', 
        'schedule': crontab(minute=0, hour='*/4'),
    },
    
    # Relatórios semanais - segunda às 9h
    'weekly-reports': {
        'task': 'generate_analytics_reports',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
    
    # Limpeza mensal - primeiro dia do mês
    'monthly-cleanup': {
        'task': 'cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
    }
}
```

## 📊 Exemplos de Analytics e Queries

### Relatórios Implementáveis

#### 1. Top 10 Vídeos por Métricas
```sql
-- Top 10 vídeos por likes
SELECT 
    eldorado_username,
    tiktok_username,
    description,
    like_count,
    view_count,
    published_at
FROM tiktok_videos 
ORDER BY like_count DESC 
LIMIT 10;

-- Top 10 por engagement rate
SELECT 
    eldorado_username,
    (like_count + comment_count + share_count) / NULLIF(view_count, 0) * 100 as engagement_rate,
    description
FROM tiktok_videos 
WHERE view_count > 0
ORDER BY engagement_rate DESC 
LIMIT 10;
```

#### 2. Análises Temporais
```sql  
-- Vídeos publicados por mês
SELECT 
    DATE_TRUNC('month', published_at) as mes,
    COUNT(*) as total_videos,
    AVG(view_count) as media_views,
    SUM(like_count) as total_likes
FROM tiktok_videos 
GROUP BY mes 
ORDER BY mes DESC;

-- Performance por influenciador no período
SELECT 
    eldorado_username,
    COUNT(*) as videos_publicados,
    AVG(like_count) as media_likes,
    MAX(view_count) as melhor_performance
FROM tiktok_videos 
WHERE published_at >= '2024-01-01'
GROUP BY eldorado_username
ORDER BY media_likes DESC;
```

#### 3. Insights de Negócio
```sql
-- Influenciadores mais ativos (que mais publicam)
SELECT 
    eldorado_username,
    COUNT(*) as total_videos,
    DATE(MAX(published_at)) as ultimo_video
FROM tiktok_videos 
GROUP BY eldorado_username
ORDER BY total_videos DESC;

-- Crescimento mensal de métricas
SELECT 
    DATE_TRUNC('month', published_at) as mes,
    SUM(view_count) as total_visualizacoes,
    AVG(like_count) as media_curtidas,
    COUNT(DISTINCT eldorado_username) as influenciadores_ativos
FROM tiktok_videos 
GROUP BY mes 
ORDER BY mes;
```

## 📋 Roadmap Atualizado

### Fase 1 - MVP Core (3-4 semanas)
- [x] **Estrutura do banco de dados** (3 tabelas especializadas)
- [ ] **API básica FastAPI** (CRUD influenciadores)
- [ ] **Integração RapidAPI ScrapTik** (Username to ID + User Posts)
- [ ] **Formulário de cadastro** (para equipe de recrutamento)
- [ ] **Filtro de vídeos patrocinados** (@El Dorado P2P)

### Fase 2 - Automação e Processamento (3-4 semanas)
- [ ] **Celery Tasks** (sincronização automática)
- [ ] **Scheduler diário** (Celery Beat)
- [ ] **Controle de duplicação** (UPDATE vs INSERT)
- [ ] **Dashboard básico** (listagem e métricas simples)
- [ ] **APIs de analytics** (endpoints de relatórios)

### Fase 3 - Analytics Avançados (4 semanas)
- [ ] **Relatórios especializados** (Top 10, rankings, períodos)
- [ ] **Frontend dashboard** (React/Next.js)
- [ ] **Gráficos interativos** (Chart.js)
- [ ] **Exportação de dados** (CSV/Excel)
- [ ] **Notificações** (vídeos virais, relatórios semanais)

### Fase 4 - Expansão e Otimização (futuro)
- [ ] **Multi-plataforma** (Instagram, Facebook, X)
- [ ] **ML para insights** (previsão de performance)
- [ ] **API pública** (para outros sistemas El Dorado)
- [ ] **Mobile dashboard** (visualização móvel)
- [ ] **Cache inteligente** (Redis para queries frequentes)

## 🚀 Como Executar

### Desenvolvimento
```bash
# Backend API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Celery Worker
celery -A app.celery worker --loglevel=info

# Celery Beat (scheduler)
celery -A app.celery beat --loglevel=info
```

### Produção
```bash
# Docker Compose
docker-compose up -d

# Ou usando Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🧪 Testes
```bash
# Testes unitários
pytest tests/

# Cobertura
pytest --cov=app tests/

# Testes de integração
pytest tests/integration/
```

## 📝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

- **Projeto**: El Dorado Influencer Management System
- **Email**: contato@eldorado.com.br
- **Slack**: #influencer-system

---

**Desenvolvido com ❤️ para El Dorado**