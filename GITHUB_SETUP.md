# 🔧 Configuración de GitHub para Publicación Automática

## ⚠️ Error Actual: 401 Bad Credentials

Este error indica que el token de GitHub no está configurado o es inválido.

---

## 📋 Pasos para Configurar GitHub

### 1️⃣ Obtener Token de GitHub

1. **Ve a tu cuenta de GitHub**
   - URL: https://github.com/settings/tokens

2. **Genera un nuevo token**
   - Click en **"Generate new token"**
   - Selecciona **"Generate new token (classic)"**

3. **Configura el token**
   - **Note:** `WebControl Studio`
   - **Expiration:** `No expiration` (o elige un tiempo)
   
4. **Selecciona permisos (scopes):**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (Upload packages to GitHub Package Registry)

5. **Genera y copia el token**
   - Click en **"Generate token"**
   - ⚠️ **IMPORTANTE:** Copia el token AHORA (solo se muestra una vez)
   - Ejemplo: `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

---

### 2️⃣ Configurar el archivo .env

Abre el archivo `.env` en la raíz del proyecto y completa:

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_tu_token_aqui_pegalo
GITHUB_USERNAME=tu_usuario_github
```

**Ejemplo real:**
```bash
GITHUB_TOKEN=ghp_AbC123XyZ789DefGhiJklMnoPqrStuVwx
GITHUB_USERNAME=mrmontero
```

---

### 3️⃣ Reiniciar el Servidor

Después de guardar el archivo `.env`:

```bash
# Detener servidor actual
Ctrl + C (en la terminal donde está corriendo)

# O ejecutar:
pkill -f uvicorn

# Reiniciar servidor
./start.sh

# O manualmente:
.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verificar Configuración

Una vez configurado, podrás:

1. ✅ **Crear sitios** normalmente desde el panel
2. ✅ **Publicar en GitHub Pages** automáticamente
3. ✅ **Ver la URL pública** de cada sitio creado

---

## 🎯 Uso sin GitHub (Opcional)

Si NO quieres usar GitHub Pages, puedes:

1. **Crear sitios localmente** - Funcionará normal
2. **Exportar HTML** - Los archivos se generan en el servidor
3. **Usar otro hosting** - Sube manualmente los archivos generados

Pero NO podrás usar la función de **"Publicar"** automáticamente.

---

## 🔍 Solución de Problemas

### Error: "Bad credentials"
- ✅ Verifica que el token esté completo (empeza con `ghp_`)
- ✅ Asegúrate de que no haya espacios antes/después del token
- ✅ Genera un nuevo token si el anterior expiró

### Error: "Resource not accessible by integration"
- ✅ Verifica que el token tenga los permisos correctos
- ✅ Regenera el token con los scopes: `repo`, `workflow`, `write:packages`

### Error: "Not Found"
- ✅ Verifica que `GITHUB_USERNAME` sea tu nombre de usuario correcto
- ✅ No uses tu email, usa tu username de GitHub

---

## 📞 Ayuda Adicional

- **Documentación GitHub Tokens:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **GitHub Pages Docs:** https://docs.github.com/en/pages

---

**Última actualización:** 13 de noviembre de 2025
