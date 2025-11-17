@echo off
REM Script de inicio rápido para Windows

echo Iniciando Control de Sitios Productivos...
echo.

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Verificar si existe .env
if not exist ".env" (
    echo Creando archivo .env desde .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env y configura:
    echo    - GITHUB_TOKEN tu token de GitHub
    echo    - GITHUB_USERNAME tu usuario de GitHub
    echo    - SECRET_KEY clave secreta segura
    echo.
    pause
)

REM Inicializar base de datos
echo Inicializando base de datos...
cd backend
python -c "from database import init_db; init_db()"
cd ..

echo.
echo Instalacion completada!
echo.
echo Para iniciar el servidor:
echo    cd backend
echo    uvicorn main:app --reload
echo.
echo El panel estara disponible en: http://localhost:8000
echo.
echo Credenciales por defecto:
echo    Email: admin@webcontrol.com
echo    Password: admin123
echo.
pause
