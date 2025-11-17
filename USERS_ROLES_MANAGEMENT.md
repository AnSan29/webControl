# 👥 Módulo de Gestión de Usuarios y Roles

## 📋 Descripción General

El módulo de Gestión de Usuarios y Roles es una interfaz completa integrada en el dashboard de WebControl Studio que permite a los administradores:

- ✅ Crear, actualizar y eliminar usuarios
- ✅ Asignar roles a usuarios
- ✅ Crear y gestionar roles personalizados
- ✅ Asignar usuarios a sitios específicos
- ✅ Ver todas las asignaciones activas

## 🗂️ Estructura de Carpetas

```
webControl/
├── backend/
│   ├── routers/
│   │   ├── auth.py          # Endpoints de autenticación
│   │   ├── roles.py         # CRUD de roles
│   │   └── users.py         # CRUD de usuarios
│   ├── schemas.py           # Esquemas Pydantic para validación
│   ├── permissions.py       # Funciones de control de permisos
│   └── main.py              # Rutas principales
│
└── frontend/
    └── users-management.html # Interfaz de gestión de usuarios
```

## 🚀 Acceso al Módulo

1. **Desde el Dashboard**: 
   - Inicia sesión en http://localhost:8000
   - En la barra lateral, haz clic en "👥 Usuarios y Roles"
   - O accede directamente a: http://localhost:8000/users-management

2. **Credenciales por defecto**:
   - Email: `admin@example.com`
   - Password: `admin123`

## 📊 Tabs Principales

### 1️⃣ Pestaña "Usuarios"

**Funcionalidades**:
- Listar todos los usuarios del sistema
- Ver email, nombre de usuario, rol y estado
- **Botón "Editar"**: Cambiar rol del usuario
- **Botón "Eliminar"**: Eliminar usuario (no disponible para admins)
- **Botón "+ Nuevo Usuario"**: Crear nuevo usuario

**Crear Usuario**:
```
Modal con campos:
- Email (ej: usuario@example.com)
- Usuario (ej: usuario)
- Contraseña (mín. 8 caracteres)
- Rol (usuario, editor, owner)
```

**Editar Usuario**:
```
Modal con campos:
- Email (lectura)
- Rol (editable: usuario, editor, owner, admin)
```

### 2️⃣ Pestaña "Roles"

**Funcionalidades**:
- Crear nuevos roles personalizados
- Listar todos los roles del sistema
- Eliminar roles personalizados
- Los roles del sistema (admin, owner, editor, user) son protegidos

**Crear Rol**:
```
Formulario con campos:
- Nombre del Rol (ej: supervisor)
- Descripción (ej: Supervisor de sitios)
```

### 3️⃣ Pestaña "Asignaciones"

**Funcionalidades**:
- Asignar usuarios a sitios específicos
- Definir el rol del usuario en cada sitio
- Listar todas las asignaciones activas
- Remover asignaciones

**Asignar Usuario a Sitio**:
```
Formulario con campos:
- Usuario (dropdown con lista de usuarios)
- Sitio (dropdown con lista de sitios)
- Rol en este Sitio (editor, viewer, owner)
```

## 🔐 Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **admin** | Acceso total | Ver/editar todos los sitios, gestionar usuarios y roles |
| **owner** | Dueño del sitio | Editar y publicar su sitio asignado |
| **editor** | Editor asignado | Editar sitios que le asigne un admin |
| **user** | Usuario básico | Acceso al panel sin permisos de edición |

## 🔌 Endpoints de API

### Autenticación

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=admin123

Response: {
  "token": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer"
  },
  "user": { ... }
}
```

### Usuarios

```http
# Listar usuarios
GET /api/users
Authorization: Bearer <token>

# Obtener usuario
GET /api/users/{id}
Authorization: Bearer <token>

# Crear usuario
POST /api/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "usuario@example.com",
  "username": "usuario",
  "password": "SecurePass123!",
  "role": "user"  # o role_id: 4
}

# Actualizar usuario
PATCH /api/users/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "editor"
}

# Eliminar usuario
DELETE /api/users/{id}
Authorization: Bearer <token>
```

### Roles

```http
# Listar roles
GET /api/roles
Authorization: Bearer <token>

# Obtener rol
GET /api/roles/{id}
Authorization: Bearer <token>

# Crear rol
POST /api/roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "supervisor",
  "description": "Supervisor de sitios"
}

# Actualizar rol
PATCH /api/roles/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Nueva descripción"
}

# Eliminar rol
DELETE /api/roles/{id}
Authorization: Bearer <token>
```

### Asignaciones

```http
# Listar asignaciones
GET /api/users/assignments
Authorization: Bearer <token>

