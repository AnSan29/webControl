#!/bin/bash

echo "🔍 Verificando instalación de WebControl Studio..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de errores
ERRORS=0

# Verificar Python
echo -n "Verificando Python 3.8+... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python no encontrado"
    ERRORS=$((ERRORS+1))
fi

# Verificar pip
echo -n "Verificando pip... "
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip instalado"
else
    echo -e "${RED}✗${NC} pip no encontrado"
    ERRORS=$((ERRORS+1))
fi

# Verificar Git
echo -n "Verificando Git... "
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    echo -e "${GREEN}✓${NC} Git $GIT_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Git no encontrado (necesario para GitHub Pages)"
fi

echo ""
echo "📂 Verificando estructura de archivos..."

# Verificar archivos críticos
FILES=(
    "backend/main.py"
    "backend/database.py"
    "backend/auth.py"
    "backend/models.json"
    "backend/utils/github_api.py"
    "backend/utils/template_engine.py"
    "frontend/login.html"
    "frontend/dashboard.html"
    "frontend/create-site.html"
    "templates_base/artesanias/index.html"
    "requirements.txt"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (faltante)"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""
echo "📦 Verificando dependencias Python..."

# Verificar si requirements.txt existe
if [ -f "requirements.txt" ]; then
    # Intentar importar módulos principales
    python3 -c "import fastapi" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} FastAPI instalado"
    else
        echo -e "${YELLOW}⚠${NC} FastAPI no instalado. Ejecuta: pip install -r requirements.txt"
    fi
    
    python3 -c "import uvicorn" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Uvicorn instalado"
    else
        echo -e "${YELLOW}⚠${NC} Uvicorn no instalado. Ejecuta: pip install -r requirements.txt"
    fi
    
    python3 -c "import sqlalchemy" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} SQLAlchemy instalado"
    else
        echo -e "${YELLOW}⚠${NC} SQLAlchemy no instalado. Ejecuta: pip install -r requirements.txt"
    fi
else
    echo -e "${RED}✗${NC} requirements.txt no encontrado"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "⚙️ Verificando configuración..."

# Verificar .env
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} Archivo .env existe"
    
    # Verificar variables críticas
    if grep -q "SECRET_KEY=" .env; then
        echo -e "${GREEN}✓${NC} SECRET_KEY configurado"
    else
        echo -e "${YELLOW}⚠${NC} SECRET_KEY no configurado"
    fi
    
    if grep -q "GITHUB_TOKEN=" .env; then
        echo -e "${GREEN}✓${NC} GITHUB_TOKEN configurado"
    else
        echo -e "${YELLOW}⚠${NC} GITHUB_TOKEN no configurado (opcional pero recomendado)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Archivo .env no existe. Copia .env.example a .env"
fi

echo ""
echo "🎨 Verificando plantillas..."

TEMPLATES=(
    "templates_base/artesanias/index.html"
    "templates_base/cocina/index.html"
    "templates_base/adecuaciones/index.html"
    "templates_base/belleza/index.html"
    "templates_base/chivos/index.html"
)

TEMPLATE_COUNT=0
for template in "${TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        TEMPLATE_COUNT=$((TEMPLATE_COUNT+1))
    fi
done

echo -e "${GREEN}✓${NC} $TEMPLATE_COUNT/5 plantillas encontradas"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Sistema verificado correctamente!${NC}"
    echo ""
    echo "🚀 Para iniciar el sistema ejecuta:"
    echo "   ./start.sh"
    echo ""
    echo "🌐 Luego abre tu navegador en:"
    echo "   http://localhost:8000"
    echo ""
else
    echo -e "${RED}✗ Se encontraron $ERRORS errores${NC}"
    echo ""
    echo "Por favor, corrige los errores antes de continuar."
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
