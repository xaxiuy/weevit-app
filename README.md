# Weev MVP - Plataforma de Activación de Productos

## 🎉 ¡MVP Completado y Funcional!

**Weev MVP** es una aplicación web completa desarrollada en Flask que permite a los consumidores "activar" productos para obtener beneficios personalizados, mientras proporciona a las marcas datos valiosos sobre el consumo real.

## 🌐 **Acceso Público**

**URL de Prueba:** https://5000-igt2wyl7p4waiavavfie5-d415a8de.manusvm.computer

## ✨ **Funcionalidades Implementadas**

### **Para Consumidores:**
- ✅ Registro y autenticación completa
- ✅ Dashboard personalizado con métricas
- ✅ Sistema "Weev It" para activar productos
- ✅ Sistema de puntos y niveles gamificado
- ✅ Gestión de recompensas disponibles
- ✅ Historial de activaciones
- ✅ Interfaz responsive y moderna

### **Para Marcas:**
- ✅ Dashboard de administración
- ✅ Gestión completa de productos
- ✅ Analytics en tiempo real
- ✅ Seguimiento de activaciones
- ✅ Sistema de códigos de activación
- ✅ Métricas de engagement

### **Características Técnicas:**
- ✅ API RESTful completa
- ✅ Base de datos SQLite con modelos optimizados
- ✅ Autenticación con sesiones seguras
- ✅ Validaciones de seguridad
- ✅ CORS habilitado
- ✅ Interfaz moderna con CSS/JavaScript
- ✅ Responsive design

## 🚀 **Cómo Probar el MVP**

### **1. Registro de Usuario**
1. Visita: https://5000-igt2wyl7p4waiavavfie5-d415a8de.manusvm.computer
2. Haz clic en "Registrarse"
3. Completa el formulario:
   - **Nombre:** Tu nombre
   - **Email:** tu@email.com
   - **Contraseña:** Mínimo 8 caracteres con mayúscula, minúscula, número y símbolo
   - **Tipo:** Selecciona "Consumidor" o "Administrador de Marca"

### **2. Activar Productos (Consumidores)**
1. Una vez registrado, verás tu dashboard
2. En la sección "Weev It", ingresa uno de estos códigos de prueba:
   - `WEEV-PREMIUM` - Producto Premium (10 puntos)
   - `WEEV-BASIC` - Producto Básico (5 puntos)
   - `WEEV-DELUXE` - Producto Deluxe (15 puntos)
3. Haz clic en "Activar"
4. ¡Verás tus puntos aumentar y recompensas desbloqueadas!

### **3. Reclamar Recompensas**
1. Desplázate hacia abajo en tu dashboard
2. En "Recompensas Disponibles" verás las recompensas obtenidas
3. Haz clic en "Reclamar" para usar tus recompensas

### **4. Dashboard de Marca**
1. Regístrate como "Administrador de Marca"
2. Accede al dashboard de marca con métricas completas
3. Crea nuevos productos con códigos de activación
4. Monitorea activaciones en tiempo real

## 🛠 **Instalación Local**

### **Prerrequisitos**
- Python 3.11+
- pip

### **Pasos de Instalación**
```bash
# Clonar el proyecto
cd /home/ubuntu/weev_mvp/weev_app

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python src/main.py
```

La aplicación estará disponible en: http://localhost:5000

## 📊 **Estructura del Proyecto**

```
weev_app/
├── src/
│   ├── main.py              # Punto de entrada principal
│   ├── models/
│   │   └── user.py          # Modelos de base de datos
│   ├── routes/
│   │   ├── auth.py          # Rutas de autenticación
│   │   ├── products.py      # Gestión de productos
│   │   ├── rewards.py       # Sistema de recompensas
│   │   └── dashboard.py     # Dashboards y analytics
│   ├── static/
│   │   ├── index.html       # Interfaz principal
│   │   ├── styles.css       # Estilos CSS
│   │   └── script.js        # Lógica JavaScript
│   └── database/
│       └── app.db           # Base de datos SQLite
├── venv/                    # Entorno virtual
└── requirements.txt         # Dependencias
```

## 🔧 **APIs Disponibles**