# Asignar usuario a sitio
POST /api/users/{user_id}/assignments
Authorization: Bearer <token>
Content-Type: application/json

{
  "site_id": 1,
  "permission": "editor"
}

# Eliminar asignación
DELETE /api/users/assignments/{assignment_id}
Authorization: Bearer <token>
```

## 💾 Bases de Datos

### Tablas Principales

**users**
```sql
id INTEGER PRIMARY KEY
username VARCHAR UNIQUE
email VARCHAR UNIQUE
hashed_password VARCHAR
role_id INTEGER FOREIGN KEY
site_id INTEGER FOREIGN KEY
is_active BOOLEAN
last_login DATETIME
created_at DATETIME
updated_at DATETIME
```

**roles**
```sql
id INTEGER PRIMARY KEY
name VARCHAR UNIQUE
description TEXT
created_at DATETIME
updated_at DATETIME
```

**site_assignments**
```sql
id INTEGER PRIMARY KEY
user_id INTEGER FOREIGN KEY
site_id INTEGER FOREIGN KEY
permission VARCHAR (editor/viewer/owner)
created_at DATETIME
```

## 🧪 Testing

### Script de Prueba

El archivo `test_api.py` contiene pruebas automatizadas:

```bash
python test_api.py
```

**Pruebas incluidas**:
1. ✅ Login y obtener token
2. ✅ Listar usuarios
3. ✅ Listar roles
4. ✅ Crear nuevo usuario
5. ✅ Actualizar rol de usuario

## 🔒 Seguridad

### Autenticación

- JWT (JSON Web Tokens) con RS256
- Tokens de acceso con expiración
- Tokens de refresco para renovación
- Contraseñas hasheadas con bcrypt

### Autorización

- Control de permisos basado en roles (RBAC)
- Verificación de permisos en cada endpoint
- Solo admins pueden gestionar usuarios y roles
- Users solo pueden acceder a sus datos

### Validación de Entrada

- Pydantic para validación de esquemas
- Email validation automática
- Constrainsts de longitud en campos
- SQL Injection prevention (SQLAlchemy ORM)

## 📝 Ejemplos de Uso

### Crear usuario desde la interfaz

1. Haz clic en "+ Nuevo Usuario"
2. Completa el formulario:
   - Email: `vendedor@empresa.com`
   - Usuario: `vendedor`
   - Contraseña: `MiPassword123!`
   - Rol: `editor`
3. Haz clic en "Crear Usuario"

### Asignar usuario a sitio

1. Ve a la pestaña "Asignaciones"
2. Selecciona:
   - Usuario: `vendedor (editor)`
   - Sitio: `Mi Tienda Online`
   - Rol: `editor`
3. Haz clic en "Asignar"

### Cambiar rol de usuario

1. Ve a la pestaña "Usuarios"
2. Haz clic en "Editar" en el usuario
3. Selecciona nuevo rol
4. Haz clic en "Guardar Cambios"

## 🐛 Troubleshooting

### Error: "No tienes permisos para esta acción"
- Asegúrate de estar logueado como admin
- Algunos roles no pueden gestionar usuarios

### Error: "Usuario o email ya registrado"
- El email o username ya existe en la base de datos
- Usa un valor único

### Error: "Rol inválido"
- El rol no existe en la base de datos
- Verifica los roles disponibles en la pestaña "Roles"

### Los datos no se cargan
- Verifica que el servidor esté corriendo: `ps aux | grep uvicorn`
- Revisa la consola del navegador (F12) para más detalles
- Comprueba que el token de acceso sea válido

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [JWT.io](https://jwt.io/)
- [Pydantic](https://pydantic-ai.jina.ai/)

## ✅ Checklist de Implementación

- [x] Modelos de base de datos (User, Role, SiteAssignment)
- [x] Esquemas Pydantic (UserCreate, RoleRead, etc.)
- [x] Autenticación JWT
- [x] CRUD de usuarios
- [x] CRUD de roles
- [x] Asignaciones de usuarios a sitios
- [x] Control de permisos (RBAC)
- [x] Interfaz HTML completa
- [x] Validación de entrada
- [x] Tests automatizados

## 🎯 Próximas Mejoras

- [ ] Importación/exportación en CSV
- [ ] Auditoría de cambios (quién cambió qué y cuándo)
- [ ] Cambio masivo de permisos
- [ ] Backup de usuarios
- [ ] 2FA (Autenticación de dos factores)
- [ ] Tokens con tiempo de vida específico

---

**Documento actualizado**: 16 de noviembre de 2025
**Versión**: 1.0
**Autor**: WebControl Studio Team
