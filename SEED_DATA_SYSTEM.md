# Sistema de Datos Semilla (Seed Data)

## 📋 Descripción General

El sistema de datos semilla proporciona contenido de ejemplo precargado para cada tipo de modelo de negocio. Cuando un usuario crea un nuevo sitio, automáticamente se llena con imágenes, textos y productos de ejemplo basados en el tipo de negocio seleccionado.

## 🎯 Propósito

- **Facilitar el inicio**: Los usuarios ven inmediatamente cómo se verá su sitio con contenido real
- **Proveer ejemplos**: Muestra qué tipo de contenido es apropiado para cada sección
- **Acelerar el proceso**: Reduce el tiempo de configuración inicial
- **Guiar al usuario**: Sirve como plantilla que el usuario puede modificar

## 🗂️ Archivo de Datos

**Ubicación**: `/backend/seed_data.json`

### Estructura por Modelo

Cada modelo de negocio tiene su conjunto de datos semilla:

```json
{
  "artesanias": { ... },
  "cocina": { ... },
  "belleza": { ... },
  "adecuaciones": { ... },
  "chivos": { ... }
}
```

### Campos Incluidos

Para cada modelo se incluye:

#### Información Básica
- `site_name`: Nombre del sitio de ejemplo
- `site_description`: Descripción meta para SEO
- `hero_title`: Título principal del hero
- `hero_subtitle`: Subtítulo del hero
- `hero_image`: URL de imagen del hero

#### Sección "Nosotros"
- `about_text`: Texto descriptivo de la empresa
- `about_image`: URL de imagen de la sección

#### Productos/Servicios (Array)
- `name`: Nombre del producto/servicio
- `description`: Descripción detallada
- `price`: Precio en formato string
- `image`: URL de imagen del producto

#### Galería (Array de URLs)
- `gallery_images`: Array de URLs de imágenes para la galería

#### Contacto
- `contact_phone`: Teléfono de ejemplo
- `contact_email`: Email de ejemplo
- `whatsapp_number`: Número de WhatsApp

#### Redes Sociales
- `facebook_url`: URL de Facebook
- `instagram_url`: URL de Instagram
- `tiktok_url`: URL de TikTok (opcional)

## 📦 Modelos Disponibles

### 1. Artesanías 🎨
**Contenido semilla**:
- Nombre: "Artesanías Tradicionales"
- 3 productos: Mochilas Wayuu, Hamacas Artesanales, Cestas de Palma
- 4 imágenes en galería
- Enfoque: Productos artesanales y cultura tradicional

### 2. Cocina Doméstica 🍳
**Contenido semilla**:
- Nombre: "Sabores Guajiros"
- 3 productos: Friche de Chivo, Arepa de Huevo, Sopa de Pescado
- 4 imágenes en galería
- Enfoque: Comida tradicional y casera

### 3. Belleza y Barbería 💇
**Contenido semilla**:
- Nombre: "Acera - Salón de Belleza"
- 3 servicios: Corte y Peinado, Manicure y Pedicure, Tratamiento Capilar
- 4 imágenes en galería
- Enfoque: Servicios profesionales de belleza

### 4. Adecuaciones Menores 🔧
**Contenido semilla**:
- Nombre: "Construcciones y Arreglos JM"
- 3 servicios: Reparaciones Eléctricas, Plomería, Pintura y Acabados
- 4 imágenes en galería
- Enfoque: Servicios de construcción y mantenimiento

### 5. Cabras 🐐
**Contenido semilla**:
- Nombre: "Cabras de La Guajira"
- 3 productos: Cabra Adulta, Cabrito Joven, Queso de Cabra
- 4 imágenes en galería
- Enfoque: Ganadería caprina y productos derivados

## 🔧 Implementación Técnica

### Backend (main.py)

```python
# Cargar datos semilla al iniciar
with open(Path(__file__).parent / "seed_data.json", 'r', encoding='utf-8') as f:
    SEED_DATA = json.load(f)

# Usar en creación de sitio
@app.post("/api/sites")
async def create_site(request: Request, ...):
    data = await request.json()
    model_type = data.get("model_type")
    
    # Obtener datos semilla para este modelo
    seed_data = SEED_DATA.get(model_type, {})
    
    # Crear sitio usando seed data como defaults
    site = Site(
        name=data.get("name", seed_data.get("site_name", "Nuevo Sitio")),
        hero_title=data.get("hero_title", seed_data.get("hero_title", "")),
        # ... etc
    )
```

### Proceso de Creación

1. **Usuario selecciona modelo**: Elige tipo de negocio (artesanías, cocina, etc.)
2. **Backend carga seed data**: Busca datos correspondientes en `seed_data.json`
3. **Datos se aplican como defaults**: Si el usuario no proporciona valor, se usa el seed data
4. **Usuario puede personalizar**: Los datos semilla son editables en el editor

## 🖼️ Imágenes de Ejemplo