### **Autenticación**
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/check-auth` - Verificar autenticación
- `GET /api/auth/me` - Obtener usuario actual

### **Productos**
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto (marcas)
- `GET /api/products/{id}` - Obtener producto específico

### **Activaciones**
- `POST /api/activate` - Activar producto con código
- `GET /api/my-activations` - Historial de activaciones

### **Recompensas**
- `GET /api/my-rewards` - Recompensas del usuario
- `POST /api/claim/{id}` - Reclamar recompensa

### **Dashboards**
- `GET /api/user-dashboard` - Métricas de consumidor
- `GET /api/brand-dashboard` - Analytics de marca

### **Utilidades**
- `GET /api/health` - Estado de la API

## 🎯 **Datos de Prueba Incluidos**

### **Usuarios Precargados:**
- **Consumidor:** usuario@test.com / password123
- **Marca:** marca@test.com / password123

### **Productos de Prueba:**
- **Producto Premium** (Código: WEEV-PREMIUM) - 10 puntos
- **Producto Básico** (Código: WEEV-BASIC) - 5 puntos  
- **Producto Deluxe** (Código: WEEV-DELUXE) - 15 puntos

### **Recompensas Automáticas:**
- Descuentos por activaciones
- Puntos bonus por productos premium
- Recompensas por niveles alcanzados

## 🚀 **Despliegue en Producción**

### **Opciones Recomendadas:**

1. **Heroku** (Gratuito)
   ```bash
   # Instalar Heroku CLI
   # Crear app: heroku create weev-mvp
   # Deploy: git push heroku main
   ```

2. **Railway** (Moderno)
   ```bash
   # Conectar repositorio GitHub
   # Deploy automático desde main branch
   ```

3. **Render** (Confiable)
   ```bash
   # Crear Web Service desde GitHub
   # Build: pip install -r requirements.txt
   # Start: python src/main.py
   ```

### **Variables de Entorno para Producción:**
```bash
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_URL=sqlite:///database/app.db
```

## 🔒 **Seguridad Implementada**

- ✅ Validación de contraseñas seguras
- ✅ Hash de contraseñas con bcrypt
- ✅ Sesiones seguras con Flask-Session
- ✅ Validación de entrada en todas las APIs
- ✅ Protección CSRF
- ✅ Sanitización de datos
- ✅ Rate limiting básico

## 📈 **Métricas y Analytics**

### **Para Consumidores:**
- Puntos totales acumulados
- Nivel actual en el sistema
- Total de activaciones realizadas
- Recompensas disponibles y reclamadas

### **Para Marcas:**
- Total de productos creados
- Productos activos vs inactivos
- Total de activaciones por producto
- Usuarios únicos que activaron productos
- Tendencias de activación por fecha

## 🎨 **Diseño y UX**

- **Paleta de colores:** Azul primario (#6366f1) con acentos dorados
- **Tipografía:** Segoe UI, moderna y legible
- **Responsive:** Optimizado para móvil y desktop
- **Animaciones:** Transiciones suaves y feedback visual
- **Accesibilidad:** Contraste adecuado y navegación por teclado

## 🔄 **Próximas Mejoras Sugeridas**

### **Corto Plazo:**
- [ ] Notificaciones push
- [ ] Integración con códigos QR
- [ ] Marketplace de recompensas
- [ ] Sistema de referidos

### **Mediano Plazo:**
- [ ] App móvil nativa
- [ ] Integración con redes sociales
- [ ] Analytics avanzados
- [ ] Sistema de niveles más complejo

### **Largo Plazo:**
- [ ] IA para recomendaciones personalizadas
- [ ] Blockchain para verificación de productos
- [ ] Integración con e-commerce
- [ ] Expansión internacional

## 📞 **Soporte y Contacto**

Para soporte técnico o consultas sobre el MVP:
- **Desarrollado por:** Manus AI
- **Tecnología:** Flask + SQLite + HTML/CSS/JS
- **Versión:** 1.0.0 MVP
- **Fecha:** Julio 2025

## 🏆 **Estado del Proyecto**

**✅ COMPLETADO Y FUNCIONAL**

El MVP de Weev está completamente desarrollado, probado y desplegado. Todas las funcionalidades core están implementadas y funcionando correctamente. La aplicación está lista para ser utilizada por usuarios reales y puede servir como base para el desarrollo futuro de la plataforma completa.

**¡Prueba el MVP ahora en:** https://5000-igt2wyl7p4waiavavfie5-d415a8de.manusvm.computer **!**

