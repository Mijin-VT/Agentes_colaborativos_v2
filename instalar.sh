#!/bin/bash
# ============================================================
# INSTALADOR - Sistema de Agentes Colaborativos v2.1 (Linux/macOS)
# ============================================================
# Ejecutar: chmod +x instalar.sh && ./instalar.sh
# Se recomienda: sudo ./instalar.sh
# ============================================================

set -e

PROYECTO_DIR="$HOME/AgentesColaborativos"
WORKSPACE_DIR="$HOME/agentes_workspace"
LOG_FILE="$PROYECTO_DIR/instalacion.log"

# Colores
ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
CYAN='\033[0;36m'
BLANCO='\033[1;37m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

header() {
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "  $1"
    echo -e "${CYAN}============================================================${NC}"
}

paso() {
    echo -e "  ${AMARILLO}→ $1${NC}"
}

ok() {
    echo -e "  ${VERDE}✅ $1${NC}"
}

error() {
    echo -e "  ${ROJO}❌ $1${NC}"
}

info() {
    echo -e "  ${BLANCO}ℹ️  $1${NC}"
}

# Detectar SO
if [[ "$OSTYPE" == "darwin"* ]]; then
    SO="macos"
    DETECTAR_PAQUETE="brew"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SO="linux"
    if command -v apt-get &> /dev/null; then
        DETECTAR_PAQUETE="apt"
    elif command -v dnf &> /dev/null; then
        DETECTAR_PAQUETE="dnf"
    elif command -v pacman &> /dev/null; then
        DETECTAR_PAQUETE="pacman"
    else
        DETECTAR_PAQUETE="desconocido"
    fi
else
    SO="desconocido"
fi

echo -e ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🤖 INSTALADOR - Agentes Colaborativos v2.1 🤖        ║${NC}"
echo -e "${CYAN}║                                                          ║${NC}"
echo -e "${CYAN}║   Este instalador configurará:                           ║${NC}"
echo -e "${CYAN}║     1. Python 3.x                                       ║${NC}"
echo -e "${CYAN}║     2. LM Studio (si está disponible)                   ║${NC}"
echo -e "${CYAN}║     3. Dependencias Python (openai)                     ║${NC}"
echo -e "${CYAN}║     4. 3 modelos de IA (~42 GB)                         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "  ${AMARILLO}⚠️  IMPORTANTE:${NC}"
echo -e "    - Necesitas ~50 GB de espacio libre en disco"
echo -e "    - La descarga de modelos puede tardar bastante"
echo -e ""

read -p "  ¿Deseas continuar con la instalación? (s/n): " confirmacion
if [[ ! "$confirmacion" =~ ^[sS] ]]; then
    echo -e "  ${AMARILLO}Instalación cancelada.${NC}"
    exit 0
fi

mkdir -p "$PROYECTO_DIR" "$WORKSPACE_DIR"
log "Instalación iniciada en $SO"

# ============================================================
# PASO 1: PYTHON
# ============================================================

header "PASO 1/4: Verificando Python"

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    ok "Python encontrado: $python_version"
    log "Python encontrado: $python_version"
