# 🛍️ Guía de Productos y Galería - WebControl Studio

## ✅ Funcionalidades Agregadas

### 1. **Gestión de Productos/Servicios**

Ahora puedes agregar productos o servicios a tu sitio web de forma estructurada.

#### Formato de Productos

Los productos se gestionan en formato JSON. Cada producto tiene:

- `name`: Nombre del producto
- `description`: Descripción breve
- `price`: Precio (texto, puedes incluir formato)
- `image`: URL de la imagen del producto

#### Ejemplo de Productos:

```json
[
  {
    "name": "Mochila Wayuu",
    "description": "Mochila artesanal tejida a mano con diseños tradicionales",
    "price": "150000",
    "image": "https://ejemplo.com/mochila.jpg"
  },
  {
    "name": "Hamaca",
    "description": "Hamaca tejida de algodón 100% natural",
    "price": "200000",
    "image": "https://ejemplo.com/hamaca.jpg"
  },
  {
    "name": "Accesorio Tejido",
    "description": "Pulsera artesanal con colores vibrantes",
    "price": "25000",
    "image": "https://ejemplo.com/pulsera.jpg"
  }
]
```

#### Cómo Agregar Productos:

1. **Método Manual**:
   - Ve al editor del sitio
   - Busca la sección "🛍️ Productos/Servicios"
   - Escribe el JSON directamente en el textarea
   - Guarda los cambios

2. **Usando el Botón de Ejemplo**:
   - Click en "➕ Agregar Producto de Ejemplo"
   - Se agregará un producto de muestra
   - Edita los valores según tu negocio
   - Agrega más productos copiando el formato

#### Visualización de Productos:

Los productos se muestran en una cuadrícula responsive:

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Imagen  │  │  Imagen  │  │  Imagen  │
│          │  │          │  │          │
│  Nombre  │  │  Nombre  │  │  Nombre  │
│ Descrip  │  │ Descrip  │  │ Descrip  │
│ $Precio  │  │ $Precio  │  │ $Precio  │
└──────────┘  └──────────┘  └──────────┘
```

Características:
- ✅ Grid adaptativo (1-3 columnas según pantalla)
- ✅ Hover effect (tarjeta se eleva)
- ✅ Imágenes con aspect ratio 4:3
- ✅ Precio destacado en color secundario

---

### 2. **Galería de Imágenes**

Sistema simple para mostrar múltiples imágenes en una galería atractiva.

#### Formato de Galería:

- Una URL por línea
- Sin comas ni formato especial
- URLs completas (https://...)

#### Ejemplo:

```
https://ejemplo.com/foto1.jpg
https://ejemplo.com/foto2.jpg
https://ejemplo.com/foto3.jpg
https://ejemplo.com/foto4.jpg
https://ejemplo.com/foto5.jpg
https://ejemplo.com/foto6.jpg
```

#### Cómo Agregar Imágenes a la Galería:

1. Ve al editor del sitio
2. Busca la sección "🖼️ Galería de Imágenes"
3. Escribe cada URL en una línea nueva
4. Guarda los cambios

#### Visualización de la Galería:

Las imágenes se muestran en un grid elegante:

```
┌───────┐ ┌───────┐ ┌───────┐
│ Img 1 │ │ Img 2 │ │ Img 3 │
└───────┘ └───────┘ └───────┘
┌───────┐ ┌───────┐ ┌───────┐
│ Img 4 │ │ Img 5 │ │ Img 6 │
└───────┘ └───────┘ └───────┘
```

Características:
- ✅ Grid responsive (adapta columnas según pantalla)
- ✅ Imágenes con aspect ratio automático
- ✅ Lazy loading (carga bajo demanda)
- ✅ Hover effect (imagen se eleva)
- ✅ Bordes redondeados
- ✅ Sombras suaves

---

## 📱 Uso Completo del Sistema

### Flujo de Trabajo Recomendado:

#### 1. Crear Sitio Nuevo

```
Login → Crear Sitio → Seleccionar Plantilla
```

#### 2. Configurar Información Básica

```
✏️ Nombre del sitio
✏️ Descripción
✏️ Título Hero
✏️ Subtítulo Hero
✏️ Imagen Hero (URL)
```

#### 3. Agregar Contenido "Sobre Nosotros"

```
✏️ Texto descriptivo
✏️ Imagen (URL)
```

#### 4. Configurar Contacto

```
📧 Email
📱 Teléfono
💬 WhatsApp (+código país)
📍 Dirección
```

#### 5. Agregar Redes Sociales

```
🔵 Facebook URL
📸 Instagram URL
🎵 TikTok URL
```

#### 6. Personalizar Colores

```
🎨 Color Primario (picker)
🎨 Color Secundario (picker)
```

#### 7. **Agregar Productos** ⭐ NUEVO

```json
[
  {
    "name": "Producto 1",
    "description": "Descripción",
    "price": "50000",
    "image": "https://..."
  }
]
```

O usar el botón "➕ Agregar Producto de Ejemplo"

#### 8. **Agregar Galería** ⭐ NUEVO

```
https://ejemplo.com/imagen1.jpg
https://ejemplo.com/imagen2.jpg
https://ejemplo.com/imagen3.jpg
```

#### 9. Guardar y Publicar

```
💾 Guardar → Auto-sincroniza si está publicado
🚀 Publicar → Primera vez activa GitHub Pages
```

---

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Tienda de Artesanías

**Productos:**
```json
[
  {
    "name": "Mochila Wayuu Grande",
    "description": "Mochila artesanal tejida a mano con diseños tradicionales de La Guajira",
    "price": "150.000 COP",
    "image": "https://i.imgur.com/mochila1.jpg"
  },
  {
    "name": "Mochila Wayuu Mediana",
    "description": "Perfecta para el día a día, colores vibrantes",
    "price": "120.000 COP",
    "image": "https://i.imgur.com/mochila2.jpg"
  },
  {
    "name": "Mochila Wayuu Pequeña",
    "description": "Ideal para niños o como bolso de mano",
    "price": "80.000 COP",
    "image": "https://i.imgur.com/mochila3.jpg"
  }
]
```

**Galería:**
```
https://i.imgur.com/proceso1.jpg
https://i.imgur.com/proceso2.jpg
https://i.imgur.com/artesana1.jpg
https://i.imgur.com/artesana2.jpg
https://i.imgur.com/tienda.jpg
```

### Ejemplo 2: Restaurante/Cocina

**Productos (Menú):**
```json
[
  {
    "name": "Friche de Chivo",
    "description": "Plato tradicional guajiro, carne de chivo guisada con especias",
    "price": "35.000 COP",
    "image": "https://i.imgur.com/friche.jpg"
  },
  {
    "name": "Arroz con Camarón",
    "description": "Arroz marinero con camarones frescos del Caribe",
    "price": "28.000 COP",
    "image": "https://i.imgur.com/arroz.jpg"
  },
  {
    "name": "Yuca Cocida",
    "description": "Acompañamiento tradicional",
    "price": "8.000 COP",
    "image": "https://i.imgur.com/yuca.jpg"
  }
]
```

**Galería:**
```
https://i.imgur.com/cocina.jpg
https://i.imgur.com/chef.jpg
https://i.imgur.com/mesa1.jpg
https://i.imgur.com/mesa2.jpg
https://i.imgur.com/local.jpg
```

### Ejemplo 3: Salón de Belleza

**Productos (Servicios):**
```json
[
  {
    "name": "Corte de Cabello Mujer",
    "description": "Incluye lavado y secado",
    "price": "25.000 COP",
    "image": "https://i.imgur.com/corte-mujer.jpg"
  },
  {
    "name": "Corte de Cabello Hombre",
    "description": "Corte moderno y clásico",
    "price": "15.000 COP",
    "image": "https://i.imgur.com/corte-hombre.jpg"
  },
  {
    "name": "Manicure y Pedicure",
    "description": "Servicio completo con esmaltado",
    "price": "30.000 COP",
    "image": "https://i.imgur.com/manicure.jpg"
  },
  {
    "name": "Tinte Completo",
    "description": "Coloración profesional",
    "price": "60.000 COP",
    "image": "https://i.imgur.com/tinte.jpg"
  }
]
```

**Galería:**
```
https://i.imgur.com/salon1.jpg
https://i.imgur.com/salon2.jpg
https://i.imgur.com/antes-despues1.jpg
https://i.imgur.com/antes-despues2.jpg
https://i.imgur.com/equipo.jpg
```

---

## 💡 Consejos y Mejores Prácticas

### Para Productos:

✅ **DO:**
- Usa imágenes de buena calidad (mínimo 800x600px)
- Mantén descripciones cortas y claras (1-2 líneas)
- Usa formato de precio consistente
- Agrega al menos 3-6 productos
- Actualiza precios regularmente

❌ **DON'T:**
- No uses imágenes muy pesadas (>500KB)
- No hagas descripciones muy largas
- No dejes campos vacíos
- No uses URLs que expiren

### Para Galería:

✅ **DO:**
- Usa imágenes horizontales o cuadradas
- Mantén calidad consistente
- Agrega al menos 6-9 imágenes
- Usa imágenes profesionales si es posible
- Muestra variedad (productos, local, equipo, proceso)

❌ **DON'T:**
- No mezcles orientaciones extremas (muy verticales con horizontales)
- No uses imágenes de baja resolución
- No sobrecargues con muchas imágenes (máx 20)
- No uses imágenes con marca de agua

### Hosting de Imágenes Recomendado:

1. **Imgur.com** (Gratis, fácil)
   - Sube imagen
   - Copia "Direct Link"
   - Pega en el campo correspondiente

2. **Cloudinary.com** (Gratis hasta 25GB)
   - Optimización automática
   - CDN rápido
   - Transformaciones on-the-fly

3. **GitHub** (Si ya usas GitHub)
   - Sube a repositorio público
   - Usa raw.githubusercontent.com URL

4. **Google Drive** (Requiere configuración)
   - Necesita hacer público el enlace
   - Formato especial de URL

---

## 🔄 Auto-Sincronización

Cuando guardas cambios en productos o galería:

1. ✅ Se guardan en la base de datos
2. 🔄 Si el sitio está publicado, se regenera automáticamente
3. 📤 Se sube a GitHub
4. ⏳ GitHub Pages actualiza (1-2 minutos)
5. ✅ Cambios visibles en tu sitio público

---

## 🆘 Solución de Problemas

### Los productos no se muestran

**Problema**: JSON mal formateado
**Solución**: 
- Verifica que tengas corchetes `[]` al inicio y fin
- Cada producto entre llaves `{}`
- Separa productos con comas
- Usa comillas dobles `"` no simples `'`

