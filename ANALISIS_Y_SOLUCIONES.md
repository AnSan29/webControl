# 📋 ANÁLISIS Y SOLUCIONES - WebControl FastAPI

## 🎯 RESUMEN EJECUTIVO

Tu proyecto tiene un **modelo de datos centralizado y unificado** que SÍ funciona. El problema es que **las plantillas HTML de cocina, belleza, adecuaciones y chivos tienen estructuras diferentes** y no usan los mismos nombres de variables que el formulario envía.

### ✅ Lo que SÍ funciona:
- **Modelo de datos**: `Site` en `database.py` tiene todos los campos necesarios
- **API de creación**: `/api/sites` recibe los datos correctamente
- **Template Engine**: `TemplateEngine` renderiza plantillas con el contexto correcto
- **Plantilla de artesanías**: Usa las variables correctas (logo_url, hero_title, about_text, etc.)

### ❌ Lo que NO funciona:
- **Plantillas cocina, belleza, adecuaciones y chivos**: Tienen HTML hardcodeado o usan variables con nombres diferentes
- **Logo por URL**: Las plantillas no renderizaban bien las URLs externas (pero artesanías SÍ lo hace correctamente)
- **Variables inconsistentes**: Las plantillas usan nombres como `site_name` cuando deberían usar variables del contexto

---

## 🔍 ANÁLISIS DETALLADO

### 1. CÓMO FUNCIONA ARTESANÍAS (La que SÍ funciona)

#### Flujo de datos:
```
Usuario llena formulario en create-site-windster.html
    ↓
POST /api/sites (datos JSON)
    ↓
Backend crea objeto Site en BD con campos:
  - name, description, hero_title, hero_subtitle
  - about_text, about_image
  - contact_email, contact_phone, contact_address
  - whatsapp_number, facebook_url, instagram_url, tiktok_url
  - logo_url, primary_color, secondary_color
  - products_json, gallery_images
    ↓
PublishSite: POST /api/sites/{site_id}/publish
    ↓
Template Engine genera HTML:
  - Carga templates_base/artesanias/index.html
  - Renderiza con contexto (variables del Site)
  - Genera index.html, styles.css, tracking.js
    ↓
GitHub Publisher sube archivos al repo
    ↓
GitHub Pages publica el sitio
```

#### Variables que el formulario envía (en `data`):
```javascript
{
  model_type: "artesanias",
  name: "Artesanías La Tradición",
  description: "Descripción...",
  custom_domain: "",
  hero_title: "Titulo del Hero",
  hero_subtitle: "Subtítulo",
  hero_image: "URL o path",
  about_text: "Sobre nosotros...",
  about_image: "URL",
  contact_email: "email@example.com",
  contact_phone: "1234567890",
  contact_address: "Dirección",
  whatsapp_number: "+57...",
  facebook_url: "https://...",
  instagram_url: "https://...",
  tiktok_url: "https://...",
  logo_url: "https://drive.google.com/... o URL externa",
  primary_color: "#C46B29",
  secondary_color: "#E7B77D",
  gallery_images: ["URL1", "URL2", "URL3"],
  products: [
    { name: "Producto 1", description: "...", price: "100", image: "URL" }
  ]
}
```

#### Contexto en TemplateEngine:
```python
context = {
    "site_name": site_data.get("name"),
    "site_description": site_data.get("description"),
    "hero_title": site_data.get("hero_title"),
    "hero_subtitle": site_data.get("hero_subtitle"),
    "hero_image": site_data.get("hero_image"),
    "about_text": site_data.get("about_text"),
    "about_image": site_data.get("about_image"),
    "contact_email": site_data.get("contact_email"),
    "contact_phone": site_data.get("contact_phone"),
    "contact_address": site_data.get("contact_address"),
    "whatsapp_number": site_data.get("whatsapp_number"),
    "facebook_url": site_data.get("facebook_url"),
    "instagram_url": site_data.get("instagram_url"),
    "tiktok_url": site_data.get("tiktok_url"),
    "logo_url": site_data.get("logo_url"),  # ← IMPORTANTE: URL completa sin modificar
    "primary_color": site_data.get("primary_color"),
    "secondary_color": site_data.get("secondary_color"),
    "palette": model_config["palette"],
    "model_icon": model_config["icon"],
    "products": json.loads(site_data.get("products_json", "[]")),
    "gallery_images": json.loads(site_data.get("gallery_images", "[]")),
    "current_year": 2025
}
```

#### Plantilla de artesanías (CORRECTA):
```html
<!-- Header con logo -->
<div class="logo">
    {% if logo_url %}
    <img src="{{ logo_url }}" alt="{{ site_name }}">
    {% else %}
    <span class="icon">{{ model_icon }}</span>
    {% endif %}
    <h1>{{ site_name }}</h1>
</div>
```

**¿Por qué funciona?**
- ✅ `logo_url` es una variable en el contexto
- ✅ Usa `<img src="{{ logo_url }}">` directamente (soporta URLs externas)
- ✅ `site_name` está en el contexto
- ✅ Condicional `{% if logo_url %}` maneja URLs vacías

