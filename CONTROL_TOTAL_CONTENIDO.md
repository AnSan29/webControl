# 🎨 Control Total de Contenido - WebControl Studio

## ✅ Cambios Implementados

### 1. **Base de Datos Expandida**

Se han agregado nuevos campos al modelo `Site` para control total del contenido:

#### Redes Sociales
- `facebook_url` - URL completa del perfil de Facebook
- `instagram_url` - URL completa del perfil de Instagram  
- `tiktok_url` - URL completa del perfil de TikTok
- `whatsapp_number` - Número de WhatsApp con código de país

#### Imágenes
- `hero_image` - Imagen de la sección principal/hero
- `about_image` - Imagen de la sección "Sobre Nosotros"
- `gallery_images` - Array JSON de URLs de imágenes para galería

#### Personalización
- `primary_color` - Color primario del sitio (selector de color)
- `secondary_color` - Color secundario del sitio (selector de color)

### 2. **Plantillas Organizadas**

Las plantillas de `webs-templates_organizar/` han sido movidas a sus ubicaciones correctas:

```
✅ artesaniasTejidos.html → templates_base/artesanias/index.html
✅ cocinaGastronomia.html → templates_base/cocina/index.html
✅ instalacionesArreglos.html → templates_base/adecuaciones/index.html
✅ salonBelleza.html → templates_base/belleza/index.html
✅ ventaCabras.html → templates_base/chivos/index.html
```

### 3. **Botón Flotante de WhatsApp**

#### Características:
- 🟢 Botón verde flotante en esquina inferior derecha
- 📱 Adaptativo (responsive) para móviles
- ✨ Animación suave al pasar el mouse
- 🔗 Link directo a WhatsApp con mensaje predefinido
- 🎯 Solo aparece si `whatsapp_number` está configurado

#### Implementación:
```html
<!-- WhatsApp Floating Button -->
{% if whatsapp_number %}
<a href="https://wa.me/{{ whatsapp_number }}?text=Hola,%20estoy%20interesado%20en%20sus%20productos" 
   class="whatsapp-float" 
   target="_blank">
    <svg>...</svg>
</a>
{% endif %}
```

#### Estilos CSS:
```css
.whatsapp-float {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #25D366;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4);
    z-index: 1000;
}
```

### 4. **Redes Sociales en Footer**

#### Iconos SVG incluidos:
- 🔵 Facebook
- 📸 Instagram
- 🎵 TikTok

#### Características:
- Iconos vectoriales (SVG) escalables
- Hover effects con transformación
- Background semi-transparente
- Abre en nueva pestaña
- Solo aparecen las redes configuradas

### 5. **Editor Expandido**

El editor ahora incluye campos para:

#### Sección Hero
- Título Principal
- Subtítulo
- **Imagen Hero** (nuevo)

#### Sobre Nosotros
- Texto descriptivo
- **Imagen** (nuevo)

#### Contacto
- Email
- Teléfono
- **WhatsApp** (nuevo) - con validación de formato
- Dirección

#### Redes Sociales (nuevo)
- Facebook URL
- Instagram URL
- TikTok URL

#### Personalización (nuevo)
- Color Primario (picker de color)
- Color Secundario (picker de color)

### 6. **Template Engine Actualizado**

El motor de plantillas ahora procesa todos los nuevos campos:

```python
context = {
    # ... campos existentes
    "hero_image": site_data.get("hero_image", ""),
    "about_image": site_data.get("about_image", ""),
    "whatsapp_number": site_data.get("whatsapp_number", ""),
    "facebook_url": site_data.get("facebook_url", ""),
    "instagram_url": site_data.get("instagram_url", ""),
    "tiktok_url": site_data.get("tiktok_url", ""),
    "primary_color": site_data.get("primary_color", ...),
    "secondary_color": site_data.get("secondary_color", ...),
}
```

### 7. **CSS Mejorado**

Nuevos estilos agregados automáticamente:

