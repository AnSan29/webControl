# 🚀 Guía de Inicio Rápido - WebControl Studio

## ⚡ Iniciar en 3 Pasos

### 1️⃣ Instalar Dependencias
```bash
cd /home/mrmontero/Documentos/webcontrol_studio
pip install -r requirements.txt
```

### 2️⃣ Configurar GitHub Token (Opcional pero Recomendado)
```bash
# Crear archivo .env
echo 'SECRET_KEY=mi_clave_super_secreta_123' > .env
echo 'GITHUB_TOKEN=ghp_TU_TOKEN_AQUI' >> .env
```

**Obtener GitHub Token:**
1. Ir a https://github.com/settings/tokens
2. Generar nuevo token (classic)
3. Permisos necesarios: `repo`, `workflow`, `write:packages`

### 3️⃣ Iniciar el Sistema
```bash
# Linux/Mac
./start.sh

# O manualmente
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Acceder al Sistema

1. **Abrir navegador:** http://localhost:8000
2. **Usuario por defecto:** `admin@webcontrol.com`
3. **Contraseña por defecto:** `admin123`

## 🎨 Crear tu Primer Sitio

1. **Login** → Usa las credenciales por defecto
2. **Dashboard** → Ver estadísticas generales
3. **Modelos** → Explorar los 5 modelos disponibles
4. **Crear Sitio** → Completar formulario:
   - Nombre del negocio: "Mi Artesanías"
   - Modelo: Selecciona "artesanias"
   - Descripción: "Artesanías únicas hechas a mano"
   - Teléfono: "555-1234"
   - Email: "contacto@miartesanias.com"
   - (Opcional) Dominio personalizado: "miartesanias.com"
   - (Opcional) GitHub Repository: "miartesanias-site"

5. **Ver Resultado** → El sitio se genera automáticamente
6. **Editar** → Modifica contenido desde el panel
7. **Publicar** → Se sube a GitHub Pages automáticamente

## 📋 Checklist de Configuración

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] GitHub Token configurado (para publicación)
- [ ] Servidor iniciado y accesible
- [ ] Login exitoso en el panel
- [ ] Primer sitio creado

## 🎯 Modelos Disponibles

| Modelo | Descripción | Colores |
|--------|-------------|---------|
| 🎨 **Artesanías** | Para negocios de artesanías y productos hechos a mano | Cálidos: Naranja, Beige, Café |
| 🍳 **Cocina Doméstica** | Para negocios de comida casera y catering | Apetitosos: Rojo, Naranja, Amarillo |
| 🔧 **Adecuaciones** | Para servicios de reparación y adecuaciones | Técnicos: Azul, Verde, Naranja |
| 💇 **Belleza** | Para salones, barberías y servicios de estética | Elegantes: Morado, Dorado, Crema |
| 🐐 **Cría de Chivos** | Para negocios agropecuarios y productos naturales | Naturales: Café, Naranja, Beige |

## 🛠️ Comandos Útiles

```bash
# Ver logs del servidor
tail -f logs/app.log

# Reiniciar servidor
pkill -f uvicorn && ./start.sh

# Acceder a la base de datos
sqlite3 backend/sites.db

# Ver sitios creados
sqlite3 backend/sites.db "SELECT * FROM sites;"

# Limpiar base de datos
rm backend/sites.db
```

## 📱 Estructura de URLs

- `http://localhost:8000/` - Panel de login
- `http://localhost:8000/dashboard.html` - Dashboard principal
- `http://localhost:8000/models.html` - Ver modelos
- `http://localhost:8000/create-site.html` - Crear nuevo sitio
- `http://localhost:8000/editor.html?id=1` - Editar sitio
- `http://localhost:8000/api/sites` - API REST (JSON)

## 🔍 Solución de Problemas Comunes

### Error: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Error: "Port 8000 already in use"
```bash
# Cambiar puerto
uvicorn backend.main:app --reload --port 8001
```

### Error: "GitHub API rate limit"
```bash
# Configurar token en .env
echo 'GITHUB_TOKEN=ghp_tu_token' >> .env
```

### No aparecen las plantillas
```bash
# Verificar estructura de directorios
ls -la templates_base/
```

## 🎓 Próximos Pasos

1. ✅ Crear tu primer sitio de prueba
2. ✅ Personalizar contenido desde el editor
3. ✅ Configurar GitHub Token para publicación
4. ✅ Publicar en GitHub Pages
5. ✅ Configurar dominio personalizado (opcional)
6. ✅ Revisar estadísticas de visitas

## 📚 Documentación Adicional

- `README.md` - Información general del proyecto
- `USAGE.md` - Guía de uso detallada
- `DEPLOYMENT.md` - Guía de despliegue en producción
- `PROJECT_STATUS.md` - Estado actual del proyecto

## 💡 Tips

- **Desarrollo**: Usa `--reload` para ver cambios en tiempo real
- **Producción**: Usa Gunicorn con múltiples workers
- **Backups**: Respalda regularmente `backend/sites.db`
- **Seguridad**: Cambia las credenciales por defecto
- **Performance**: Considera usar CDN para assets estáticos

---

**¿Todo listo?** 🎉 Ejecuta `./start.sh` y visita http://localhost:8000