---

### 2. POR QUÉ NO FUNCIONAN LAS OTRAS PLANTILLAS

#### Problema 1: HTML hardcodeado
Cocina, belleza, adecuaciones y chivos tienen:
```html
<title>Sabores Guajiros | Tradición y Sabor de La Guajira</title>
<!-- ↑ HARDCODEADO, no usa {{ site_name }} -->
```

#### Problema 2: Variables con nombres diferentes
```html
<!-- COCINA usa: -->
<h1 class="site-title">{{ titulo }}</h1>
<!-- ↑ Pero el formulario envía: hero_title, name, site_name -->

<!-- BELLEZA usa: -->
<span class="business-name">Acera - Salón de Belleza</span>
<!-- ↑ También HARDCODEADO -->
```

#### Problema 3: Estructura completamente diferente
Cocina tiene secciones como "Menu" en lugar de "Products"
Belleza tiene "Services" en lugar de "Products"
Adecuaciones tiene "Projects" en lugar de "Products"

#### Problema 4: Logo no se renderiza correctamente
Algunas plantillas esperan rutas locales `/images/...` en lugar de URLs completas

---

## ✅ SOLUCIONES

### PASO 1: Unificar la estructura de datos (YA HECHO)

Tu `Site` model ya tiene todo lo necesario:
```python
class Site(Base):
    # Campos que envía el formulario ✅
    name
    hero_title, hero_subtitle, hero_image
    about_text, about_image
    contact_email, contact_phone, contact_address
    whatsapp_number
    facebook_url, instagram_url, tiktok_url
    logo_url  # ← URL COMPLETA
    primary_color, secondary_color
    products_json  # → lista de productos
    gallery_images  # → lista de URLs de imágenes
```

### PASO 2: Adaptar el Template Engine (LISTO)

El `TemplateEngine` ya genera el contexto correcto con todas las variables.
Solo hay que asegurar que las plantillas las usen.

### PASO 3: Corregir cada plantilla (TRABAJO A HACER)

**Estructura base que todas deben tener:**
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_name }}</title>  <!-- ← Dinámico -->
    <meta name="description" content="{{ site_description }}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="logo">
            {% if logo_url %}
            <img src="{{ logo_url }}" alt="{{ site_name }}">
            {% else %}
            <span class="icon">{{ model_icon }}</span>
            {% endif %}
            <h1>{{ site_name }}</h1>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <h2>{{ hero_title }}</h2>
        <p>{{ hero_subtitle }}</p>
    </section>

    <!-- About Section -->
    <section class="about">
        <p>{{ about_text }}</p>
    </section>

    <!-- Products/Services/Menu Section -->
    <section class="products">
        {% for product in products %}
        <div class="product-card">
            {% if product.image %}
            <img src="{{ product.image }}" alt="{{ product.name }}">
            {% endif %}
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
        </div>
        {% endfor %}
    </section>

    <!-- Gallery Section -->
    <section class="gallery">
        {% for image_url in gallery_images %}
        <img src="{{ image_url }}" alt="Galería">
        {% endfor %}
    </section>

    <!-- Contact Section -->
    <section class="contact">
        <p>{{ contact_email }}</p>
        <p>{{ contact_phone }}</p>
        <p>{{ contact_address }}</p>
    </section>

    <!-- Social Links -->
    <footer class="footer">
        {% if facebook_url %}<a href="{{ facebook_url }}">Facebook</a>{% endif %}
        {% if instagram_url %}<a href="{{ instagram_url }}">Instagram</a>{% endif %}
        {% if tiktok_url %}<a href="{{ tiktok_url }}">TikTok</a>{% endif %}
        {% if whatsapp_number %}<a href="https://wa.me/{{ whatsapp_number }}">WhatsApp</a>{% endif %}
    </footer>

    <script src="tracking.js"></script>
</body>
</html>
```

### PASO 4: Logo por URL externa (SOLUCIÓN)

**La solución ya está en artesanías:**
```html
{% if logo_url %}
<img src="{{ logo_url }}" alt="{{ site_name }}">
{% else %}
<span class="icon">{{ model_icon }}</span>
{% endif %}
```

**¿Qué hace?**
1. ✅ Si `logo_url` existe, usa `<img src="{{ logo_url }}">` directamente
2. ✅ Soporta URLs de Google Drive: `https://drive.google.com/uc?export=download&id=...`
3. ✅ Soporta cualquier URL completa
4. ✅ Si está vacío, muestra un emoji de icono (`{{ model_icon }}`)

**Para URLs de Google Drive, el usuario debe pegar:**
```
https://drive.google.com/uc?export=download&id=1YOUR_FILE_ID
```

O usando formato de vista previa:
```
https://drive.google.com/uc?id=1YOUR_FILE_ID
```

---

## 🔧 CAMBIOS NECESARIOS