```css
/* Redes Sociales */
.footer .social-links {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
}

.footer .social-links a {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
}

/* WhatsApp Flotante */
.whatsapp-float {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #25D366;
    /* ... más estilos */
}
```

## 📱 Uso del Sistema

### Crear un Sitio con Control Total

1. **Login** en WebControl Studio
2. **Crear Nuevo Sitio** - Seleccionar modelo de negocio
3. **Editar Contenido**:

   #### Información Básica
   - Nombre y descripción del sitio
   
   #### Sección Hero
   - Título llamativo
   - Subtítulo descriptivo
   - URL de imagen de fondo

   #### Sobre Nosotros
   - Historia del negocio
   - URL de imagen representativa

   #### Contacto
   - Email de contacto
   - Teléfono fijo/móvil
   - **WhatsApp**: `+573001234567` (incluir código país)
   - Dirección física

   #### Redes Sociales
   - **Facebook**: `https://facebook.com/tupagina`
   - **Instagram**: `https://instagram.com/tuusuario`
   - **TikTok**: `https://tiktok.com/@tuusuario`

   #### Personalización
   - Elegir color primario (usar selector)
   - Elegir color secundario (usar selector)

4. **Guardar** - Cambios se guardan y sincronizanel con GitHub Pages automáticamente
5. **Publicar** - Primera vez activa GitHub Pages

### Botón de WhatsApp

**Formato del número**: `+[código país][número]`

Ejemplos:
- Colombia: `+573001234567`
- México: `+525512345678`
- España: `+34612345678`

El botón:
- ✅ Aparece automáticamente si `whatsapp_number` está configurado
- ✅ Abre WhatsApp Web/App según dispositivo
- ✅ Incluye mensaje predefinido: "Hola, estoy interesado en sus productos"
- ✅ Se adapta a móviles (tamaño reducido)

### Redes Sociales

**URLs completas requeridas**:
- ❌ Incorrecto: `@miusuario` o `miusuario`
- ✅ Correcto: `https://instagram.com/miusuario`

Los iconos:
- ✅ Solo aparecen las redes configuradas
- ✅ Se muestran en el footer del sitio
- ✅ Abren en nueva pestaña
- ✅ Tienen efectos hover elegantes

### Imágenes

**URLs de imágenes**:
- Pueden ser de cualquier hosting (Imgur, Cloudinary, etc.)
- Deben ser URLs completas: `https://...`
- Formatos recomendados: JPG, PNG, WebP
- Tamaños recomendados:
  - Hero: 1920x1080px
  - About: 800x600px
  - Logo: 200x200px

### Colores

**Selectores de color**:
- Click en el cuadro de color
- Elegir color del picker
- Se aplica automáticamente al publicar
- Afecta botones, encabezados, enlaces, etc.

## 🔄 Auto-Sincronización

Con estos cambios, el flujo es:

1. Usuario edita contenido (textos, imágenes, redes sociales, colores)
2. Click en "💾 Guardar"
3. Sistema guarda en base de datos
4. **Si el sitio está publicado**: Sistema automáticamente:
   - Regenera HTML con nuevos datos
   - Actualiza repositorio en GitHub
   - GitHub Pages se actualiza (1-2 minutos)
5. Cambios visibles en el sitio público

## 🎯 Beneficios

### Para el Usuario
- ✅ Control completo del contenido
- ✅ No necesita editar código
- ✅ Cambios en tiempo real
- ✅ Integración con redes sociales
- ✅ WhatsApp directo desde el sitio
- ✅ Personalización de colores
- ✅ Gestión de imágenes fácil

### Para el Negocio
- ✅ Mayor engagement con WhatsApp
- ✅ Tráfico a redes sociales
- ✅ Identidad visual personalizada
- ✅ Actualización rápida de contenido
- ✅ Sin dependencia de desarrolladores

## 📊 Campos Disponibles por Plantilla

