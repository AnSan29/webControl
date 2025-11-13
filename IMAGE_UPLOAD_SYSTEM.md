# 📤 Sistema de Upload de Imágenes

## 🎯 Nueva Funcionalidad: Subir Imágenes al Proyecto

Ahora puedes **subir imágenes directamente** desde tu computadora, además de usar URLs externas. Las imágenes se guardan en el proyecto y se publican automáticamente en GitHub Pages.

---

## ✨ Características

### 🔄 **Doble Opción**
Cada campo de imagen ahora ofrece dos opciones:
1. **📤 Subir Imagen** - Sube desde tu computadora
2. **🔗 Usar URL** - Pega una URL externa

### 💾 **Almacenamiento**
- Las imágenes se guardan en la carpeta `/uploads/` del proyecto
- Se suben automáticamente al repositorio de GitHub en `/images/`
- Se publican junto con el sitio en GitHub Pages

### ✅ **Validaciones**
- Tipos permitidos: JPG, PNG, GIF, WebP
- Tamaño máximo: **5MB**
- Nombres únicos automáticos (UUID)

---

## 🖼️ Campos con Upload

### 1. **Imagen Hero (Principal)**
```
┌────────────────────────────────┐
│   [Vista Previa de Imagen]     │
├────────────────────────────────┤
│ [📤 Subir Imagen] [🔗 Usar URL]│
│ [Input URL oculto]             │
└────────────────────────────────┘
```

### 2. **Imagen Sobre Nosotros**
```
┌────────────────────────────────┐
│   [Vista Previa de Imagen]     │
├────────────────────────────────┤
│ [📤 Subir Imagen] [🔗 Usar URL]│
│ [Input URL oculto]             │
└────────────────────────────────┘
```

### 3. **Imágenes de Productos**
Cada tarjeta de producto tiene:
```
┌─────────────────────┐
│  [Imagen Preview]   │
│      [Nombre]       │
│   [Descripción]     │
│     [Precio]        │
├─────────────────────┤
│ [📤 Subir] [🔗 URL] │
└─────────────────────┘
```

### 4. **Galería de Imágenes**
Al agregar imagen nueva:
```
Diálogo:
¿Deseas subir una imagen desde tu computadora?

OK = Subir archivo
Cancelar = Usar URL
```

---

## 🚀 Flujo de Uso

### Opción 1: Subir desde Computadora

#### Paso a Paso:
1. **Click en "📤 Subir Imagen"**
2. **Selecciona archivo** desde el explorador
3. **Espera** mientras se sube (notificación "Subiendo imagen...")
4. **Confirmación** "✅ Imagen subida exitosamente"
5. **Preview actualizado** automáticamente

#### Ejemplo: Imagen Hero
```javascript
// Usuario hace click en "📤 Subir Imagen"
→ Se abre selector de archivos
→ Usuario selecciona "logo-empresa.png"
→ Sistema valida (tipo, tamaño)
→ Sube a /api/upload-image
→ Guarda en /uploads/abc123.png
→ Retorna URL: /images/abc123.png
→ Actualiza preview
```

### Opción 2: Usar URL Externa

