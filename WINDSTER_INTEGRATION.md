# Integración con Windster Template

## 📋 Descripción

WebControl Studio ahora utiliza la plantilla **Windster v1.1.0** (Tailwind CSS Dashboard) para proporcionar una interfaz de usuario moderna, responsive y profesional.

## 🎨 Características de Windster

- **Tailwind CSS 3.x**: Framework CSS utility-first
- **Responsive Design**: Totalmente adaptable a móviles, tablets y desktop
- **Componentes Modernos**: Sidebar, Navbar, Cards, Tables, Forms
- **Font Awesome Icons**: Iconos profesionales integrados
- **Animaciones Suaves**: Transiciones y efectos visuales

## 📁 Estructura de Archivos

### Archivos Windster Nuevos

```
frontend/
├── dashboard-windster.html      # Dashboard principal (Windster)
├── create-site-windster.html    # Asistente guiado para nuevos sitios
├── models-windster.html         # Biblioteca completa de modelos
└── login-windster.html          # Login moderno Tailwind
```

### Archivos Originales (Mantenidos)

```
frontend/
├── dashboard.html               # Dashboard original
├── create-site.html             # Crear sitio original
├── editor.html                  # Editor visual (rediseñado con Windster)
├── models.html                  # Modelos original
└── login.html                   # Login original
```

## 🚀 Componentes Implementados

### 1. **Navbar** (Barra de navegación superior)
- Logo de la aplicación
- Menú de usuario con dropdown
- Responsive burger menu para móviles
- Fixed position para scroll

### 2. **Sidebar** (Barra lateral de navegación)
- Navegación principal
- Enlaces a secciones
- Links a GitHub y documentación
- Colapsa en móviles

### 3. **Dashboard Stats Cards**
- Total de sitios
- Sitios publicados
- Sitios en borrador
- Total de visitas

### 4. **Data Tables**
- Tabla de sitios con información completa
- Acciones inline (Editar, Ver, Eliminar)
- Badges de estado
- Iconos por tipo de modelo

### 5. **Empty States**
- Mensaje cuando no hay sitios
- Call-to-action para crear primer sitio
- Diseño centrado y atractivo

## 🎯 Integración con el Backend

Los archivos Windster están completamente integrados con el backend de FastAPI:

```javascript
const API_URL = 'http://localhost:8000/api';

// Endpoints utilizados:
- GET /api/me                  // Info del usuario
- GET /api/dashboard/stats     // Estadísticas
- GET /api/sites               // Lista de sitios
- DELETE /api/sites/{id}       // Eliminar sitio
- POST /api/sites              // Crear sitio
- PUT /api/sites/{id}          // Actualizar sitio
- POST /api/sites/{id}/publish // Publicar sitio
```

## 🔧 Personalización

### Colores Principales

Windster usa Tailwind CSS con colores personalizables:

```javascript
// En el <script> de configuración de Tailwind:
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    "50":"#eff6ff",
                    "100":"#dbeafe",
                    "200":"#bfdbfe",
                    "300":"#93c5fd",
                    "400":"#60a5fa",
                    "500":"#3b82f6",  // Azul principal
                    "600":"#2563eb",
                    "700":"#1d4ed8",
                    "800":"#1e40af",
                    "900":"#1e3a8a"
                }
            }
        }
    }
}
```

### Iconos por Modelo

```javascript
const modelIcons = {
    'artesanias': 'palette',     // 🎨
    'cocina': 'utensils',        // 🍴
    'belleza': 'cut',            // ✂️
    'adecuaciones': 'tools',     // 🔧
    'chivos': 'paw'              // 🐾
};
```

## 📱 Responsive Breakpoints

Windster utiliza los breakpoints estándar de Tailwind:

- **sm**: 640px  (móvil grande)
- **md**: 768px  (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (desktop grande)
- **2xl**: 1536px (desktop extra grande)

## 🔐 Autenticación

Todos los archivos Windster incluyen validación de token:

```javascript
let token = localStorage.getItem('token');

if (!token) {
    window.location.href = '/login-windster.html';
}
```

## 🎭 Animaciones

Las páginas incluyen animaciones suaves:

```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.3s ease-in;
}
```

## 📦 Dependencias CDN

- **Tailwind CSS**: `https://cdn.tailwindcss.com`
- **Font Awesome**: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`

## 🔄 Migración de Archivos Antiguos

Para migrar completamente a Windster:

1. **Actualizar rutas en backend** (main.py):
```python
@app.get("/dashboard")
async def dashboard_page():
    return FileResponse("frontend/dashboard-windster.html")
```

2. **Renombrar archivos**:
```bash
mv dashboard-windster.html dashboard.html
mv create-site-windster.html create-site.html
# ... etc
```

3. **Actualizar enlaces internos** en los archivos HTML

## 🎨 Personalizar Tema

Para cambiar el color principal de azul a otro:

1. Buscar todas las ocurrencias de `blue-` en los archivos
2. Reemplazar por otro color de Tailwind: `red-`, `green-`, `purple-`, etc.
3. O definir colores custom en `tailwind.config`

## 📄 Páginas Disponibles

| Página | Archivo | Descripción |
|--------|---------|-------------|
| Dashboard | `dashboard-windster.html` | Vista principal con estadísticas y lista de sitios |
| Crear Sitio | `create-site-windster.html` | Formulario para crear nuevo sitio |
| Editor | `editor-windster.html` | Editor completo del sitio |
| Modelos | `models-windster.html` | Catálogo de plantillas disponibles |
| Login | `login-windster.html` | Página de inicio de sesión |

## 🚀 Próximos Pasos

1. ✅ Dashboard completo
2. ⏳ Crear sitio con wizard
3. ⏳ Editor con preview en tiempo real
4. ⏳ Galería de modelos
5. ⏳ Login/Registro

## 📚 Recursos

- [Windster Template](https://themesberg.com/product/tailwind-css/windster-admin-dashboard)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Font Awesome Icons](https://fontawesome.com/icons)

---

**Nota**: Los archivos originales se mantienen para compatibilidad. Puedes eliminarlos una vez completada la migración.