else
    paso "Python no encontrado. Instalando..."

    if [[ "$SO" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install python3
            ok "Python instalado via Homebrew"
            log "Python instalado via Homebrew"
        else
            error "Homebrew no encontrado"
            info "Instala Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            info "O descarga Python de https://www.python.org/downloads/"
            read -p "  Presiona Enter para continuar..."
        fi
    elif [[ "$SO" == "linux" ]]; then
        if [[ "$DETECTAR_PAQUETE" == "apt" ]]; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
        elif [[ "$DETECTAR_PAQUETE" == "dnf" ]]; then
            sudo dnf install -y python3 python3-pip
        elif [[ "$DETECTAR_PAQUETE" == "pacman" ]]; then
            sudo pacman -S python python-pip
        fi
        ok "Python instalado via gestor de paquetes"
        log "Python instalado via gestor de paquetes"
    fi
fi

# ============================================================
# PASO 2: LM STUDIO
# ============================================================

header "PASO 2/4: Verificando LM Studio"

if [[ "$SO" == "linux" ]]; then
    if command -v lm-studio &> /dev/null || [ -f "$HOME/.local/bin/lm-studio" ]; then
        ok "LM Studio encontrado"
        log "LM Studio encontrado"
    else
        paso "LM Studio no encontrado"
        info "Descarga LM Studio de: https://lmstudio.ai"
        info "LM Studio para Linux está disponible como AppImage"
        info "Descarga, haz chmod +x y ejecuta"
        read -p "  Presiona Enter para continuar..."
    fi
elif [[ "$SO" == "macos" ]]; then
    if [ -d "/Applications/LM Studio.app" ]; then
        ok "LM Studio encontrado"
        log "LM Studio encontrado"
    else
        paso "LM Studio no encontrado"
        info "Descarga LM Studio de: https://lmstudio.ai"
        info "O instala via Homebrew: brew install --cask lm-studio"
        read -p "  Presiona Enter para continuar..."
    fi
fi

# ============================================================
# PASO 3: DEPENDENCIAS PYTHON
# ============================================================

header "PASO 3/4: Instalando dependencias Python"

paso "Instalando librerías openai y colorama..."
python3 -m pip install --upgrade pip
python3 -m pip install openai colorama
ok "openai y colorama instalados correctamente"
log "openai y colorama instalados"

# ============================================================
# PASO 4: MODELOS
# ============================================================

header "PASO 4/4: Modelos de IA"

echo -e ""
echo -e "  ${BLANCO}Los 3 modelos que necesitas son:${NC}"
echo -e ""
echo -e "  ${CYAN}🤖 P-E-W Qwen3 4B Instruct 2507 Heretic${NC}"
echo -e "     Repo: bartowski/P-E-W-Qwen3-4B-Instruct-2507-Heretic-GGUF"
echo -e "     Rol:  Coordinador (4B - rápido)"
echo -e ""
echo -e "  ${CYAN}🤖 P-E-W GPT Oss 20B Heretic${NC}"
echo -e "     Repo: bartowski/P-E-W-Gpt-Oss-20B-Heretic-GGUF"
echo -e "     Rol:  Analista (20B - razonamiento)"
echo -e ""
echo -e "  ${CYAN}🤖 Huihui Qwen3 Coder 30B A3B${NC}"
echo -e "     Repo: mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-GGUF"
echo -e "     Rol:  Desarrollador (30B - código)"
echo -e ""

info "Descarga los modelos manualmente en LM Studio:"
info "1. Abre LM Studio"
info "2. Ve a la pestaña de búsqueda (lupa)"
info "3. Busca cada repo y descarga la cuantización recomendada (Q4_K_M)"

log "Modelos requieren descarga manual"

# ============================================================
# COPIAR ARCHIVOS
# ============================================================

header "Configurando archivos del proyecto"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/agentes_colaborativos_v2.py" ]; then
    cp "$SCRIPT_DIR/agentes_colaborativos_v2.py" "$PROYECTO_DIR/"
    cp "$SCRIPT_DIR/config.json" "$PROYECTO_DIR/" 2>/dev/null || true
    ok "Scripts copiados a: $PROYECTO_DIR"
else
    info "Copia manualmente los archivos .py y config.json a: $PROYECTO_DIR"
fi

# Crear script ejecutable
cat > "$PROYECTO_DIR/ejecutar_agentes.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 agentes_colaborativos_v2.py
EOF
chmod +x "$PROYECTO_DIR/ejecutar_agentes.sh"

ok "Script ejecutable creado: $PROYECTO_DIR/ejecutar_agentes.sh"

# ============================================================
# RESUMEN
# ============================================================

echo -e ""
echo -e "${VERDE}============================================================${NC}"
echo -e "  ✅ INSTALACIÓN COMPLETADA"
echo -e "${VERDE}============================================================${NC}"
echo -e ""
echo -e "  📂 Proyecto en:  $PROYECTO_DIR"
echo -e "  📂 Workspace en: $WORKSPACE_DIR"
echo -e "  📝 Log en:       $LOG_FILE"
echo -e ""
echo -e "  ${AMARILLO}🚀 PARA EJECUTAR:${NC}"
echo -e "     Opción A: cd $PROYECTO_DIR && ./ejecutar_agentes.sh"
echo -e "     Opción B: cd $PROYECTO_DIR && python3 agentes_colaborativos_v2.py"
echo -e ""
echo -e "  ${AMARILLO}⚠️  ANTES DE EJECUTAR:${NC}"
echo -e "     1. Asegúrate de que LM Studio está abierto"
echo -e "     2. Los 3 modelos están cargados (READY)"
echo -e "     3. El servidor dice 'Status: Running'"
echo -e ""

log "Instalación completada"

echo -e "  Presiona Enter para cerrar..."
read