#### Paso a Paso:
1. **Click en "🔗 Usar URL"**
2. **Input URL aparece**
3. **Pega la URL** (ej: https://ejemplo.com/imagen.jpg)
4. **Preview actualizado** automáticamente

---

## 🏗️ Arquitectura Técnica

### Backend

#### Endpoint: `POST /api/upload-image`

**Request:**
```javascript
FormData {
    file: File (imagen),
    site_id: number (opcional)
}
```

**Response:**
```json
{
    "success": true,
    "filename": "abc123.png",
    "url": "/images/abc123.png",
    "local_path": "/path/to/uploads/abc123.png",
    "size": 245678,
    "type": "image/png"
}
```

**Validaciones:**
- Tipo de archivo (image/jpeg, image/png, etc.)
- Tamaño máximo (5MB)
- Generación de nombre único (UUID)

#### Almacenamiento Local

```
webcontrol_studio/
├── uploads/          ← Nuevas imágenes subidas
│   ├── abc123.png
│   ├── def456.jpg
│   └── ghi789.webp
```

**Características:**
- Carpeta creada automáticamente
- Montada como estática: `/uploads`
- Accesible via URL: `http://localhost:8000/uploads/filename.png`

#### Publicación en GitHub

```python
def publish_site(...):
    # 1. Subir archivos HTML/CSS
    upload_multiple_files(...)
    
    # 2. Subir imágenes locales
    for image in uploads_dir.glob("*"):
        upload_binary_file(
            repo_name=repo_name,
            file_path=f"images/{image.name}",
            file_content=image_bytes
        )
    
    # 3. Habilitar GitHub Pages
    enable_github_pages(...)
```

**En el Repositorio de GitHub:**
```
usuario/sitio-negocio/
├── index.html
├── styles.css
└── images/          ← Imágenes subidas
    ├── abc123.png
    ├── def456.jpg
    └── ghi789.webp
```

---

### Frontend

#### Componentes de Upload

**1. Input File (oculto):**
```html
<input 
    type="file" 
    id="hero_image_file" 
    accept="image/*" 
    style="display: none;" 
    onchange="uploadImage(this, 'hero_image', 'heroImagePreview')"
>
```

**2. Botones de Acción:**
```html
<button onclick="document.getElementById('hero_image_file').click()">
    📤 Subir Imagen
</button>
<button onclick="toggleUrlInput('hero')">
    🔗 Usar URL
</button>
```

**3. Input URL (oculto por defecto):**
```html
<input 
    type="url" 
    id="hero_image" 
    placeholder="O pega una URL aquí..." 
    style="display: none;"
>
```

#### Funciones JavaScript

**uploadImage(fileInput, targetInputId, previewId)**
```javascript
// Maneja upload de imágenes individuales (Hero, About)
async function uploadImage(fileInput, targetInputId, previewId) {
    const file = fileInput.files[0];
    
    // Validar
    if (!file.type.startsWith('image/')) { ... }
    if (file.size > 5MB) { ... }
    
    // Crear FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Enviar
    const response = await fetchAPI('/api/upload-image', {
        method: 'POST',
        body: formData
    });
    
    // Actualizar URL y preview
    urlInput.value = data.url;
    updateImagePreview();
}
```

**uploadProductImage(fileInput, productIndex)**
```javascript
// Maneja upload de imágenes de productos
// Similar a uploadImage pero actualiza array de productos
updateProduct(productIndex, 'image', imageUrl);
renderProducts();
```

**uploadGalleryImage(file)**
```javascript
// Maneja upload de imágenes de galería
// Agrega URL al array de galería
window.galleryData.push(imageUrl);
renderGallery();
```

---

## 📊 Ventajas del Sistema

### ✅ Para el Usuario

1. **Más Fácil**
   - No necesita subir imágenes a otro servicio
   - Todo en un solo lugar
   - Drag and drop en futuro

2. **Más Rápido**
   - Upload directo desde computadora
   - Sin copiar/pegar URLs
   - Preview inmediato

3. **Más Confiable**
   - Imágenes siempre disponibles
   - No dependen de servicios externos
   - Control total

### ✅ Para el Sistema

1. **Autocontenido**
   - Imágenes en el mismo repo
   - Sin dependencias externas
   - Backup automático (GitHub)

2. **Versionado**
   - Imágenes versionadas en Git
   - Historial de cambios
   - Rollback posible

3. **Performance**
   - GitHub Pages CDN
   - Carga rápida
   - HTTPS automático

---

## 🔒 Seguridad

### Validaciones Implementadas

**1. Tipo de Archivo**
```python
allowed_types = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp"
]
```

**2. Tamaño Máximo**
```python
max_size = 5 * 1024 * 1024  # 5MB

if file_size > max_size:
    raise HTTPException(400, "Imagen muy grande")
```

**3. Nombres Únicos**
```python
unique_filename = f"{uuid.uuid4().hex}.{extension}"
# Ejemplo: a1b2c3d4e5f6.png
```

**4. Autenticación**
```python
@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile,
    current_admin = Depends(get_current_admin)  # ← Requiere login
):
```

---

## 📁 Estructura de Archivos

### Proyecto Local

```
webcontrol_studio/
├── backend/
│   ├── main.py                    # Endpoint /api/upload-image
│   └── utils/
│       └── github_api.py          # upload_binary_file()
├── frontend/
│   ├── editor.html                # Botones y inputs de upload
│   └── static/
│       └── js/
│           └── main.js            # fetchAPI con FormData
└── uploads/                       # ← NUEVA CARPETA
    ├── a1b2c3d4.png
    ├── e5f6g7h8.jpg
    └── i9j0k1l2.webp
```

### Repositorio GitHub

```
usuario/sitio-negocio/
├── index.html
├── styles.css
└── images/                        # ← Imágenes publicadas
    ├── a1b2c3d4.png
    ├── e5f6g7h8.jpg
    └── i9j0k1l2.webp
```

### GitHub Pages (Publicado)

```
https://usuario.github.io/sitio-negocio/
├── index.html
├── styles.css
└── images/
    ├── a1b2c3d4.png              # ← URL pública
    ├── e5f6g7h8.jpg
    └── i9j0k1l2.webp
```

---

## 🎯 Casos de Uso

### Caso 1: Crear Sitio Nuevo con Imágenes Locales

**Flujo:**
1. Usuario crea sitio nuevo
2. Sube logo desde computadora (📤)
3. Sube imagen hero desde computadora (📤)
4. Sube 3 imágenes de productos (📤)
5. Sube 5 imágenes a galería (📤)
6. Guarda sitio
7. Publica en GitHub Pages
8. ✅ Todas las imágenes se suben al repo y están disponibles

### Caso 2: Mix de Imágenes Locales y URLs

**Flujo:**
1. Usuario sube logo local (📤)
2. Usa URL externa para hero (🔗 https://unsplash.com/...)
3. Sube 2 productos locales (📤)
4. Usa URL para 1 producto (🔗)
5. Galería: 3 locales + 2 URLs
6. ✅ Sistema maneja ambos tipos sin problema

### Caso 3: Actualizar Imagen Existente

**Flujo:**
1. Usuario edita sitio publicado
2. Click en producto con imagen antigua
3. Click "📤 Subir" → Selecciona nueva imagen
4. Nueva imagen reemplaza la anterior
5. Guarda y auto-sync actualiza GitHub Pages
6. ✅ Nueva imagen visible en sitio publicado

---

## 🚦 Estados y Feedback

### Durante Upload

**Notificaciones:**
```javascript
// Inicio
showNotification('Subiendo imagen...', 'info');

// Éxito
showNotification('✅ Imagen subida exitosamente', 'success');

// Error (tipo)
showNotification('Por favor selecciona una imagen válida', 'error');

// Error (tamaño)
showNotification('La imagen es muy grande. Máximo 5MB', 'error');

// Error (servidor)
showNotification('Error al subir imagen', 'error');
```

### Preview Visual

**Estados:**
1. **Sin Imagen**: Placeholder con emoji 🖼️
2. **Subiendo**: Notificación "Subiendo imagen..."
3. **Exitoso**: Preview actualizado + "✓ Imagen cargada"
4. **Error**: Mensaje de error, preview sin cambios

---

## 🔄 Integración con Sistema Existente

### Compatible con Auto-Sync

```javascript
// Al guardar, imágenes locales se incluyen automáticamente
saveSite() {
    // Serializa datos
    data.hero_image = "http://localhost:8000/uploads/abc.png"
    
    // Al publicar, github_api.py sube las imágenes
    publish_site() {
        // Sube HTML/CSS
        // Sube TODAS las imágenes de /uploads/
        // Habilita Pages
    }
}
```

### Sin Cambios en Templates

Los templates siguen usando URLs normales:
```html
<img src="{{ hero_image }}" alt="Hero">
```

Puede ser:
- `https://ejemplo.com/imagen.jpg` (URL externa)
- `/images/abc123.png` (Imagen local → relativa en GitHub)

---

## 📈 Futuras Mejoras

### V2.2 - Optimización de Imágenes
- [ ] Redimensionamiento automático
- [ ] Compresión automática
- [ ] Conversión a WebP
- [ ] Generación de thumbnails

### V2.3 - Gestión Avanzada
- [ ] Galería de imágenes subidas
- [ ] Buscar y reusar imágenes
- [ ] Eliminar imágenes no usadas
- [ ] Ver tamaño total de imágenes

### V2.4 - UX Mejorada
- [ ] Drag & drop de imágenes
- [ ] Paste desde clipboard
- [ ] Preview antes de subir
- [ ] Edición básica (crop, rotate)

### V2.5 - Múltiples Sitios
- [ ] Compartir imágenes entre sitios
- [ ] Librería global de imágenes
- [ ] Tags y categorías
- [ ] Búsqueda de imágenes

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env
GITHUB_TOKEN=ghp_xxxxx
GITHUB_USERNAME=usuario

# Opcional (futuro)
MAX_UPLOAD_SIZE=5242880  # 5MB en bytes
ALLOWED_IMAGE_TYPES=jpg,png,gif,webp
```

### Permisos de GitHub Token

El token necesita estos permisos para subir imágenes:
- ✅ `repo` (acceso completo a repositorios)
- ✅ `workflow` (actualizar actions)
- ✅ `write:packages` (subir archivos)

---

## 🐛 Troubleshooting

### Problema: "Error al subir imagen"

**Causas posibles:**
1. Tamaño mayor a 5MB
2. Tipo de archivo no permitido
3. Sin autenticación (token expirado)
4. Carpeta /uploads sin permisos

**Soluciones:**
1. Reducir tamaño de imagen
2. Convertir a JPG/PNG
3. Relogin
4. Verificar permisos de carpeta

### Problema: Imagen no aparece en sitio publicado

**Causas posibles:**
1. No se guardó antes de publicar
2. GitHub Pages aún actualizando (1-2 min)
3. Error al subir a GitHub

**Soluciones:**
1. Guardar y volver a publicar
2. Esperar 2-3 minutos
3. Verificar repositorio en GitHub

### Problema: Preview no actualiza

**Causas posibles:**
1. URL incorrecta
2. Caché del navegador
3. Error en JavaScript

**Soluciones:**
1. Verificar URL
2. Hard refresh (Ctrl+Shift+R)
3. Verificar consola de navegador

---

## ✅ Checklist de Implementación

### Backend ✅
- [x] Endpoint POST /api/upload-image
- [x] Validación de tipo de archivo
- [x] Validación de tamaño
- [x] Generación de nombres únicos
- [x] Almacenamiento en /uploads/
- [x] Montar carpeta como estática
- [x] Método upload_binary_file en github_api.py
- [x] Subir imágenes en publish_site()

### Frontend ✅
- [x] Botones "📤 Subir" y "🔗 URL"
- [x] Inputs file ocultos
- [x] Inputs URL toggleables
- [x] Función uploadImage()
- [x] Función uploadProductImage()
- [x] Función uploadGalleryImage()
- [x] Función toggleUrlInput()
- [x] Actualizar fetchAPI para FormData
- [x] Notificaciones de estado

### Integración ✅
- [x] Compatible con sistema existente
- [x] Sin breaking changes
- [x] Auto-sync funcionando
- [x] Templates sin cambios

---

## 🎊 Resultado Final

### Antes ❌
```
Usuario:
1. Abre Imgur/Cloudinary
2. Sube imagen
3. Copia URL
4. Vuelve al editor
5. Pega URL
```

### Ahora ✅
```
Usuario:
1. Click "📤 Subir Imagen"
2. Selecciona archivo
3. ✅ Listo!
```

**Reducción:** De 5 pasos a 2 pasos (60% más rápido)

---

**Versión**: 2.2 - Upload de Imágenes
**Fecha**: 13 de Noviembre 2025
**Estado**: ✅ Implementado y Funcional