### 1. En `backend/utils/template_engine.py`
✅ YA ESTÁ BIEN - No requiere cambios

### 2. En `backend/database.py`
✅ YA ESTÁ BIEN - El modelo Site tiene todos los campos

### 3. En `backend/main.py`
✅ YA ESTÁ BIEN - El endpoint `/api/sites` funciona correctamente

### 4. En `frontend/create-site-windster.html`
✅ REVISAR que envíe los campos correctos en `data`

**Campos que DEBE enviar el formulario:**
```javascript
const formData = {
    model_type: selectedModel,
    name: document.getElementById('name').value,
    description: document.getElementById('description').value,
    hero_title: document.getElementById('hero_title').value,
    hero_subtitle: document.getElementById('hero_subtitle').value,
    hero_image: document.getElementById('hero_image').value,
    about_text: document.getElementById('about_text').value,
    about_image: document.getElementById('about_image').value,
    contact_email: document.getElementById('contact_email').value,
    contact_phone: document.getElementById('contact_phone').value,
    contact_address: document.getElementById('contact_address').value,
    whatsapp_number: document.getElementById('whatsapp_number').value,
    facebook_url: document.getElementById('facebook_url').value,
    instagram_url: document.getElementById('instagram_url').value,
    tiktok_url: document.getElementById('tiktok_url').value,
    logo_url: document.getElementById('logo_url').value,  // ← URL COMPLETA
    primary_color: document.getElementById('primary_color').value,
    secondary_color: document.getElementById('secondary_color').value,
    gallery_images: [...],  // Array de URLs
    products: [...]  // Array de productos
};
```

### 5. En `templates_base/*/index.html` (COCINA, BELLEZA, ADECUACIONES, CHIVOS)
❌ REQUIEREN CORRECCIONES IMPORTANTES

**Lo que deben hacer:**
- ✅ Reemplazar HTML hardcodeado con variables Jinja2
- ✅ Usar los mismos nombres de variables que artesanías
- ✅ Mantener su diseño visual único pero con variables dinámicas
- ✅ Soportar URLs de logo externas
- ✅ Renderizar productos, galería y contacto desde variables

---

## 📝 VARIABLE MAPPING

| Campo del Formulario | Variable en Contexto | Uso en Plantilla |
|---|---|---|
| name | `site_name` | `{{ site_name }}` |
| description | `site_description` | `{{ site_description }}` |
| hero_title | `hero_title` | `{{ hero_title }}` |
| hero_subtitle | `hero_subtitle` | `{{ hero_subtitle }}` |
| hero_image | `hero_image` | `<img src="{{ hero_image }}">` |
| about_text | `about_text` | `{{ about_text }}` |
| about_image | `about_image` | `<img src="{{ about_image }}">` |
| contact_email | `contact_email` | `{{ contact_email }}` |
| contact_phone | `contact_phone` | `{{ contact_phone }}` |
| contact_address | `contact_address` | `{{ contact_address }}` |
| whatsapp_number | `whatsapp_number` | `{{ whatsapp_number }}` |
| facebook_url | `facebook_url` | `<a href="{{ facebook_url }}">` |
| instagram_url | `instagram_url` | `<a href="{{ instagram_url }}">` |
| tiktok_url | `tiktok_url` | `<a href="{{ tiktok_url }}">` |
| logo_url | `logo_url` | `<img src="{{ logo_url }}">` |
| primary_color | `primary_color` | CSS variables o inline styles |
| secondary_color | `secondary_color` | CSS variables o inline styles |
| gallery_images | `gallery_images` | `{% for img in gallery_images %}<img src="{{ img }}">{% endfor %}` |
| products | `products` | `{% for p in products %}{{ p.name }}, {{ p.price }}{% endfor %}` |

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Revisar que `backend/main.py` endpoint `/api/sites` envíe todos los campos
- [ ] Revisar que `frontend/create-site-windster.html` reciba todos los campos del usuario
- [ ] Actualizar `templates_base/cocina/index.html` con variables dinámicas
- [ ] Actualizar `templates_base/belleza/index.html` con variables dinámicas
- [ ] Actualizar `templates_base/adecuaciones/index.html` con variables dinámicas
- [ ] Actualizar `templates_base/chivos/index.html` con variables dinámicas
- [ ] Probar que logo_url de Google Drive se renderice correctamente
- [ ] Probar que products se renderize desde la API
- [ ] Probar que gallery_images se renderice desde la API
- [ ] Probar que los colores primary y secondary se apliquen en CSS
- [ ] Hacer push a GitHub

---

## 🎨 PRÓXIMAS ACCIONES

1. Crearemos **plantillas corregidas** para cocina, belleza, adecuaciones y chivos
2. Aseguraremos que **todas usen el mismo modelo de datos**
3. Cada una **mantendrá su diseño visual único** pero renderizará variables dinámicas
4. Verificaremos que **logo_url** funcione con URLs externas
5. Haremos **tests de creación de sitios** desde el formulario

---