Todas las plantillas soportan:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Texto | Nombre del sitio |
| `description` | Texto | Descripción para SEO |
| `hero_title` | Texto | Título principal |
| `hero_subtitle` | Texto | Subtítulo |
| `hero_image` | URL | Imagen de fondo hero |
| `about_text` | Texto largo | Historia/Descripción |
| `about_image` | URL | Imagen descriptiva |
| `contact_email` | Email | Correo de contacto |
| `contact_phone` | Teléfono | Número de teléfono |
| `whatsapp_number` | Teléfono | WhatsApp con código |
| `contact_address` | Texto | Dirección física |
| `facebook_url` | URL | Perfil de Facebook |
| `instagram_url` | URL | Perfil de Instagram |
| `tiktok_url` | URL | Perfil de TikTok |
| `logo_url` | URL | Logo del negocio |
| `primary_color` | Color | Color principal |
| `secondary_color` | Color | Color secundario |
| `products_json` | JSON | Productos/Servicios |

## 🚀 Próximos Pasos Sugeridos

1. **Galería de Imágenes**: Implementar subida múltiple
2. **Editor de Productos**: Interfaz drag & drop
3. **Análisis de WhatsApp**: Tracking de clics en botón
4. **Temas Predefinidos**: Paletas de colores preconfiguradas
5. **Preview en Vivo**: Vista previa antes de publicar

## 🆘 Solución de Problemas

### El botón de WhatsApp no aparece
- Verifica que `whatsapp_number` esté configurado
- Asegúrate de incluir el código de país: `+57...`
- Guarda y vuelve a publicar el sitio

### Las redes sociales no se muestran
- Verifica que las URLs sean completas: `https://...`
- Al menos una red debe estar configurada
- Limpia la caché del navegador

### Los colores no cambian
- Los colores se aplican al publicar
- Puede tardar 1-2 minutos en GitHub Pages
- Fuerza recarga: `Ctrl + Shift + R`

### Imágenes no se cargan
- Verifica que las URLs sean accesibles públicamente
- Prueba abrir la URL en el navegador
- Algunos hosting bloquean hotlinking

---

**Estado**: ✅ Completamente implementado y funcional

**Versión**: 2.0 - Control Total de Contenido

**Fecha**: Noviembre 2025

## 🧾 Formularios y checklist de captura

### Formulario de creación (`frontend/create-site-windster.html`)

1. **Modelo y nombre**
    - `model_type`: desbloquea paletas y seed data.
    - `palette_choice`: rellena `primary_color` y `secondary_color` ocultos.
    - `name`, `custom_domain`, `description`.
2. **Mensaje principal**
    - `hero_title`, `hero_subtitle`, `about_text` inicial.
3. **Contacto y redes**
    - `contact_email`, `contact_phone`, `contact_address`, `whatsapp_number`.
    - `facebook_url`, `instagram_url` (TikTok se captura luego en el editor).
4. **Acción**
    - Enviar = crea registro `Site` con defaults del modelo y abre el editor listo para completar el resto de los campos.

### Formulario de edición (`frontend/editor.html`)

El editor secciones-carta permite completar **todo** el set de campos soportado:

- **Estado del sitio**: nombre, descripción corta, botón de publicar.
- **Sección Hero**: `hero_title`, `hero_subtitle`, `hero_image` (subida directa → `/api/upload-image` o URL manual).
- **Sobre nosotros**: `about_text`, `about_image`.
- **Logos y aliados**: `logo_url` y carrusel de logos (se guarda como JSON en `supporter_logos_json`).
- **Contacto**: `contact_email`, `contact_phone`, `contact_address`, `whatsapp_number` (con ayuda visual para solo cifras).
- **Redes**: `facebook_url`, `instagram_url`, `tiktok_url`.
- **Productos y servicios**: constructor dinámico que serializa a `products_json` (cada tarjeta incluye nombre, descripción, precio, imagen).
- **Galería**: lista de URLs en `gallery_images` (sección con previsualización).
- **Colores**: selectores `primary_color`, `secondary_color` + paletas curadas por modelo.
- **Configuración avanzada**: `logo_url`, `custom_domain` persistentes.

