# 📡 Ejemplos de API - WebControl Studio

## 🔐 Autenticación

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@webcontrol.com",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 📋 Sitios Web

### Listar todos los sitios
```bash
curl http://localhost:8000/api/sites \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Obtener un sitio específico
```bash
curl http://localhost:8000/api/sites/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Crear un nuevo sitio
```bash
curl -X POST http://localhost:8000/api/sites \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Artesanías La Esperanza",
    "modelo": "artesanias",
    "descripcion": "Productos artesanales únicos hechos a mano",
    "telefono": "555-0123",
    "email": "contacto@laesperanza.com",
    "direccion": "Calle Principal #123",
    "dominio_personalizado": "artesaniaslaesperanza.com",
    "github_repo": "artesanias-esperanza"
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Artesanías La Esperanza",
  "modelo": "artesanias",
  "url_publicada": "https://username.github.io/artesanias-esperanza",
  "created_at": "2025-11-13T10:30:00",
  "visitas": 0
}
```

### Actualizar un sitio
```bash
curl -X PUT http://localhost:8000/api/sites/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Artesanías La Nueva Esperanza",
    "telefono": "555-9999"
  }'
```

### Eliminar un sitio
```bash
curl -X DELETE http://localhost:8000/api/sites/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎨 Modelos de Negocio

### Listar todos los modelos disponibles
```bash
curl http://localhost:8000/api/models
```

**Respuesta:**
```json
[
  {
    "id": "artesanias",
    "nombre": "Artesanías",
    "descripcion": "Perfecto para negocios de artesanías y productos hechos a mano",
    "color_primario": "#C46B29",
    "color_secundario": "#E7B77D",
    "color_acento": "#F1E4C6",
    "color_claro": "#D2A679"
  },
  ...
]
```

---

## 📊 Estadísticas

### Obtener estadísticas de un sitio
```bash
curl http://localhost:8000/api/sites/1/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**
```json
{
  "site_id": 1,
  "total_visitas": 150,
  "visitas_hoy": 12,
  "visitas_semana": 45,
  "visitas_mes": 150,
  "ultimo_acceso": "2025-11-13T15:30:00"
}
```

### Registrar una visita (llamado desde el sitio publicado)
```bash
curl -X POST http://localhost:8000/api/track \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "1"
  }'
```

---

## 🚀 Publicación

### Publicar sitio en GitHub Pages
```bash
curl -X POST http://localhost:8000/api/sites/1/publish \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "url": "https://username.github.io/artesanias-esperanza",
  "message": "Sitio publicado exitosamente en GitHub Pages"
}
```

---

## 📝 Ejemplos con Python

### Cliente completo con requests
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "admin@webcontrol.com",
    "password": "admin123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Crear sitio
nuevo_sitio = {
    "nombre": "Mi Negocio",
    "modelo": "artesanias",
    "descripcion": "Descripción de mi negocio",
    "telefono": "555-1234",
    "email": "contacto@minegocio.com",
    "direccion": "Mi Dirección 123"
}
response = requests.post(f"{BASE_URL}/api/sites", json=nuevo_sitio, headers=headers)
site_id = response.json()["id"]
print(f"Sitio creado con ID: {site_id}")

# 3. Listar sitios
response = requests.get(f"{BASE_URL}/api/sites", headers=headers)
sitios = response.json()
print(f"Total de sitios: {len(sitios)}")

# 4. Obtener estadísticas
response = requests.get(f"{BASE_URL}/api/sites/{site_id}/stats", headers=headers)
stats = response.json()
print(f"Visitas totales: {stats['total_visitas']}")

# 5. Publicar en GitHub Pages
response = requests.post(f"{BASE_URL}/api/sites/{site_id}/publish", headers=headers)
if response.json()["success"]:
    print(f"Sitio publicado en: {response.json()['url']}")
```

---

## 🧪 Ejemplos con JavaScript (Frontend)

### Crear sitio desde el navegador
```javascript
async function crearSitio() {
    const token = localStorage.getItem('token');
    
    const response = await fetch('http://localhost:8000/api/sites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            nombre: 'Mi Nuevo Negocio',
            modelo: 'cocina',
            descripcion: 'Comida casera deliciosa',
            telefono: '555-5678',
            email: 'info@minegocio.com',
            direccion: 'Calle 123'
        })
    });
    
    const data = await response.json();
    console.log('Sitio creado:', data);
    return data;
}

// Llamar la función
crearSitio().then(sitio => {
    console.log(`Nuevo sitio con ID: ${sitio.id}`);
});
```

### Obtener estadísticas y mostrarlas
```javascript
async function obtenerEstadisticas(siteId) {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`http://localhost:8000/api/sites/${siteId}/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const stats = await response.json();
    
    // Mostrar en el DOM
    document.getElementById('total-visitas').textContent = stats.total_visitas;
    document.getElementById('visitas-hoy').textContent = stats.visitas_hoy;
    document.getElementById('visitas-mes').textContent = stats.visitas_mes;
}
```

---

## 🔍 Testing con curl

### Script completo de testing
```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=== Testing WebControl Studio API ==="

# 1. Login
echo -e "\n1. Login..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@webcontrol.com","password":"admin123"}' \
  | jq -r '.access_token')

echo "Token obtenido: ${TOKEN:0:20}..."

# 2. Listar modelos
echo -e "\n2. Listando modelos disponibles..."
curl -s "$BASE_URL/api/models" | jq '.[] | {id, nombre}'

# 3. Crear sitio
echo -e "\n3. Creando nuevo sitio..."
SITE_ID=$(curl -s -X POST "$BASE_URL/api/sites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre":"Test Site",
    "modelo":"artesanias",
    "descripcion":"Sitio de prueba",
    "telefono":"555-0000",
    "email":"test@test.com",
    "direccion":"Test 123"
  }' | jq -r '.id')

echo "Sitio creado con ID: $SITE_ID"

# 4. Obtener sitio
echo -e "\n4. Obteniendo información del sitio..."
curl -s "$BASE_URL/api/sites/$SITE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Obtener estadísticas
echo -e "\n5. Obteniendo estadísticas..."
curl -s "$BASE_URL/api/sites/$SITE_ID/stats" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n=== Testing completado ==="
```

---

## 📚 Documentación Interactiva

Visita la documentación automática de FastAPI en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - No autorizado |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 💡 Tips de Uso de la API

1. **Siempre guarda el token**: Después del login, guarda el token para futuras peticiones
2. **Maneja errores**: Siempre verifica los códigos de estado HTTP
3. **Rate limiting**: En producción, considera implementar límites de peticiones
4. **CORS**: Configura correctamente los orígenes permitidos en producción
5. **HTTPS**: Usa siempre HTTPS en producción para proteger los tokens

---

**Última actualización**: 13 de noviembre de 2025
