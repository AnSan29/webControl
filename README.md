# 🎨 WebControl Studio

Sistema profesional de gestión y creación de sitios web estáticos con publicación automática en GitHub Pages. Diseñado para usuarios no técnicos con una interfaz visual intuitiva.

## ✨ Características Destacadas

### 🎯 **Editor Visual Profesional**
- **Tarjetas editables** para productos/servicios con preview de imágenes
- **Galería visual** de imágenes con gestión drag-and-drop style
- **Selectores de color** con vista previa en tiempo real
- **Preview de imágenes** para Hero y About sections
- **Interface intuitiva** sin necesidad de conocimientos técnicos

### 🏪 **5 Modelos de Negocio Predefinidos**
- 🧶 Artesanías y tejidos
- 🍳 Cocina doméstica y gastronomía
- 🔧 Adecuaciones e instalaciones
- 💇 Belleza y estética
- 🐐 Cría y comercialización de chivos

### 🎨 **Personalización Total**
- Colores primarios y secundarios personalizables
- Productos/servicios con imágenes y precios
- Galería de imágenes ilimitada
- Logo y dominio personalizado
- Redes sociales (Facebook, Instagram, TikTok)
- Botón flotante de WhatsApp

### 📊 **Analytics & Gestión**
- Estadísticas de visitas con gráficas
- Dashboard intuitivo
- Auto-sincronización con GitHub Pages
- Historial de cambios

### 🚀 **Publicación Automática**
- Integración directa con GitHub Pages
- Configuración automática de repositorio
- HTTPS por defecto
- Propagación automática (1-2 minutos)

## 🏗️ Estructura del Proyecto

```
webcontrol_studio/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLite models
│   ├── auth.py              # JWT Authentication
│   ├── models.json          # Business models config
│   └── utils/
│       ├── github_api.py    # GitHub Pages integration
│       └── template_engine.py # Dynamic HTML/CSS generation
├── frontend/
│   ├── login-windster.html  # Login moderno (por defecto)
│   ├── dashboard-windster.html # Dashboard profesional con Windster
│   ├── models-windster.html # Catálogo de plantillas
│   ├── create-site-windster.html # Asistente guiado de creación
│   ├── editor.html          # Editor visual ⭐ NUEVO (rediseñado)
│   ├── login.html           # Versión clásica (legacy)
│   ├── dashboard.html       # Dashboard original (legacy)
│   └── static/
│       ├── css/
│       │   └── main.css     # Estilos profesionales
│       └── js/
│           └── main.js      # Lógica del cliente
├── templates_base/
│   ├── artesanias/          # Template artesanías
│   ├── cocina/              # Template cocina
│   ├── adecuaciones/        # Template adecuaciones
│   ├── belleza/             # Template belleza
│   └── chivos/              # Template chivos
├── db.sqlite3               # Base de datos SQLite
├── requirements.txt         # Dependencias Python
└── Documentation/
    ├── UI_UX_IMPROVEMENTS.md    # Mejoras de interfaz ⭐ NUEVO
    ├── PRODUCTOS_Y_GALERIA.md   # Guía de productos
    └── API_EXAMPLES.md          # Ejemplos de API
```
└── .env
```

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/control-sitios.git
cd control-sitios
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-aqui
GITHUB_TOKEN=ghp_tuTokenDeGitHub
GITHUB_USERNAME=tu-usuario-github
ADMIN_EMAIL=admin@webcontrol.com
ADMIN_PASSWORD=admin123
DATABASE_URL=sqlite:///./backend/db.sqlite3
```

### 5. Inicializar la base de datos

```bash
cd backend
python -c "from database import init_db; init_db()"
```

## 🚀 Uso

### Ejecutar el servidor

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El panel estará disponible en: `http://localhost:8000`

### Credenciales por defecto

- **Email**: admin@webcontrol.com
- **Password**: admin123

⚠️ **Importante**: Cambia estas credenciales en producción.

## 🖼️ Imágenes alojadas en Google Drive

Puedes seguir usando enlaces de Google Drive para logos, galerías y aliados, pero asegúrate de cumplir estas reglas:

1. **Comparte el archivo como “Cualquier persona con el enlace” (lector)** desde Google Drive para evitar respuestas 403.
2. Copia el vínculo público (`https://drive.google.com/file/d/<ID>/view?...` o `...open?id=<ID>`). No es necesario editarlo manualmente.
3. Pega el enlace en el panel. El backend llama al helper `normalize_drive_image` para convertirlo automáticamente a `https://drive.google.com/uc?export=view&id=<ID>` y así usarlo en `<img>`.

> Si Google sigue bloqueando la carga (algunos tenants aplican políticas estrictas de cookies), habilitamos el helper `drive_preview_iframe` que genera un `<iframe src="https://drive.google.com/file/d/<ID>/preview">` como último recurso.

```jinja2
{# Ejemplo opcional dentro de una plantilla #}
{{ drive_preview_iframe(logo_url, max_width="180px", height="180px") }}
```

Google recomienda hospedar recursos estáticos (logos, banners) en servicios especializados como Cloudinary, Azure Blob Storage, GitHub Releases o un bucket S3 cuando se necesite máxima disponibilidad.

## 🎨 Modelos de Negocio y Paletas

| Modelo | Colores | Concepto |
|--------|---------|----------|
| **Artesanías** | `#C46B29, #E7B77D, #F1E4C6, #D2A679` | Cálido, cultural, artesanal |
| **Cocina/Alimentos** | `#D62828, #F77F00, #FCBF49, #EAE2B7` | Casero, apetitoso, hogareño |
| **Adecuaciones** | `#264653, #2A9D8F, #E9C46A, #F4A261` | Técnico, práctico, confiable |
| **Belleza/Barbería** | `#2E294E, #541388, #F1E9DA, #FFD400` | Elegante, moderno, sofisticado |
| **Cría de Chivos** | `#8D5524, #C68642, #E0AC69, #F1C27D` | Natural, rústico, auténtico |

## 📝 Flujo de Trabajo

1. **Login** → Accede al panel con tus credenciales
2. **Dashboard** → Visualiza métricas y sitios activos
3. **Crear Sitio** → Selecciona modelo, ingresa datos básicos
4. **Editar** → Personaliza contenido desde el editor visual
5. **Publicar** → El sistema genera y sube automáticamente a GitHub Pages
6. **Estadísticas** → Monitorea visitas y métricas

## 🔧 Configuración de GitHub Pages

### 1. Crear Token de GitHub

1. Ve a GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Selecciona permisos: `repo`, `workflow`
4. Copia el token y agrégalo a `.env`

### 2. Configurar Repositorio

Cada sitio generado se puede:
- Subir a un repositorio individual
- O usar subcarpetas en un repo central

El sistema configura automáticamente:
- Branch `gh-pages`
- Archivo `CNAME` (si se especifica dominio)
- GitHub Pages habilitado

## 📊 API Endpoints

### Autenticación
- `POST /api/login` - Login de administrador
- `POST /api/logout` - Cerrar sesión

### Sitios
- `GET /api/sites` - Listar todos los sitios
- `POST /api/sites` - Crear nuevo sitio
- `GET /api/sites/{id}` - Obtener sitio específico
- `PUT /api/sites/{id}` - Actualizar sitio
- `DELETE /api/sites/{id}` - Eliminar sitio
- `POST /api/sites/{id}/publish` - Publicar a GitHub Pages

### Modelos
- `GET /api/models` - Listar modelos de negocio

### Estadísticas
- `GET /api/stats/{site_id}` - Estadísticas de un sitio
- `POST /api/stats/{site_id}/visit` - Registrar visita

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI, SQLite, PyGithub
- **Frontend**: HTML5, TailwindCSS, Chart.js, Vanilla JS
- **Template Engine**: Jinja2
- **Hosting**: GitHub Pages
- **Analytics**: Sistema propio simple

## 📄 Licencia

MIT License

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para dudas o problemas, abre un issue en GitHub.

---

**Desarrollado con ❤️ para emprendedores y pequeños negocios**
