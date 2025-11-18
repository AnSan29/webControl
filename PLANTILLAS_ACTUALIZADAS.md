# ✅ PLANTILLAS ACTUALIZADAS - DINÁMICAS Y UNIFICADAS

## 📋 Resumen de Cambios

Se han actualizado todas las plantillas HTML (cocina, belleza, adecuaciones, chivos) para:

1. ✅ **Usar variables dinámicas** en lugar de HTML hardcodeado
2. ✅ **Unificar el modelo de datos** con todas usando el mismo conjunto de variables
3. ✅ **Mantener diseño visual único** para cada categoría
4. ✅ **Soportar URLs externas de logo** (Google Drive, etc.)
5. ✅ **Renderizar productos, galería y contacto** desde la API

---

## 🎯 Variables Dinámicas Implementadas

### En el `<head>`:
```html
<title>{{ site_name }}</title>
<meta name="description" content="{{ site_description }}">
```

### En el Header/Logo:
```html
{% if logo_url %}
<img src="{{ logo_url }}" alt="{{ site_name }}">
{% else %}
<span>{{ model_icon }}</span>
{% endif %}
```

### En secciones principales:
```html
<h2>{{ hero_title }}</h2>
<p>{{ hero_subtitle }}</p>
<p>{{ about_text }}</p>

{% for product in products %}
  <h3>{{ product.name }}</h3>
  <p>{{ product.description }}</p>
  <span>${{ product.price }}</span>
{% endfor %}

{% for image in gallery_images %}
  <img src="{{ image }}" alt="Gallery">
{% endfor %}

<p>{{ contact_email }}</p>
<p>{{ contact_phone }}</p>
<p>{{ contact_address }}</p>
```

### En redes sociales:
```html
{% if facebook_url %}<a href="{{ facebook_url }}">{% endif %}
{% if instagram_url %}<a href="{{ instagram_url }}">{% endif %}
{% if tiktok_url %}<a href="{{ tiktok_url }}">{% endif %}
{% if whatsapp_number %}<a href="https://wa.me/{{ whatsapp_number }}">{% endif %}
```

---

## 🏠 Plantilla: COCINA (Gastronómia)

### Características:
- ✅ Sección "Menú" en lugar de "Productos"
- ✅ Énfasis en comida casera y especialidades
- ✅ Colores cálidos (dorado, rojo tomate, verde hoja)
- ✅ Iconos culinarios (🍳 🥘 🍲)

### Cambios clave:
- Reemplaza "Nuestros Productos" con "Nuestro Menú"
- Usa "Especialidades de la casa" como subtítulo
- Renderiza `products` como items de menú con precio
- Galería de "Platos" en lugar de productos genéricos
- Botón WhatsApp: "Hacer una orden"

---

## 💇 Plantilla: BELLEZA

### Características:
- ✅ Sección "Servicios" con énfasis en tratamientos
- ✅ Portafolio visual (galería con overlay)
- ✅ Diseño elegante y moderno
- ✅ Paleta de colores sofisticada (rosa, morado, dorado)

### Cambios clave:
- Reemplaza "Productos" con "Servicios"
- Tarjetas de servicio con imagen, descripción y precio
- Galería llamada "Portafolio"
- Botón WhatsApp: "Agendar una cita"
- Énfasis en redes sociales para portafolio

---

## 🔧 Plantilla: ADECUACIONES

### Características:
- ✅ Sección "Servicios" técnicos
- ✅ Galería de "Proyectos" (antes/después)
- ✅ Diseño profesional y confiable
- ✅ Colores técnicos (azul, verde, amarillo)

### Cambios clave:
- Reemplaza "Productos" con "Servicios"
- Sección "Proyectos" para mostrar trabajos realizados
- Énfasis en experiencia y confiabilidad
- Botón WhatsApp: "Solicitar presupuesto"
- Formato de tarjetas de servicio con precio "Desde $X"

---

## 🐐 Plantilla: CHIVOS

### Características:
- ✅ Sección "Catálogo" de animales/productos
- ✅ Galería de animales y faena
- ✅ Diseño rústico y natural
- ✅ Colores tierra (marrón, dorado, verde)

