# WebControl Studio

Plataforma ligera para crear sitios estáticos de negocios locales, gestionarlos desde un dashboard Windster y publicarlos directo en GitHub Pages. Tras la limpieza del repositorio solo permanecen los componentes indispensables para ejecutar la aplicación.

## Características clave

- Editor visual con soporte para bloques de contenido, galerías y carga de imágenes.
- Plantillas base para cinco verticales (artesanías, cocina, adecuaciones, belleza y chivos).
- Gestión de usuarios con roles (superadmin, admin, owner) y avatars.
- Estadísticas por sitio, registro de últimas sesiones y vista consolidada en el dashboard.
- Publicación automática mediante integración con la API de GitHub.

## Requisitos previos

- Python 3.11 o superior.
- pip y virtualenv disponibles en la terminal.
- Cuenta de GitHub con un token clásico que tenga scopes `repo` y `workflow`.
- Sistema operativo Linux/macOS/WSL2 (Windows funciona usando PowerShell para los scripts `.bat`).

## Instalación rápida

```bash
git clone https://github.com/AnSan29/webControl.git
cd webControl
python -m venv .venv
source .venv/bin/activate  # En Windows usa .venv\Scripts\activate
pip install -r requirements.txt
```

### Variables de entorno

Crea un archivo `.env` usando `.env.example` como referencia.

| Clave | Descripción |
| --- | --- |
| `SECRET_KEY` | Clave para firmar JWT y CSRF tokens. |
| `HOST` / `PORT` | Host y puerto que usará Uvicorn. |
| `GITHUB_TOKEN` | Token personal para clonar/push y crear repositorios. |
| `GITHUB_USERNAME` | Cuenta que alojará los sitios publicados. |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Credenciales del superadmin inicial. |
| `DATABASE_URL` | Ruta SQLite, por defecto `sqlite:///./backend/db.sqlite3`. |

### Inicializar la base de datos

```bash
source .venv/bin/activate
python - <<'PY'
from backend.database import init_db
init_db()
PY
```

## Ejecutar el backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

El dashboard queda disponible en `http://localhost:8000`. Las credenciales por defecto son `admin@webcontrol.com` / `admin123` (cámbialas inmediatamente en entornos productivos).

Los scripts `start.sh` y `start.bat` ejecutan los comandos anteriores en Linux/macOS o Windows respectivamente.

## Pruebas automatizadas

```bash
source .venv/bin/activate
pytest tests
```

Los tests cubren autenticación, roles y regresiones recientes de avatar/último acceso. SQLite de pruebas vive en `tests/test_db.sqlite3`.

## Estructura mínima

```
backend/          # FastAPI, ORM y seeders
frontend/         # HTML Windster + assets estáticos
templates_base/   # Plantillas Jinja que reciben el contenido dinámico
scripts/          # Utilidades para automatizar cargas o auditorías
tests/            # Conjunto de pruebas Pytest
uploads/          # Archivos cargados por usuarios (servidos desde /images)
requirements.txt  # Dependencias del backend
start.sh|.bat     # Scripts de arranque rápido
verify.sh         # Health-check básico (opcional)
```

El resto del repositorio quedó libre de documentación histórica, plantillas duplicadas y archivos temporales para reducir el peso de `main`.

## Flujo funcional

1. Inicia sesión como superadmin.
2. Crea un sitio seleccionando uno de los modelos base.
3. Personaliza contenido, galerías y colores dentro del editor visual.
4. Sube assets (logos, banners) mediante el uploader integrado; se guardan en `uploads/` y se sirven como `/images/<archivo>`.
5. Publica desde el dashboard; el servicio clona el repositorio del cliente y hace push al branch `gh-pages`.
6. Supervisa estadísticas y últimos accesos desde el dashboard Windster.

## Despliegue y buenas prácticas

- Nunca compartas el `.env` con credenciales reales en un commit público.
- Configura un token de GitHub con vigencia limitada y revísalo periódicamente.
- Para entornos de producción usa un reverse proxy (Nginx/Caddy) que termine TLS y re-direccione hacia Uvicorn/Gunicorn.
- Programa tareas de backup para `backend/db.sqlite3` y la carpeta `uploads/` si necesitas conservar los assets.

## Documentación en inglés

Se agregó `README_en.md` con la misma información para equipos bilingües.

## Licencia

Proyecto distribuido bajo licencia MIT. Se aceptan issues y pull requests a través de GitHub.