Todas las imágenes provienen de **Unsplash** (https://images.unsplash.com):

### Ventajas de Unsplash:
- ✅ Gratuitas y de alta calidad
- ✅ No requieren atribución
- ✅ URLs estables y confiables
- ✅ Gran variedad de categorías
- ✅ Optimización automática con parámetros (w=width)

### Formato de URL:
```
https://images.unsplash.com/photo-{ID}?w={ancho}
```

Ejemplo:
```
https://images.unsplash.com/photo-1515377905703-c4788e51af15?w=1200
```

## 🎨 Personalización de Seed Data

### Modificar Datos Existentes

1. Editar `/backend/seed_data.json`
2. Cambiar textos, precios o descripciones
3. Actualizar URLs de imágenes
4. Reiniciar el servidor

### Agregar Nuevo Modelo

```json
{
  "nuevo_modelo": {
    "site_name": "Nombre del Negocio",
    "site_description": "Descripción...",
    "hero_title": "Título...",
    "hero_subtitle": "Subtítulo...",
    "hero_image": "https://...",
    "about_text": "Texto sobre nosotros...",
    "about_image": "https://...",
    "products": [
      {
        "name": "Producto 1",
        "description": "Descripción...",
        "price": "50000",
        "image": "https://..."
      }
    ],
    "gallery_images": [
      "https://...",
      "https://..."
    ],
    "contact_phone": "+57 300 123 4567",
    "contact_email": "info@ejemplo.com",
    "whatsapp_number": "573001234567",
    "facebook_url": "https://facebook.com/ejemplo",
    "instagram_url": "https://instagram.com/ejemplo",
    "tiktok_url": "https://tiktok.com/@ejemplo"
  }
}
```

## 📊 Flujo de Datos

```
Usuario crea sitio
    ↓
Selecciona modelo (ej: "cocina")
    ↓
Backend busca en SEED_DATA["cocina"]
    ↓
Aplica datos como valores por defecto
    ↓
Crea registro en base de datos
    ↓
Usuario ve sitio con contenido de ejemplo
    ↓
Usuario edita y personaliza contenido
    ↓
Datos originales son reemplazados
```

## ✏️ Experiencia del Usuario

### Al Crear el Sitio:
1. Usuario ve formulario de creación
2. Solo necesita ingresar nombre básico
3. Al crear, el sitio ya tiene:
   - Imágenes profesionales
   - Textos descriptivos
   - Productos de ejemplo
   - Información de contacto
   - Enlaces de redes sociales

### En el Editor:
1. Usuario abre el editor del sitio
2. Ve todas las secciones prellenadas
3. Puede:
   - **Reemplazar** cualquier imagen
   - **Editar** todos los textos
   - **Modificar** productos/servicios
   - **Cambiar** colores y estilos
   - **Actualizar** información de contacto

## 🔄 Actualizaciones y Mantenimiento

### Actualizar Imágenes
Si una imagen de Unsplash deja de funcionar:
1. Buscar nueva imagen en unsplash.com
2. Copiar URL de la imagen
3. Actualizar en `seed_data.json`

### Actualizar Textos
Los textos pueden ser mejorados basándose en:
- Feedback de usuarios
- Mejores prácticas de copywriting
- Optimización SEO

### Versiones Localizadas
Futuro: Agregar seed data en otros idiomas:
```json
{
  "artesanias_en": { ... },  // Inglés
  "artesanias_fr": { ... }   // Francés
}
```

## 🚀 Beneficios del Sistema

1. **Onboarding más rápido**: Usuarios pueden ver resultados inmediatos
2. **Menos frustración**: No empiezan con sitio vacío
3. **Mejores ejemplos**: Ven qué contenido funciona mejor
4. **Mayor adopción**: Reducir barrera de entrada
5. **Flexibilidad**: Todo es editable y personalizable

## 🎯 Mejores Prácticas

### Para Administradores:
- Mantener imágenes de alta calidad
- Usar textos realistas y profesionales
- Precios coherentes con el mercado
- URLs de redes sociales como ejemplos claros

### Para Desarrolladores:
- Validar que todas las imágenes carguen
- Manejar errores si seed_data.json falta
- Proveer fallbacks por si falla carga de datos
- Documentar cambios en estructura de datos

## 📝 Notas Adicionales

- Los datos semilla **NO** sobrescriben datos existentes
- Solo se aplican en la **creación inicial** del sitio
- Usuario tiene **control total** sobre su contenido
- Sistema es **extensible** para nuevos modelos
- Compatible con sistema de **upload de imágenes**

## 🔮 Futuras Mejoras

1. **Panel de administración de seed data**: Editar desde UI
2. **Múltiples variantes**: Varios ejemplos por modelo
3. **IA para generar contenido**: Textos personalizados
4. **Imágenes locales**: Backup de imágenes en el proyecto
5. **Plantillas de industria**: Más específicas (panadería, carpintería, etc.)

---

**Versión**: 1.0  
**Última actualización**: 13 de noviembre de 2025  
**Autor**: WebControl Studio Team
