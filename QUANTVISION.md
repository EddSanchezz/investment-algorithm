# QuantVision - Especificación del Proyecto

## 🎯 Visión
Plataforma SaaS todo-en-uno para traders cuantitativos que combina herramientas profesionales de análisis con educación interactiva.

---

## 📦 Fases de Implementación

### Fase 1: MVP (Semana 1-2)
- [ ] Renombrar proyecto a "QuantVision"
- [ ] Landing page profesional
- [ ] API con autenticación básica (API Keys)
- [ ] Endpoints de similitud y patrones funcionando
- [ ] Dashboard básico con gráficos

### Fase 2: Core Features (Semana 3-4)
- [ ] Motor de backtesting completo
- [ ] Sistema de alertas en tiempo real
- [ ] Screener de patrones con IA
- [ ] Integración con datos reales (Yahoo Finance, Alpha Vantage)

### Fase 3: Educativo (Semana 5-6)
- [ ] Sistema de cursos
- [ ] Lecciones interactivas con código
- [ ] Proyectos prácticos con backtesting
- [ ] Certificados de finalización

### Fase 4: Monetización (Semana 7-8)
- [ ] Sistema de planes (Free/Pro/Enterprise)
- [ ] Stripe integration
- [ ] Dashboard de usuario con uso
- [ ] Panel de administración

---

## 🏗️ Arquitectura

```
QuantVision/
├── api/                    # FastAPI REST API
│   ├── routes/
│   │   ├── auth.py         # Autenticación
│   │   ├── patterns.py     # Detección de patrones
│   │   ├── backtest.py     # Motor de backtesting
│   │   ├── screener.py     # Screener con IA
│   │   ├── courses.py      # Sistema de cursos
│   │   └── user.py         # Perfil y uso
│   ├── core/
│   │   ├── auth.py         # JWT, API Keys
│   │   ├── billing.py      # Stripe integration
│   │   └── rate_limiter.py
│   └── models/             # Pydantic models
├── services/
│   ├── patterns/          # Algoritmos de detección
│   ├── backtesting/        # Motor de backtest
│   ├── ml/                # Modelos de IA
│   └── data/              # ETL y normalización
├── frontend/
│   ├── landing/           # Página de inicio
│   ├── dashboard/         # Panel principal
│   ├── courses/           # Sistema educativo
│   └── admin/             # Panel admin
├── workers/               # Tareas background
│   ├── alerts.py          # Procesamiento de alertas
│   └── data_sync.py       # Sincronización de datos
└── infrastructure/
    ├── docker/            # Contenedores
    ├── terraform/         # Infraestructura como código
    └── monitoring/        # Observabilidad
```

---

## 💰 Modelo de Negocio

| Plan | Precio | Requests/mes | Features |
|------|--------|--------------|----------|
| **Free** | $0 | 100 | 5 patrones, 1 símbolo, sin backtest |
| **Pro** | $29/mes | 10,000 | Todos los patrones, backtest ilimitado, alerts |
| **Team** | $79/mes | 50,000 | Multi-user, API keys, soporte |
| **Enterprise** | $199/mes | Ilimitado | SLA, custom integrations, dedicated support |

---

## 🧠 Algoritmos Principales

### 1. Detección de Patrones (50+ patrones chartistas)
- Triángulos (ascendente, descendente, simétrico)
- Hombre-Cabeza-Hombro (HCH)
- Doble techo / Doble suelo
- Banderas y banderines
- Cuñas
- Gap patterns

### 2. Backtesting
- Estrategias pre-configuradas (momentum, mean reversion, breakout)
- Métricas: Sharpe, Sortino, Max Drawdown, Win Rate
- Optimización de parámetros

### 3. Screener con IA
- Clasificación de patrones en tiempo real
- Scoring de oportunidad (1-100)
- Recomendaciones basadas en historial

---

## 📊 APIs Principales

```
POST /api/v1/auth/register     - Registro de usuario
POST /api/v1/auth/login         - Login (JWT)
GET  /api/v1/patterns/detect    - Detectar patrones en símbolo
GET  /api/v1/patterns/screener  - Buscar patrones en múltiples símbolos
POST /api/v1/backtest/run       - Ejecutar backtest
GET  /api/v1/courses           - Listar cursos
GET  /api/v1/courses/{id}      - Detalle de curso
POST /api/v1/alerts/create     - Crear alerta
```

---

## 🚀 Stack Tecnológico

- **Backend:** Python 3.11+, FastAPI, Pydantic
- **Base de datos:** PostgreSQL (usuarios), Redis (cache), SQLite (datos financieros)
- **ML:** scikit-learn, numpy para clasificación de patrones
- **Frontend:** React + TypeScript + TailwindCSS
- **Infra:** Docker, Railway/Render, Cloudflare
- **Pagos:** Stripe
- **Monitoreo:** Sentry, Prometheus

---

## 👤 Target Audience

1. **Traders individuales** que quieren sistematizar sus estrategias
2. **Estudiantes de finanzas** que aprenden trading cuantitativo
3. **Fintechs** que necesitan APIs de análisis financiero
4. **Hedge funds pequeños** que buscan herramientas accesibles

---

## 🏆 Diferenciadores Competitivos

1. **Algoritmos desde cero** - No dependemos de librerías externas (fortalece CV)
2. **Educación integrada** - Aprende mientras operas
3. **IA accesible** - ML para clasificación de patrones sin complejidad excesiva
4. **Precios justos** - Competimos con productos 10x más caros

---

## 📈 Métricas de Éxito

- 1,000 usuarios activos en 3 meses
- $5,000 MRR en 6 meses
- NPS > 50
- Tiempo de respuesta API < 200ms

---

## 🔜 Roadmap

### Q2 2026: MVP
- Landing page profesional
- API funcional con 10+ endpoints
- 50 patrones detectados
- Dashboard básico

### Q3 2026: Crecimiento
- Sistema de cursos
- Comunidad activa
- Integración con brokers
- Mobile app básica

### Q4 2026: Escalamiento
- API marketplace
- White-label para empresas
- Expansion LATAM
- $50k MRR target