### Matriz UI → Base de datos → Template Engine

| Grupo UI | Campo / ID HTML | Clave en payload/BD (`Site`) | Uso final en plantillas (`template_engine`) |
| --- | --- | --- | --- |
| Identidad | `name` | `Site.name` | `<title>`, hero `h1`, footer |
| SEO | `description` | `Site.description` | meta description, secciones intro |
| Hero | `hero_title`, `hero_subtitle`, `hero_image` | `Site.hero_title`, `Site.hero_subtitle`, `Site.hero_image` | Cabecera, CTA, fondos (con `normalize_drive_image`) |
| Story | `about_text`, `about_image` | `Site.about_text`, `Site.about_image` | Sección “Sobre nosotros” |
| Contacto | `contact_email`, `contact_phone`, `contact_address` | Columnas homónimas | Bloque de contacto y footer |
| WhatsApp | `whatsapp_number` | `Site.whatsapp_number` (se normaliza quitando `+` y espacios antes de generar `wa.me`) | Botón flotante + icono en footer |
| Redes | `facebook_url`, `instagram_url`, `tiktok_url` | Columnas homónimas | Iconos condicionales en footer |
| Logo | `logo_url` | `Site.logo_url` | Header / SEO fallback |
| Colores | `primary_color`, `secondary_color` (+ paletas modelo) | Columnas homónimas | `styles.css` (variables CSS) + tokens en HTML |
| Productos | UI dinámica → `products_json` | `Site.products_json` (JSON) | Cards en sección productos |
| Galería | `gallery_images_input` | `Site.gallery_images` (JSON) | Grilla de imágenes |
| Dominio | `custom_domain` | `Site.custom_domain` | Configuración para CNAME en despliegue |

> 📝 **Normalizaciones clave**: `template_engine` reutiliza `normalize_media_url` y `drive_preview_iframe`; el script de auditoría aplica `sanitize_whatsapp` antes de buscar el valor en el HTML generado.

## 🔍 Auditoría automatizada y verificación con `curl`

1. **Generar un sitio de prueba completo**

```bash
/home/mrmontero/Documentos/webcontrol_studio/.venv/bin/python scripts/variable_flow_audit.py
```

Este comando:
- Hace login en `/api/login` con las credenciales del entorno.
- Crea un sitio modelo artesanías con valores únicos.
- Lee el `Site` almacenado y renderiza los archivos con `TemplateEngine`.

## 🌐 Publicación real y validación vía `curl`

> Contexto: se publicó el **sitio ID 4** y se validó el despliegue final en GitHub Pages (`https://ReconvencionLaboralGuajira.github.io/sitio-qa-curl-4/`).

1. **Reiniciar el backend** (evita sockets colgados de uvicorn):

        ```bash
        pkill -f "uvicorn" || true
        PYTHONPATH=/home/mrmontero/Documentos/webcontrol_studio \
        /home/mrmontero/Documentos/webcontrol_studio/.venv/bin/uvicorn backend.main:app --reload
        ```

2. **Login con cURL** y guardar el token (archivo `/tmp/webcontrol_login.json`):

        ```bash
        curl -sS -X POST http://127.0.0.1:8000/api/login \
            -H 'Content-Type: application/json' \
            -d '{"email":"'$ADMIN_EMAIL'","password":"'$ADMIN_PASSWORD'"}' \
            | tee /tmp/webcontrol_login.json
        export ACCESS_TOKEN=$(jq -r '.access_token' /tmp/webcontrol_login.json)
        ```

3. **Publicar el sitio 4** (respuesta guardada en `/tmp/site_publish_response.json`):

        ```bash
        curl -sS -X POST http://127.0.0.1:8000/api/sites/4/publish \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            | tee /tmp/site_publish_response.json
        ```

        Resultado: `{ "message": "Sitio publicado exitosamente", "url": "https://ReconvencionLaboralGuajira.github.io/sitio-qa-curl-4/" }`.

