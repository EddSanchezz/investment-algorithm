# QuantVision Backend

API REST para QuantVision - Plataforma de inversión educativa y análisis profesional.

## Stack

- **FastAPI** (Python 3.11+)
- **PostgreSQL** (async con SQLAlchemy + asyncpg)
- **Redis** (sesiones y cache)
- **JWT** (autenticación)

## Setup Local

### 1. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. Variables de entorno

Crear `.env` en `backend/`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/quantvision
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=tu-secret-key-super-secreto
CORS_ORIGINS=["http://localhost:3000"]
DEBUG=true
```

### 3. Ejecutar con Docker Compose

```bash
docker-compose up -d
```

Esto levantará:
- PostgreSQL en `localhost:5432`
- Redis en `localhost:6379`
- API en `localhost:8000`

### 4. Sin Docker (solo API)

```bash
# Crear base de datos PostgreSQL
createdb quantvision

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

Documentación interactiva disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Principales

```
POST /api/v1/auth/register     Registro
POST /api/v1/auth/login         Login
GET  /api/v1/assets             Lista de activos
GET  /api/v1/research/compare   Comparar activos
GET  /api/v1/research/volatility-ranking  Ranking de volatilidad
GET  /api/v1/education/lessons  Lecciones
GET  /api/v1/gamification/achievements  Logros
```

## Tests

```bash
pytest tests/ -v
```

## Deploy

### Render (Backend)

1. Crear Web Service en Render
2. Conectar con repositorio GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Agregar environment variables desde `.env`

### Vercel (Frontend)

Ver carpeta `frontend/`