### Cambios clave:
- Reemplaza "Productos" con "Catálogo"
- Items muestran nombre del animal/producto, características y valor
- Galería llamada "Galería" con énfasis en animales
- Botón WhatsApp: "Información sobre los animales"
- Iconos rurales (🐐 🐑 🌾 🏞️)

---

## 🔄 Flujo de Datos Actual

```
Usuario en formulario (create-site-windster.html)
    ↓
Envía JSON con:
  - name, description, hero_title, hero_subtitle
  - about_text, contact_email, contact_phone
  - whatsapp_number, facebook_url, instagram_url, tiktok_url
  - logo_url (URL completa de Google Drive o externa)
  - primary_color, secondary_color
  - products: [{name, description, price, image}]
  - gallery_images: ["url1", "url2", ...]
    ↓
Backend: POST /api/sites
  ↓
Template Engine renderiza con contexto:
  ↓
Plantilla (cocina/belleza/adecuaciones/chivos/artesanias)
  - Lee variables dinámicas
  - Renderiza HTML completo
  - Soporta URLs externas para imágenes
    ↓
Genera: index.html, styles.css, tracking.js
    ↓
GitHub Publisher sube a repositorio
    ↓
GitHub Pages publica el sitio en línea
```

---

## 🧪 Cómo Probar

### 1. Crear un sitio desde el formulario:
```
1. Ir a: http://localhost:8000/create-site
2. Seleccionar modelo: "Cocina" (o cualquier otro)
3. Llenar formulario completo:
   - Nombre del negocio
   - Título del hero
   - Subtítulo
   - Texto de "Sobre nosotros"
   - Datos de contacto
   - URL del logo (ej: URL de Google Drive)
   - Agregar productos
   - Agregar imágenes de galería
4. Crear sitio
```

### 2. Verificar renderizado:
```
1. Ir a: http://localhost:8000/editor/{site_id}
2. Verificar que todos los datos aparezcan correctamente
3. Publicar en GitHub
4. Esperar 1-3 minutos
5. Visitar la URL publicada
```

### 3. Probar logo con URL externa:
```
- Usar URL de Google Drive con formato:
  https://drive.google.com/uc?id=TU_FILE_ID
  
- O cualquier otra URL pública de imagen

- El logo debe aparecer en el header de la página publicada
```

---

## ✅ Checklist de Verificación

- [x] Cocina: plantilla con variables dinámicas
- [x] Belleza: plantilla con variables dinámicas
- [x] Adecuaciones: plantilla con variables dinámicas
- [x] Chivos: plantilla con variables dinámicas
- [x] Logo_url soporta URLs externas
- [x] Products se renderizan desde la API
- [x] Gallery_images se renderizan desde la API
- [x] Contacto se renderiza desde la API
- [x] Redes sociales se renderizan dinámicamente
- [x] WhatsApp floating button con número dinámico

---

## 📝 Cambios Implementados

### Archivos Modificados:
- ✅ `templates_base/cocina/index.html` - Completamente reescrita
- ✅ `templates_base/belleza/index.html` - Completamente reescrita
- ✅ `templates_base/adecuaciones/index.html` - Completamente reescrita
- ✅ `templates_base/chivos/index.html` - Completamente reescrita
- ✅ `templates_base/artesanias/index.html` - Sin cambios (ya era correcta)

### Archivos Respaldados:
- `templates_base/cocina/index_old.html`
- `templates_base/belleza/index_old.html`
- `templates_base/adecuaciones/index_old.html`
- `templates_base/chivos/index_old.html`

---

## 🚀 Próximos Pasos

1. [ ] Hacer commit de los cambios
2. [ ] Hacer push a GitHub
3. [ ] Probar creación de sitios desde el formulario
4. [ ] Verificar que logo con URLs externas funcione
5. [ ] Publicar un sitio en GitHub Pages
6. [ ] Verificar que el sitio publicado tenga todos los datos correctos

---

## 💡 Beneficios

✅ **Unificación**: Todas las plantillas usan el mismo modelo de datos
✅ **Flexibilidad**: Cada plantilla puede tener su propio diseño visual
✅ **Dinamismo**: Los datos se cargan desde la API, no son hardcodeados
✅ **Logo externo**: Soporta URLs de Google Drive y otros servicios
✅ **Escalabilidad**: Agregar nuevas plantillas es ahora más simple
✅ **Mantenimiento**: Un solo conjunto de variables en el backend

---