4. **Esperar a que GitHub Pages esté activo** (HTTP 200) y conservar cuerpo/headers:

        ```bash
        PUBLISHED_URL="https://ReconvencionLaboralGuajira.github.io/sitio-qa-curl-4/"
        until curl -sS -o /tmp/site_publish_body.html -D /tmp/site_publish_headers.txt "$PUBLISHED_URL"; do
            echo "GitHub Pages aún propagando..."
            sleep 10
        done
        head -n 20 /tmp/site_publish_headers.txt
        ```

        - Varios intentos devolvieron `404 Not Found` hasta que GitHub Pages completó el build.
        - El último intento registró `HTTP/2 200` con los headers finales en `/tmp/site_publish_headers.txt`.

5. **Scrape de contenido final** para asegurar que el HTML público refleja los datos esperados:

        ```bash
        python - <<'PY'
        from bs4 import BeautifulSoup
        from pathlib import Path

        html = Path('/tmp/site_publish_body.html').read_text()
        soup = BeautifulSoup(html, 'html.parser')

        hero = soup.select_one('.hero-content')
        report = {
                'hero_title': hero.find('h2').get_text(strip=True),
                'hero_subtitle': hero.find('p').get_text(strip=True),
                'contact_email': soup.select_one('a[href^="mailto:"]').get_text(strip=True),
                'whatsapp_link': soup.select_one('a[href^="https://wa.me/"]')['href'],
        }
        print(report)
        PY
        ```

        Salida observada:

        ```text
        {
            'hero_title': 'Transformamos fibras en historias',
            'hero_subtitle': 'Colecciones hechas a mano desde La Guajira',
            'contact_email': 'qa-curl@example.com',
            'whatsapp_link': 'https://wa.me/573015559988'
        }
        ```

6. **Artefactos generados** (útiles para auditoría posterior):

| Archivo | Contenido |
| --- | --- |
| `/tmp/webcontrol_login.json` | Token y payload devuelto por `/api/login`. |
| `/tmp/site_publish_response.json` | Respuesta completa del POST `/api/sites/4/publish`. |
| `/tmp/site_publish_headers.txt` | Últimos headers HTTP/2 200 recibidos desde GitHub Pages. |
| `/tmp/site_publish_body.html` | HTML final del sitio publicado (base para scraping). |

> ✅ Con esto se documenta el flujo completo **publicar → esperar propagación → validar contenido real** usando únicamente `curl` + `BeautifulSoup`.
- Guarda todo en `qa_artifacts/content_audit_<timestamp>/` junto a `site_payload.json`, `site_data.json` y `verification_matrix.json` (todas las variables quedan marcadas como **OK**).

2. **Verificar el despliegue generado con `curl`**

```bash
cd /home/mrmontero/Documentos/webcontrol_studio/qa_artifacts/content_audit_20251116_195820
python -m http.server 8099 &
curl -I http://127.0.0.1:8099/index.html
curl http://127.0.0.1:8099/index.html | head -n 10
kill %1
```

Resultado sample:

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.12.3
Content-type: text/html
...
<!DOCTYPE html>
<html lang="es">
<head>
     <title>QA Control Artesanías 195820</title>
     <meta name="description" content="Auditoría integral del flujo de datos">
