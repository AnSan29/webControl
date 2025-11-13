#!/bin/bash

# Script de inicio rápido para Control de Sitios Productivos

echo "🎨 Iniciando Control de Sitios Productivos..."
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Verificar si existe .env
if [ ! -f ".env" ]; then
    echo "⚙️ Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env y configura:"
    echo "   - GITHUB_TOKEN (tu token de GitHub)"
    echo "   - GITHUB_USERNAME (tu usuario de GitHub)"
    echo "   - SECRET_KEY (clave secreta segura)"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Inicializar base de datos
echo "💾 Inicializando base de datos..."
cd backend
python -c "from database import init_db; init_db()"
cd ..

echo ""
echo "✅ Instalación completada!"
echo ""
echo "🚀 Para iniciar el servidor:"
echo "   cd backend"
echo "   uvicorn main:app --reload"
echo ""
echo "📊 El panel estará disponible en: http://localhost:8000"
echo ""
echo "🔐 Credenciales por defecto:"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