**Valida tu JSON**: https://jsonlint.com/

### Las imágenes de galería no cargan

**Problema**: URLs incorrectas o privadas
**Solución**:
- Verifica que la URL sea accesible públicamente
- Prueba abrir la URL en navegador privado
- Usa https:// no http://
- No uses URLs de Google Drive sin configurar

### Los precios se ven raros

**Problema**: Formato inconsistente
**Solución**:
- Decide un formato: `"50000"` o `"50.000 COP"` o `"$50.000"`
- Mantén el mismo formato en todos los productos
- El precio es texto, puedes usar cualquier formato

---

## 📊 Resumen de Cambios Técnicos

### Frontend (editor.html)

✅ Campo `products_json` (textarea JSON)
✅ Campo `gallery_images_input` (textarea líneas)
✅ Botón "Agregar Producto de Ejemplo"
✅ Función `addProductTemplate()`
✅ Procesamiento de galería en `saveSite()`

### Backend (main.py)

✅ Endpoint actualizado con todos los campos
✅ Procesamiento de `gallery_images`
✅ Validación de JSON

### Template Engine

✅ Contexto con `products` array
✅ Contexto con `gallery_images` array
✅ CSS para galería responsive
✅ Lazy loading de imágenes

### Plantillas

✅ Loop de productos con Jinja2
✅ Loop de galería con Jinja2
✅ Fallback si no hay contenido

---

**Estado**: ✅ Completamente implementado y funcional

**Versión**: 2.1 - Productos y Galería

**Fecha**: Noviembre 2025