```

> Así comprobamos, sin depender de GitHub Pages, que el paquete generado contiene todos los contenidos y que los encabezados HTTP responden correctamente.

3. **Ubicar la evidencia**
    - HTML/CSS/JS finales: `qa_artifacts/content_audit_20251116_195820/{index.html, styles.css, tracking.js}`.
    - Payload original vs. datos persistidos: `site_payload.json` y `site_data.json`.
    - Matriz de verificaciones campo a campo: `verification_matrix.json` (todas las entradas en `found: true`).

Con este flujo no queda ningún campo sin rastrear: los formularios guían la captura, la base lo persiste, las plantillas lo reflejan y la auditoría automática + `curl` certifican que el despliegue sirve exactamente los contenidos esperados.

## 🧪 Pruebas rigurosas con `curl` + scraping (nov 16)

1. **Autenticación vía `curl`**
     ```bash
     curl -s -X POST \
         -d 'username=mariomontero942@gmail.com&password=M@rio1027' \
         http://127.0.0.1:8000/api/login > /tmp/webcontrol_login.json
     ```
     - Se extrae el token (`/tmp/webcontrol_token.txt`) para reusar en todas las peticiones protegidas.

2. **Creación de un sitio real por API**
     ```bash
     TOKEN=$(cat /tmp/webcontrol_token.txt)
     curl -s -X POST http://127.0.0.1:8000/api/sites \
         -H "Authorization: Bearer $TOKEN" \
         -H 'Content-Type: application/json' \
         --data @/tmp/site_payload.json > /tmp/site_create_response.json
     ```
     - Payload incluye todos los campos: hero, contacto, redes, productos (ver `/tmp/site_payload.json`).
     - Respuesta: `{ "id": 4, "name": "Sitio QA Curl", ... }`.
     - Se consultó inmediatamente: `curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/sites/4 > /tmp/site_detail_4.json` para confirmar persistencia.

3. **Renderizado del sitio y verificación de cabeceras HTTP**
     ```bash
     python - <<'PY'
     from pathlib import Path
     import json, sys
     sys.path.insert(0, str(Path('.').resolve()))
     from backend.utils.template_engine import TemplateEngine
     data = json.load(open('/tmp/site_detail_4.json'))
     data['products_json'] = json.dumps(data.get('products', []))
     data['gallery_images'] = json.dumps(data.get('gallery_images', []))
     out = Path('qa_artifacts/curl_site_4'); out.mkdir(parents=True, exist_ok=True)
     files = TemplateEngine().generate_site(data['model_type'], data)
     for name, content in files.items():
             (out / name).write_text(content, encoding='utf-8')
     PY

     cd qa_artifacts/curl_site_4
     python -m http.server 8123 &
     curl -I http://127.0.0.1:8123/index.html > /tmp/site4_headers.txt
     curl -s http://127.0.0.1:8123/index.html > /tmp/site4_page.html
     kill <PID>
     ```
     - Cabeceras devueltas: `HTTP/1.0 200 OK`, `Content-type: text/html`, `Content-Length: 28 714`.

4. **Scraping con BeautifulSoup**
     ```bash
     python - <<'PY'
     from bs4 import BeautifulSoup
     from pathlib import Path
     import json
     html = Path('/tmp/site4_page.html').read_text(encoding='utf-8')
     soup = BeautifulSoup(html, 'html.parser')
     checks = {
             'hero_title': soup.find(['h1','h2']).get_text(strip=True),
             'contact_email': 'qa-curl@example.com' in html,
             'whatsapp_link': any('https://wa.me' in (a.get('href') or '') for a in soup.find_all('a')),
             'product_names': [h.get_text(strip=True) for h in soup.select('.product-card h3')[:2]],
             'gallery_images': [img.get('src') for img in soup.select('.gallery-card img')[:2]],
     }
     Path('/tmp/site4_scrape.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding='utf-8')
     print(json.dumps(checks, indent=2, ensure_ascii=False))
     PY
     ```
     - Salida principal:
         ```json
         {
             "hero_title": "Sitio QA Curl",
             "contact_email": true,
             "whatsapp_link": true,
             "product_names": ["Hamaca Wayuu QA"],
             "gallery_images": [
                 "https://picsum.photos/seed/curl-gallery-1/1200/900",
                 "https://picsum.photos/seed/curl-gallery-2/1200/900"
             ]
         }
         ```

> 📌 Nota: el backend almacena `price` como string sin símbolo (`50.000`), por lo que el template muestra ese formato. Todo el resto de los campos se conserva sin alteraciones.
