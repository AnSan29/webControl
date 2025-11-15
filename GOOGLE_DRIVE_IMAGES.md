# 📸 Guía: Cargar Imágenes desde Google Drive

Este documento explica cómo configurar y usar imágenes alojadas en **Google Drive** con WebControl.

## 🔑 Requisitos Previos

Para que las imágenes de Google Drive se carguen correctamente en tu sitio web, **DEBES** seguir estos pasos:

### 1. Subir la imagen a Google Drive

1. Ve a [Google Drive](https://drive.google.com)
2. Haz clic en **"+ Nuevo"** → **"Subir archivo"** o **"Subir carpeta"**
3. Selecciona la imagen desde tu computadora

### 2. **PASO CRÍTICO: Compartir con permisos públicos**

⚠️ **ESTO ES LO MÁS IMPORTANTE**: Si no compartes la imagen correctamente, obtendrás errores **403 (Forbidden)** y la imagen NO se cargará.

#### Pasos para compartir:

1. **Click derecho en el archivo** → **"Compartir"**
   
2. En la ventana de compartir:
   - Haz clic en el botón **"Restringido"** (esquina inferior derecha)
   - En el menú que aparece, selecciona **"Cualquier persona con el enlace"**
   - En **"Rol"**, selecciona **"Lector"** ✅
   - Haz clic en **"Copiar enlace"**
   - Haz clic en **"Compartir"** o **"Cerrar"**

```
📋 Captura de pantalla mental:
┌─────────────────────────────────┐
│  Compartir                       │
├─────────────────────────────────┤
│ 🔒 Restringido ▼                │
│                                 │
│ ○ Cualquier persona con enlace  │
│ ◉ Lector                        │
│ ○ Comentador                    │
│ ○ Editor                        │
│                                 │
│ [Copiar enlace]  [Compartir]   │
└─────────────────────────────────┘
```

### 3. Copiar el enlace compartido

Después de hacer clic en **"Copiar enlace"**, tendrás algo como:

```
https://drive.google.com/file/d/1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV/view?usp=drive_link
```

O más antiguo:
```
https://drive.google.com/open?id=1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV
```

## 🎨 Usar la imagen en WebControl

### En el Panel de Administrador

1. **Logo del sitio**: Pega el enlace de Google Drive en el campo `Logo URL`
2. **Imagen del héroe**: Pega en el campo `Hero Image URL`
3. **Imagen "Sobre nosotros"**: Pega en el campo `About Image URL`
4. **Productos/servicios**: Pega en el campo de imagen de cada producto
5. **Galería**: Agrega enlaces de Drive en la galería
6. **Logos de aliados**: Pega en los campos de supporter logos

### Ejemplo de entrada:
```
Logo URL: https://drive.google.com/file/d/1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV/view?usp=drive_link
```

**WebControl automáticamente convertirá esto a:**
```
https://drive.google.com/uc?export=view&id=1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV
```

Esta es la URL directa que carga la imagen sin Google Drive interfiriendo.

## ✅ Cómo verificar que funciona

1. Después de pegar el enlace en WebControl, ve al **Editor Visual**
2. Busca el campo donde pegaste la URL
3. Verifica que la vista previa de la imagen aparezca

### Si ves una imagen rota ❌

1. Regresa a Google Drive
2. Verifica que el archivo esté compartido con **"Cualquier persona con el enlace"**
3. En caso contrario, repite los pasos de compartir

### Alternativa: Usar otra URL

Si Google Drive sigue generando problemas (errores 403), considera:

- **Google Photos**: https://photos.google.com (mejor para imágenes públicas)
- **Imgur**: https://imgur.com (rápido y confiable)
- **Cloudinary**: https://cloudinary.com (almacenamiento optimizado)
- **Un servidor propio**: Si tienes hosting

## 🚀 Cómo funciona en el backend

WebControl usa la siguiente lógica:

1. **Detección**: Identifica si la URL contiene `drive.google.com`
2. **Extracción de ID**: Obtiene el ID único del archivo
3. **Conversión**: Convierte a formato embebible: `https://drive.google.com/uc?export=view&id=<ID>`
4. **Rendering**: Inserta el `<img src="...">` en la página

```python
# Ejemplo de transformación
Input:  https://drive.google.com/file/d/ABC123/view?usp=drive_link
Output: https://drive.google.com/uc?export=view&id=ABC123
```

## 🔧 Solución de problemas

### Problema: "Image not loaded" o icono roto

**Solución**:
- ✅ Verifica que el archivo esté compartido públicamente
- ✅ Comprueba que el rol sea **"Lector"** (o "Comentador"/"Editor")
- ✅ Espera 30 segundos y recarga la página
- ✅ Prueba en una pestaña de incógnito (Ctrl+Shift+N)

### Problema: Error 403 (Forbidden)

**Causa**: Google bloqueó el acceso porque el archivo no está compartido correctamente.

**Solución**:
1. Abre Google Drive
2. Haz clic derecho en el archivo
3. Selecciona **"Compartir"**
4. Asegúrate de que esté en **"Cualquier persona con el enlace"**
5. Copia de nuevo el enlace
6. Actualiza en WebControl

### Problema: La imagen se carga pero se ve pixelada o pequeña

**Solución**:
- Usa una imagen de alta resolución (mínimo 1920x1080 para fondos)
- Para logos, usa PNG con fondo transparente (300x300px mínimo)
- Comprime la imagen si es muy grande (< 5MB recomendado)

## 📋 Checklist rápido

- [ ] ✅ Imagen subida a Google Drive
- [ ] ✅ Archivo compartido con "Cualquier persona con el enlace"
- [ ] ✅ Rol configurado como "Lector"
- [ ] ✅ Enlace copiado desde Google Drive
- [ ] ✅ Enlace pegado en WebControl
- [ ] ✅ Imagen aparece en vista previa
- [ ] ✅ Sitio publicado y imagen cargada en página en vivo

## 💡 Tips profesionales

1. **Organiza tus imágenes**: Crea una carpeta "WebControl Imágenes" en Drive
2. **Nombres descriptivos**: Usa nombres como `logo-artesanias.png` en lugar de `image123.jpg`
3. **Formato ideal**:
   - **Logos**: PNG (transparencia) o SVG
   - **Fotos**: JPG (comprimido) o WebP (moderno)
   - **Iconos**: SVG (escalable)
4. **Tamaños recomendados**:
   - Logo: 200x200px - 500x500px
   - Héroe: 1920x1080px
   - Productos: 600x600px
   - Galería: 800x600px

## 🛡️ Seguridad

- **Tus imágenes son públicas**: Cualquiera con el enlace puede verlas
- **No uses imágenes confidenciales**: No compartas documentos sensibles
- **Revoca acceso cuando sea necesario**: Si eliminas el archivo en Drive, la imagen desaparecerá del sitio

---

**¿Aún tienes problemas?** Revisa los logs de la consola del navegador (F12 → Pestaña "Console") para mensajes de error adicionales.
