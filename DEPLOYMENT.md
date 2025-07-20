# Guía de Despliegue - Weev MVP

## 🚀 Opciones de Despliegue

### 1. Heroku (Recomendado para MVP)

#### Preparación
```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login a Heroku
heroku login
```

#### Archivos necesarios
Crear `Procfile` en la raíz:
```
web: python src/main.py
```

Crear `runtime.txt`:
```
python-3.11.0
```

#### Despliegue
```bash
# Inicializar git (si no existe)
git init
git add .
git commit -m "Initial commit"

# Crear app en Heroku
heroku create weev-mvp-tu-nombre

# Configurar variables de entorno
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=tu-clave-super-secreta-aqui

# Deploy
git push heroku main

# Abrir la app
heroku open
```

### 2. Railway

#### Pasos
1. Conecta tu repositorio GitHub a Railway
2. Selecciona el proyecto
3. Railway detectará automáticamente que es Flask
4. Configura variables de entorno:
   - `FLASK_ENV=production`
   - `SECRET_KEY=tu-clave-secreta`
5. Deploy automático

### 3. Render

#### Configuración
1. Conecta repositorio GitHub
2. Crear Web Service
3. Configuración:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python src/main.py`
   - **Environment:** Python 3.11

### 4. DigitalOcean App Platform

#### Configuración
```yaml
# .do/app.yaml
name: weev-mvp
services:
- name: web
  source_dir: /
  github:
    repo: tu-usuario/weev-mvp
    branch: main
  run_command: python src/main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
  - key: SECRET_KEY
    value: tu-clave-secreta
```

## 🔧 Configuración de Producción

### Variables de Entorno Requeridas
```bash
FLASK_ENV=production
SECRET_KEY=clave-super-secreta-de-al-menos-32-caracteres
DATABASE_URL=sqlite:///database/app.db  # Para SQLite
# O para PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Modificaciones para Producción

#### 1. Actualizar main.py
```python
import os

# Configuración de producción
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
else:
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'dev-secret-key'

# Puerto dinámico para Heroku
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
```

#### 2. Configurar Base de Datos para Producción
```python
# Para PostgreSQL en producción
import os
from sqlalchemy import create_engine

if os.environ.get('DATABASE_URL'):
    # Usar PostgreSQL en producción
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # SQLite para desarrollo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
```

## 🔒 Seguridad en Producción

### 1. Variables de Entorno Seguras
```bash
# Generar clave secreta segura
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. HTTPS Forzado
```python
from flask_talisman import Talisman

if os.environ.get('FLASK_ENV') == 'production':
    Talisman(app, force_https=True)
```

### 3. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Lógica de login
```

## 📊 Monitoreo y Logs

### 1. Logging en Producción
```python
import logging
from logging.handlers import RotatingFileHandler

if os.environ.get('FLASK_ENV') == 'production':
    file_handler = RotatingFileHandler('logs/weev.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 2. Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }
```

## 🗄️ Base de Datos en Producción

### Migración a PostgreSQL (Recomendado)

#### 1. Instalar dependencias
```bash
pip install psycopg2-binary
```

#### 2. Configurar conexión
```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///database/app.db'
```

#### 3. Migrar datos
```python
# Script de migración (migration.py)
import sqlite3
import psycopg2
from urllib.parse import urlparse

def migrate_sqlite_to_postgres():
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect('src/database/app.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar a PostgreSQL
    postgres_url = urlparse(os.environ.get('DATABASE_URL'))
    postgres_conn = psycopg2.connect(
        database=postgres_url.path[1:],
        user=postgres_url.username,
        password=postgres_url.password,
        host=postgres_url.hostname,
        port=postgres_url.port
    )
    postgres_cursor = postgres_conn.cursor()
    
    # Migrar tablas...
    # (Código específico de migración)
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "weev-mvp"
        heroku_email: "tu@email.com"
```

## 📈 Escalabilidad

### 1. Configuración de Workers
```python
# Para Gunicorn
# Procfile
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 src.main:app
```

### 2. Cache con Redis
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
})

@app.route('/api/products')
@cache.cached(timeout=300)  # 5 minutos
def get_products():
    # Lógica de productos
```

### 3. CDN para Assets
```python
# Configurar CDN para archivos estáticos
if os.environ.get('FLASK_ENV') == 'production':
    app.config['CDN_DOMAIN'] = 'https://cdn.tudominio.com'
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Puerto en Heroku
```python
# Asegúrate de usar PORT dinámico
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

#### 2. Base de Datos no Inicializada
```python
# Agregar inicialización automática
with app.app_context():
    db.create_all()
    # Crear datos de prueba si no existen
    if not User.query.first():
        create_sample_data()
```

#### 3. Assets no Cargan
```python
# Verificar rutas estáticas
app.static_folder = 'static'
app.static_url_path = '/static'
```

## ✅ Checklist de Despliegue

- [ ] Variables de entorno configuradas
- [ ] Base de datos inicializada
- [ ] HTTPS habilitado
- [ ] Logs configurados
- [ ] Health check funcionando
- [ ] Rate limiting activo
- [ ] Backup de base de datos configurado
- [ ] Monitoreo activo
- [ ] Dominio personalizado (opcional)
- [ ] SSL certificado válido

## 📞 Soporte Post-Despliegue

### Comandos Útiles

```bash
# Ver logs en Heroku
heroku logs --tail

# Ejecutar comandos en producción
heroku run python

# Reiniciar aplicación
heroku restart

# Ver métricas
heroku ps
```

### Monitoreo Recomendado
- **Uptime:** UptimeRobot, Pingdom
- **Performance:** New Relic, DataDog
- **Errors:** Sentry, Rollbar
- **Analytics:** Google Analytics, Mixpanel

¡Tu MVP de Weev está listo para conquistar el mundo! 🚀

