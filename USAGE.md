# 📖 Guía de Uso - Control de Sitios Productivos

## 🎯 Primeros Pasos

### 1. Instalación Inicial

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

### 2. Configurar GitHub

1. Ve a GitHub.com → Settings → Developer settings → Personal access tokens
2. Click en "Generate new token (classic)"
3. Selecciona los permisos: `repo`, `workflow`
4. Copia el token generado
5. Pégalo en el archivo `.env` en la variable `GITHUB_TOKEN`

### 3. Iniciar el Servidor

```bash
cd backend
uvicorn main:app --reload
```

El panel estará disponible en: **http://localhost:8000**

## 🔐 Login

**Credenciales por defecto:**
- Email: `admin@example.com`
- Password: `admin123`

⚠️ **Importante:** Cambia estas credenciales después del primer login.

## 🏗️ Crear tu Primer Sitio

### Paso 1: Seleccionar Modelo

1. Click en **"Modelos"** en el menú
2. Explora los 5 modelos disponibles:
   - 🎨 **Artesanías** - Para productos hechos a mano
   - 🍳 **Cocina** - Para negocios de comida
   - 🔧 **Adecuaciones** - Para servicios de construcción
   - 💇 **Belleza** - Para salones y spas
   - 🐐 **Cría de Chivos** - Para ganadería

3. Click en **"Usar este modelo"**

### Paso 2: Llenar Información

Completa el formulario con:

- **Nombre del Negocio**: Ej: "Artesanías Don Pedro"
- **Descripción**: Breve descripción de tu negocio
- **Título Principal**: El mensaje principal en tu sitio
- **Subtítulo**: Un mensaje complementario
- **Sobre Nosotros**: Historia y valores de tu negocio
- **Contacto**: Email, teléfono, dirección

### Paso 3: Editar Contenido

1. Después de crear, serás redirigido al **Editor**
2. Personaliza cada sección de tu sitio
3. Click en **"💾 Guardar"** para guardar cambios

### Paso 4: Publicar

1. Click en **"🚀 Publicar"**
2. El sistema creará automáticamente:
   - Un repositorio en tu GitHub
   - Habilitará GitHub Pages
   - Generará tu sitio con la URL

## 📝 Editar un Sitio Existente

1. Ve al **Dashboard**
2. Encuentra tu sitio en la tabla
3. Click en **"Editar"**
4. Modifica el contenido
5. Click en **"💾 Guardar"**
6. Si quieres actualizar el sitio publicado, click en **"🚀 Publicar"** nuevamente

## 🌐 Configurar Dominio Personalizado

### Opción 1: Durante la Creación

En el formulario de creación, ingresa tu dominio en **"Dominio Personalizado"**:
```
www.minegocio.com
```

### Opción 2: Después de Crear

1. Edita el sitio
2. Ve a **"Configuración Avanzada"**
3. Ingresa tu dominio
4. Guarda y republica

### Configuración DNS

En tu proveedor de dominio (GoDaddy, Namecheap, etc.):

**Para dominio con www:**
```
Tipo: CNAME
Nombre: www
Valor: tu-usuario.github.io
```

**Para dominio raíz:**
```
Tipo: A
Nombre: @
Valor: 185.199.108.153
Valor: 185.199.109.153
Valor: 185.199.110.153
Valor: 185.199.111.153
```

⏱️ Los cambios DNS pueden tardar hasta 48 horas en propagarse.

## 📊 Ver Estadísticas

1. Ve al sitio en el Dashboard
2. Click en **"Editar"**
3. Click en la pestaña **"Estadísticas"**

Verás:
- **Visitas Totales**
- **Gráfico de visitas por día** (últimos 7 días)
- **Información del sitio**

## 🎨 Personalización Avanzada

### Cambiar Logo

1. Sube tu logo a un servicio de hosting de imágenes:
   - [Imgur.com](https://imgur.com)
   - [ImgBB.com](https://imgbb.com)
   - GitHub (en tu repositorio)

2. Copia la URL de la imagen
3. En el editor, pega la URL en **"URL del Logo"**

### Agregar Productos

**Nota:** La funcionalidad de productos se expandirá en futuras versiones.

Por ahora, los productos se definen en el código. Para agregar productos:

1. Edita el archivo del sitio en GitHub
2. Modifica la sección de productos
3. Commit y push

## 🔧 Mantenimiento

### Backup de la Base de Datos

```bash
cp backend/db.sqlite3 backup/db.sqlite3.$(date +%Y%m%d)
```

### Actualizar el Sistema

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
cd backend
python -c "from database import init_db; init_db()"
```

### Cambiar Contraseña de Admin

1. Abre Python en el backend:
```bash
cd backend
python
```

2. Ejecuta:
```python
from database import SessionLocal, Admin
from auth import get_password_hash

db = SessionLocal()
admin = db.query(Admin).filter(Admin.email == "admin@example.com").first()
admin.hashed_password = get_password_hash("nueva_contraseña")
db.commit()
print("Contraseña actualizada")
```

## ❓ Problemas Comunes

### Error: "GITHUB_TOKEN no encontrado"

**Solución:** Verifica que el archivo `.env` tenga configurado `GITHUB_TOKEN`.

### Error: "No se puede publicar en GitHub"

**Posibles causas:**
1. Token de GitHub inválido o sin permisos
2. Nombre de repositorio ya existe
3. Límite de repositorios alcanzado

**Solución:** Verifica tu token y permisos en GitHub.

### El sitio no se ve después de publicar

**Solución:** GitHub Pages puede tardar 1-2 minutos en activarse. Espera y recarga.

### Errores de base de datos

**Solución:** Reinicializa la BD:
```bash
cd backend
rm db.sqlite3
python -c "from database import init_db; init_db()"
```

## 🆘 Soporte

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/control-sitios/issues)
- **Email:** soporte@example.com
- **Documentación:** Ver `README.md` y `DEPLOYMENT.md`

## 💡 Tips

1. **Guarda frecuentemente** mientras editas
2. **Prueba localmente** antes de publicar
3. **Usa imágenes optimizadas** (max 500KB)
4. **Revisa estadísticas regularmente** para mejorar tu sitio
5. **Actualiza contenido mensualmente** para mantener relevancia

## 🚀 Próximas Funcionalidades

- [ ] Editor visual de productos
- [ ] Subida de imágenes directo desde el panel
- [ ] Múltiples temas por modelo
- [ ] Integración con redes sociales
- [ ] Formulario de contacto funcional
- [ ] Blog integrado
- [ ] SEO automático mejorado
- [ ] Multiidioma

---

**¿Necesitas ayuda?** No dudes en contactarnos o abrir un issue en GitHub.
