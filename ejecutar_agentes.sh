#!/bin/bash
# ============================================================
# EJECUTAR - Agentes Colaborativos v2.1 (Linux/macOS)
# ============================================================
# Ejecutar: chmod +x ejecutar_agentes.sh && ./ejecutar_agentes.sh
# Requisitos:
#   - Python 3 instalado
#   - LM Studio abierto con servidor activo
#   - Al menos un modelo cargado
# ============================================================

echo ""
echo " ╔══════════════════════════════════════════════════════╗"
echo " ║       🤖 Agentes Colaborativos v2.1                  ║"
echo " ╚══════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "  ❌ Python3 no encontrado."
    echo "     Ejecuta instalar.sh primero."
    echo ""
    read -p "  Presiona Enter para salir..."
    exit 1
fi

echo "  ✅ Python encontrado: $(python3 --version)"

# Verificar openai y colorama
if ! python3 -c "import openai, colorama" 2>/dev/null; then
    echo "  ⚠️  Dependencias no encontradas. Instalando..."
    python3 -m pip install openai colorama
    echo ""
fi

# Verificar conexión con LM Studio
echo "  Verificando conexión con LM Studio..."
if ! python3 -c "from openai import OpenAI; c=OpenAI(base_url='http://localhost:1234/v1',api_key='lm-studio'); c.models.list(); print('OK')" 2>/dev/null; then
    echo ""
    echo "  ❌ No se puede conectar a LM Studio."
    echo ""
    echo "  Verifica que:"
    echo "    1. LM Studio está abierto"
    echo "    2. Ve a la pestaña 'Developer'"
    echo "    3. El servidor dice 'Status: Running'"
    echo "    4. Al menos un modelo está cargado (dice 'READY')"
    echo ""
    read -p "  ¿Quieres intentar de todas formas? (s/n): " continuar
    if [[ ! "$continuar" =~ ^[sS] ]]; then
        exit 1
    fi
else
    echo "  ✅ Conexión con LM Studio verificada"
fi

# Buscar el script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/agentes_colaborativos_v2.py" ]; then
    echo "  ✅ Todo listo. Iniciando agentes..."
    echo ""
    python3 "$SCRIPT_DIR/agentes_colaborativos_v2.py"
else
    echo "  ❌ No se encontró 'agentes_colaborativos_v2.py'"
    echo "     Ubicación buscada: $SCRIPT_DIR"
    echo ""
    echo "     Coloca el archivo .py en esta ubicación."
fi

echo ""
echo "  Sesión terminada."
read -p "  Presiona Enter para salir..."
