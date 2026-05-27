# QuantVision — Especificación Técnica

## 1. Visión y Objetivos

**QuantVision** es una plataforma SaaS para inversores novatos que combina herramientas profesionales de análisis financiero con educación interactiva y gamificación. El objetivo es hacer los mercados financieros accesibles para todos, ofreciendo datos reales, algoritmos robustos y una experiencia de aprendizaje atractiva.

### Target Users
- Inversores novatos que quieren aprender a analizar activos
- Estudiantes de finanzas que practican con datos reales
- Personas que quieren trackear su portfolio sin transacciones reales

---

## 2. Stack Tecnológico (100% Free)

| Capa | Tecnología | Costo |
|------|------------|-------|
| Frontend | Next.js 14 (App Router) + TypeScript + TailwindCSS + shadcn/ui | $0 (Vercel) |
| Backend | FastAPI (Python 3.11+) + Pydantic v2 | $0 |
| Database | PostgreSQL (Neon/Render free tier) | $0 |
| Cache/Sessions | Redis (Render free tier) | $0 |
| Auth | NextAuth.js v5 (JWT + OAuth) | $0 |
| Charts | Recharts + Lightweight Charts (TradingView) | $0 |
| Hosting | Vercel (frontend) + Render (backend) | $0 |

---

## 3. Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                       │
│                  Vercel (vercel.app)                         │
│                                                               │
│  / (landing), /login, /register, /dashboard, /research,     │
│  /portfolio, /education, /achievements, /profile           │
└──────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│                   Render (render.com)                          │
│                                                               │
│  /api/v1/auth/*    → Autenticación (JWT + OAuth)              │
│  /api/v1/assets/*  → Datos de activos (Yahoo Finance)         │
│  /api/v1/research/* → Algoritmos (DTW, Pearson, etc.)       │
│  /api/v1/portfolio/* → Portfolio + Transactions              │
│  /api/v1/news/*    → RSS feeds                                │
│  /api/v1/education/* → Lecciones + Quizzes                   │
│  /api/v1/gamification/* → XP + Achievements + Leaderboard   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  PostgreSQL (users, progress, portfolios, etc.)    │      │
│  └─────────────────────────────────────────────────────┘      │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  Redis (sessions, rate limiting, cache)            │      │
│  └─────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Diseño de Base de Datos (PostgreSQL)

### Tablas

```sql
-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),           -- NULL si es OAuth-only
    name VARCHAR(100),
    avatar_url TEXT,
    auth_provider VARCHAR(20) DEFAULT 'email',  -- 'email', 'google', 'github', 'apple'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- GAMIFICATION
-- ============================================

CREATE TABLE user_progress (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    xp INTEGER DEFAULT 0,
    level VARCHAR(50) DEFAULT 'Beginner',
    streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    total_lessons_completed INTEGER DEFAULT 0,
    total_quizzes_passed INTEGER DEFAULT 0,
    total_research_sessions INTEGER DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(50),                    -- emoji
    xp_reward INTEGER DEFAULT 50,
    category VARCHAR(50) NOT NULL,       -- 'research', 'education', 'portfolio', 'special'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_achievements (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, achievement_id)
);

-- ============================================
-- EDUCATION
-- ============================================

CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,                        -- Markdown
    xp_reward INTEGER DEFAULT 25,
    order_index INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL,     -- 'basics', 'technical', 'risk', 'strategies'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB NOT NULL,             -- [{"text": "...", "correct": true}, ...]
    explanation TEXT
);

CREATE TABLE user_lesson_progress (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, lesson_id)
);

CREATE TABLE user_quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    selected_option INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- PORTFOLIO
-- ============================================

CREATE TABLE portfolios (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id UUID REFERENCES portfolios(user_id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,  -- 'BUY' o 'SELL'
    shares NUMERIC NOT NULL,
    price_per_share NUMERIC NOT NULL,
    total_amount NUMERIC NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE watchlists (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, symbol)
);

-- ============================================
-- NEWS
-- ============================================

CREATE TABLE user_news_read (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    news_url TEXT NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, news_url)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_user_progress_streak ON user_progress(streak_days);
CREATE INDEX idx_lessons_category ON lessons(category);
CREATE INDEX idx_lessons_order ON lessons(order_index);
```

---

## 5. API Endpoints (FastAPI)

### Auth
```
POST   /api/v1/auth/register           → Registro (email + password)
POST   /api/v1/auth/login              → Login → JWT token
POST   /api/v1/auth/logout             → Invalidar sesión
GET    /api/v1/auth/me                 → Usuario actual (protegido)
PATCH  /api/v1/auth/me                 → Actualizar perfil (protegido)
POST   /api/v1/auth/oauth/{provider}   → OAuth (Google/GitHub/Apple)
```

### Assets
```
GET    /api/v1/assets                  → Lista de activos disponibles
GET    /api/v1/assets/search?q=        → Buscar por símbolo/nombre
GET    /api/v1/assets/{symbol}         → Perfil detallado (precio, cambio, stats)
GET    /api/v1/assets/{symbol}/ohlc    → Datos OHLC para gráficos
GET    /api/v1/assets/{symbol}/history  → Precios históricos
```

### Research (Tus Algoritmos)
```
GET    /api/v1/research/compare?s1=&s2=&window=  → Comparar 2 activos (4 algoritmos)
GET    /api/v1/research/correlation-matrix        → Matriz de correlación (Pearson)
GET    /api/v1/research/volatility-ranking         → Ranking de volatilidad
GET    /api/v1/research/patterns?symbol=&type=   → Detectar patrones
GET    /api/v1/research/benchmark                 → Benchmark de algoritmos de ordenamiento
```

### Portfolio
```
GET    /api/v1/portfolio                              → Mi portfolio (transacciones + valoración)
POST   /api/v1/portfolio/transactions                 → Registrar transacción
DELETE /api/v1/portfolio/transactions/{id}           → Eliminar transacción
GET    /api/v1/portfolio/performance                  → Métricas de rendimiento
GET    /api/v1/portfolio/watchlist                    → Mi watchlist
POST   /api/v1/portfolio/watchlist/{symbol}           → Agregar a watchlist
DELETE /api/v1/portfolio/watchlist/{symbol}           → Quitar de watchlist
```

### News
```
GET    /api/v1/news                     → Últimas noticias financieras
GET    /api/v1/news/{symbol}             → Noticias filtradas por activo
POST   /api/v1/news/mark-read            → Marcar noticia como leída (para XP)
```

### Education
```
GET    /api/v1/education/lessons                     → Lista de lecciones
GET    /api/v1/education/lessons/{slug}              → Detalle de lección
GET    /api/v1/education/lessons/{slug}/quiz         → Quiz de la lección
POST   /api/v1/education/quiz/{quizId}/submit         → Responder quiz
GET    /api/v1/education/progress                    → Progreso del usuario
POST   /api/v1/education/lesson/{lessonId}/complete  → Marcar lección como completada
```

### Gamification
```
GET    /api/v1/gamification/profile          → Perfil (XP, nivel, streak)
GET    /api/v1/gamification/achievements     → Logros (todos con estado unlocked/locked)
GET    /api/v1/gamification/leaderboard      → Top 50 inversores por XP
```

---

## 6. Sistema de Gamificación

### XP Rewards
| Acción | XP |
|--------|-----|
| Registrar cuenta | +50 |
| Investigar un activo | +10 |
| Leer noticia | +5 |
| Agregar a watchlist | +2 |
| Completar lección | +25 |
| Quiz aprobado (>70%) | +15 |
| Quiz perfecto (100%) | +30 |
| Registrar transacción | +10 |
| Logro desbloqueado | +50 |
| Streak de 7 días | +100 |
| Streak de 30 días | +500 |

### Niveles
| Nivel | XP Mínima | Título |
|-------|-----------|--------|
| Beginner | 0 | Novato |
| Explorer | 101 | Explorador |
| Analyst | 501 | Analista |
| Trader | 1501 | Trader |
| Veteran | 5001 | Veterano |
| Master | 15001 | Maestro Financiero |

### Logros (Achievements)
**Research** (category: research):
- `first_search` — First Search — Realiza tu primera búsqueda
- `curious` — Curioso — Investiga 5 activos diferentes
- `diversified_research` — Diversificado — Investiga 10 activos diferentes
- `chart_master` — Maestro de Gráficos — Ve 50 gráficos
- `comparer` — Comparador Pro — Compara 20 pares de activos

**Education** (category: education):
- `first_lesson` — Primera Lección — Completa tu primera lección
- `scholar` — Erudito — Completa 3 lecciones
- `educated` — Educado — Completa 5 lecciones
- `quiz_ace` — Quiz Ace — Aprueba 10 quizzes
- `perfect_quiz` — Quiz Perfecto — Obtén 100% en un quiz
- `streak_7` — Semana Perfecta — 7 días consecutivos aprendiendo
- `streak_30` — Mes Perfecto — 30 días consecutivos aprendiendo

**Portfolio** (category: portfolio):
- `first_trade` — Primer Trade — Registra tu primera transacción
- `five_positions` — Carterista — 5 posiciones en portfolio
- `ten_positions` — Diversificado — 10 posiciones en portfolio

**Special** (category: special):
- `all_rounder` — Completo — Completa 1 de cada categoría
- `master_investor` — Maestro Inversor — Alcanza nivel Master

---

## 7. Las 10 Lecciones

| # | Slug | Título | Categoría | XP |
|---|------|--------|-----------|-----|
| 1 | what-is-a-stock | ¿Qué es una acción? | basics | 25 |
| 2 | etfs-vs-stocks | ETFs vs Acciones | basics | 25 |
| 3 | reading-charts | Lectura de gráficos | basics | 25 |
| 4 | candlesticks | Velas japonesas (Candlesticks) | technical | 25 |
| 5 | volatility-risk | Volatilidad y riesgo | risk | 25 |
| 6 | diversification | Diversificación | strategies | 25 |
| 7 | fundamental-vs-technical | Análisis fundamental vs técnico | technical | 25 |
| 8 | momentum-trading | Momentum trading | strategies | 25 |
| 9 | mean-reversion | Mean reversion | strategies | 25 |
| 10 | risk-management | Gestión de riesgo | risk | 25 |

---

## 8. Activos Disponibles

### Stocks (BVC + NYSE)
- BVC: ECOPETROL, ISA, GEB, NUTRESA
- NYSE: KO, PEP, PFE, AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, AMD, INTC, NFLX, DIS, BA, JPM, BAC, WFC, GS, MS

### ETFs
VOO, VTI, QQQ, SPY, VEA, VWO, BND, EFA, EEM, TLT, IVV, SCHD, DIA, IWM, XLF, XLK, VIG, QUAL, USMV, ITOT, IXUS, ACWI

### Crypto
BTC, ETH, SOL, XRP, ADA, DOGE, DOT, AVAX, MATIC, LINK, UNI, ATOM, LTC, BCH, XLM, ALGO, VET, FIL, THETA

---

## 9. RSS Feeds de Noticias

```
Yahoo Finance: https://finance.yahoo.com/news/rssindex
MarketWatch: https://feeds.content.dowjones.io/public/rss/mw_topstories
```

---

## 10. Frontend: Estructura de Páginas

### Landing (`/`)
- Hero con tagline y CTA
- Features highlights
- Screenshots del dashboard
- Footer

### Login (`/login`)
- Form email/password
- Botones OAuth (Google, GitHub, Apple)
- Link a register

### Register (`/register`)
- Form name, email, password
- Términos y condiciones

### Dashboard (`/dashboard`)
- Quick stats: XP, nivel, streak
- Top movers del día
- Recent activity
- Watchlist preview
- News feed

### Research Center (`/research`)
- Buscador de activos
- Asset cards con precio y cambio %
- Tabs: Overview, Charts, Compare, Correlation, Patterns, News

### Asset Detail (`/research/[symbol]`)
- Precio actual, cambio %, stats
- Gráfico interactivo (candlestick + SMA)
- Comparador de similitud
- Matriz de correlación
- News del activo

### Portfolio (`/portfolio`)
- Valor total con P&L
- Allocation pie chart
- Tabla de posiciones
- Historial de transacciones
- Formulario para agregar transacción

### Education (`/education`)
- Lecciones organizadas por categoría
- Progreso por lección
- XP acumulado

### Lesson (`/education/[slug]`)
- Contenido markdown renderizado
- Quiz al final
- Botón "Completar lección"

### Achievements (`/achievements`)
- XP progress bar
- Achievements grid
- Leaderboard
- Streak calendar

### Profile (`/profile`)
- Avatar, nombre, email
- Estadísticas
- Configuración

---

## 11. Design System

### Colors
```
Background:     #0a0a0f (dark)
Surface:        #111118 (cards)
Border:         #1e1e2e
Primary:        #3b82f6 (blue)
Success/Up:     #22c55e (green)
Danger/Down:    #ef4444 (red)
Warning:        #f59e0b (amber)
Text Primary:   #f8fafc
Text Secondary: #94a3b8
```

### Typography
- UI: Inter (Google Fonts)
- Numbers/Code: JetBrains Mono (Google Fonts)

### Spacing
- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96

### Components (shadcn/ui)
- Button, Input, Select, Dialog, Tabs, Cards, Badges
- Progress (XP bars), Avatar, DropdownMenu

---

## 12. Requisitos del Proyecto Académico (Preservados)

Los siguientes algoritmos deben mantenerse implementados desde cero (no usar librerías que los encapsulen):

### Algoritmos de Similitud (Requerimiento 2)
- Distancia Euclidiana — O(n)
- Correlación de Pearson — O(n)
- Dynamic Time Warping (DTW) — O(n×m)
- Similitud por Coseno — O(n)

### Patrones (Requerimiento 3)
- Días consecutivos al alza (sliding window) — O(n)
- Gap Up/Down — O(n)
- Detección de breakout — O(n)

### Volatilidad y Riesgo
- Desviación estándar — O(n)
- Volatilidad anualizada — O(n)
- Clasificación: Conservador <15%, Moderado 15-30%, Agresivo >30%

### Algoritmos de Ordenamiento (12 algoritmos)
Selection Sort, Insertion Sort, Binary Insertion Sort, Merge Sort, TimSort, QuickSort, HeapSort, Tree Sort, Comb Sort, Gnome Sort, Radix Sort, Bucket Sort, Pigeonhole Sort, Bitonic Sort

### ETL Pipeline
- Extracción HTTP directa (sin yfinance)
- Limpieza (duplicados, outliers, interpolación)
- Unificación (alineación de calendarios)

---

## 13. Restricciones

### NO usar
- `yfinance`, `pandas_datareader` para descarga de datos
- `scikit-learn`, `scipy` para algoritmos de similitud o clustering
- Librerías que implementen DTW en una llamada
- Datasets estáticos pre-descargados

### SÍ usar
- `requests` para HTTP
- `csv`, `json` para parsing
- `numpy` para operaciones matemáticas básicas
- `matplotlib` para gráficos estáticos
- RSS libraries para news

---

## 14. Deploy

### Backend (Render)
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Environment: Python 3.11
- Free tier: 512MB RAM, sleeps after 15min inactivity

### Frontend (Vercel)
- Framework: Next.js 14
- Auto-deploy from git
- Environment vars: `NEXT_PUBLIC_API_URL`, `NEXTAUTH_SECRET`, OAuth credentials

---

## 15. Roadmap de Implementación

### Fase 0: Setup
- [ ] Crear repositorio `quantvision`
- [ ] Backend: FastAPI + PostgreSQL + Redis en Render
- [ ] Frontend: Next.js en Vercel
- [ ] Conectar frontend ↔ backend

### Fase 1: Auth
- [ ] Registro + Login (JWT)
- [ ] OAuth (Google, GitHub)
- [ ] Perfil de usuario

### Fase 2: Research Core
- [ ] Migrar algoritmos a `backend/services/`
- [ ] Endpoints `/assets` con Yahoo Finance
- [ ] Research page con gráficos
- [ ] Comparador de similitud

### Fase 3: Portfolio
- [ ] CRUD de transacciones
- [ ] P&L en tiempo real
- [ ] Watchlist

### Fase 4: Education
- [ ] 10 lecciones (markdown)
- [ ] Motor de quizzes
- [ ] Tracking de progreso

### Fase 5: Gamification
- [ ] XP system
- [ ] Achievements
- [ ] Streaks
- [ ] Leaderboard

### Fase 6: News
- [ ] RSS parser
- [ ] News page
- [ ] News por activo

### Fase 7: Polish
- [ ] Responsive design
- [ ] Testing
- [ ] Deploy producción