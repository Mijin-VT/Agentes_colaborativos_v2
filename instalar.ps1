# ============================================================
# INSTALADOR - Sistema de Agentes Colaborativos v2.1
# ============================================================
# Este script instala todo lo necesario:
#   1. Python (si no está instalado)
#   2. Windows Terminal (si no está instalado)
#   3. LM Studio (última versión)
#   4. Dependencias de Python (openai, colorama)
#   5. Descarga los 3 modelos de IA
#   6. Carga los modelos y activa el servidor
#
# Ejecutar como Administrador para instalar software del sistema.
# ============================================================

# Configurar UTF-8 para la consola
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"

# --- Configuración ---
$PROYECTO_DIR = "$env:USERPROFILE\AgentesColaborativos"
$WORKSPACE_DIR = "$env:USERPROFILE\agentes_workspace"
$LOG_FILE = "$PROYECTO_DIR\instalacion.log"

# Modelos a descargar (formato: "usuario/repositorio" de Hugging Face)
$MODELOS = @(
    @{
        Nombre = "P-E-W Qwen3 4B Instruct 2507 Heretic"
        Repo   = "bartowski/P-E-W-Qwen3-4B-Instruct-2507-Heretic-GGUF"
        Rol    = "Coordinador (4B - rápido)"
    },
    @{
        Nombre = "P-E-W GPT Oss 20B Heretic"
        Repo   = "bartowski/P-E-W-Gpt-Oss-20B-Heretic-GGUF"
        Rol    = "Analista (20B - razonamiento)"
    },
    @{
        Nombre = "Huihui Qwen3 Coder 30B A3B"
        Repo   = "mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-GGUF"
        Rol    = "Desarrollador (30B - código)"
    }
)

# --- Funciones auxiliares ---

function Write-Header {
    param([string]$Texto)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  $Texto" -ForegroundColor White
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Texto)
    Write-Host "  → $Texto" -ForegroundColor Yellow
}

function Write-Ok {
    param([string]$Texto)
    Write-Host "  ✅ $Texto" -ForegroundColor Green
}

function Write-Err {
    param([string]$Texto)
    Write-Host "  ❌ $Texto" -ForegroundColor Red
}

function Write-Info {
    param([string]$Texto)
    Write-Host "  ℹ️  $Texto" -ForegroundColor Gray
}

function Log {
    param([string]$Mensaje)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LOG_FILE -Value "[$timestamp] $Mensaje"
}

function Test-AdminPrivileges {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-CommandExists {
    param([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Wait-ForKeypress {
    Write-Host ""
    Write-Host "  Presiona cualquier tecla para continuar..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
}

# ============================================================
# INICIO
# ============================================================

Clear-Host
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🤖 INSTALADOR - Agentes Colaborativos v2.0 🤖        ║" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "║   Este instalador configurará:                           ║" -ForegroundColor Cyan
Write-Host "║     1. Python 3.x                                       ║" -ForegroundColor Cyan
Write-Host "║     2. Windows Terminal                                  ║" -ForegroundColor Cyan
Write-Host "║     3. LM Studio (última versión)                       ║" -ForegroundColor Cyan
Write-Host "║     4. Dependencias Python (openai)                     ║" -ForegroundColor Cyan
Write-Host "║     5. 3 modelos de IA (~42 GB)                         ║" -ForegroundColor Cyan
Write-Host "║     6. Servidor LM Studio activado                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "    - Necesitas ~50 GB de espacio libre en disco" -ForegroundColor Yellow
Write-Host "    - La descarga de modelos puede tardar bastante" -ForegroundColor Yellow
Write-Host "    - Se recomienda ejecutar como Administrador" -ForegroundColor Yellow
Write-Host ""

# Verificar privilegios
if (-not (Test-AdminPrivileges)) {
    Write-Host "  ⚠️  No tienes privilegios de Administrador." -ForegroundColor Yellow
    Write-Host "     Algunas instalaciones podrían fallar." -ForegroundColor Yellow
    Write-Host "     Se recomienda: clic derecho → Ejecutar como administrador" -ForegroundColor Yellow
    Write-Host ""
}

$confirmacion = Read-Host "  ¿Deseas continuar con la instalación? (s/n)"
if ($confirmacion -notmatch "^[sS]") {
    Write-Host "  Instalación cancelada." -ForegroundColor Yellow
    exit 0
}

# Crear directorio del proyecto
New-Item -ItemType Directory -Path $PROYECTO_DIR -Force | Out-Null
New-Item -ItemType Directory -Path $WORKSPACE_DIR -Force | Out-Null
Log "Instalación iniciada"

# ============================================================
# PASO 1: PYTHON
# ============================================================

Write-Header "PASO 1/6: Verificando Python"

if (Test-CommandExists "python") {
    $pythonVersion = python --version 2>&1
    Write-Ok "Python encontrado: $pythonVersion"
    Log "Python encontrado: $pythonVersion"
} else {
    Write-Step "Python no encontrado. Instalando..."
    
    if (Test-CommandExists "winget") {
        Write-Step "Instalando Python via winget..."
        winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Python instalado correctamente"
            Log "Python instalado via winget"
            # Refrescar PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        } else {
            Write-Err "Error al instalar Python con winget"
            Write-Info "Descárgalo manualmente de https://www.python.org/downloads/"
            Write-Info "IMPORTANTE: Marca la casilla 'Add Python to PATH' durante la instalación"
            Wait-ForKeypress
        }
    } else {
        Write-Err "winget no disponible"
        Write-Info "Descarga Python manualmente de https://www.python.org/downloads/"
        Write-Info "IMPORTANTE: Marca la casilla 'Add Python to PATH'"
        Wait-ForKeypress
    }
}

# ============================================================
# PASO 2: WINDOWS TERMINAL
# ============================================================

Write-Header "PASO 2/6: Verificando Windows Terminal"

$wtInstalled = Get-AppxPackage -Name "Microsoft.WindowsTerminal" -ErrorAction SilentlyContinue

if ($wtInstalled) {
    Write-Ok "Windows Terminal ya está instalado (v$($wtInstalled.Version))"
    Log "Windows Terminal encontrado: v$($wtInstalled.Version)"
} else {
    Write-Step "Windows Terminal no encontrado. Instalando..."
    
    if (Test-CommandExists "winget") {
        winget install Microsoft.WindowsTerminal --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Windows Terminal instalado"
            Log "Windows Terminal instalado via winget"
        } else {
            Write-Err "Error al instalar Windows Terminal"
            Write-Info "Instálalo desde la Microsoft Store: busca 'Windows Terminal'"
            Wait-ForKeypress
        }
    } else {
        Write-Info "Instálalo desde la Microsoft Store: busca 'Windows Terminal'"
        Wait-ForKeypress
    }
}

# ============================================================
# PASO 3: LM STUDIO
# ============================================================

Write-Header "PASO 3/6: Verificando LM Studio"

# Buscar LM Studio en ubicaciones comunes
$lmStudioPaths = @(
    "$env:LOCALAPPDATA\LM-Studio\LM Studio.exe",
    "$env:LOCALAPPDATA\Programs\LM-Studio\LM Studio.exe",
    "$env:PROGRAMFILES\LM Studio\LM Studio.exe"
)

$lmStudioFound = $false
$lmStudioPath = ""

foreach ($path in $lmStudioPaths) {
    if (Test-Path $path) {
        $lmStudioFound = $true
        $lmStudioPath = $path
        break
    }
}

# También buscar el CLI de LM Studio
$lmsCliAvailable = Test-CommandExists "lms"

if ($lmStudioFound) {
    Write-Ok "LM Studio encontrado en: $lmStudioPath"
    Log "LM Studio encontrado: $lmStudioPath"
} else {
    Write-Step "LM Studio no encontrado. Instalando..."
    
    if (Test-CommandExists "winget") {
        Write-Step "Instalando LM Studio via winget (última versión)..."
        winget install LMStudio.LMStudio --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "LM Studio instalado"
            Log "LM Studio instalado via winget"
        } else {
            Write-Err "No se pudo instalar automáticamente"
            Write-Info "Descárgalo de: https://lmstudio.ai"
            Write-Info "Instálalo y vuelve a ejecutar este instalador"
            Wait-ForKeypress
        }
    } else {
        Write-Err "winget no disponible"
        Write-Info "Descarga LM Studio de: https://lmstudio.ai"
        Wait-ForKeypress
    }
}

# Activar el CLI de LM Studio
if (-not $lmsCliAvailable) {
    Write-Step "Configurando CLI de LM Studio (lms)..."
    Write-Info "Abre LM Studio manualmente → ve a Developer → activa el CLI"
    Write-Info "O ejecuta este comando cuando LM Studio esté abierto:"
    Write-Host '    npx lmstudio install-cli' -ForegroundColor White
    Log "CLI de LM Studio necesita configuración manual"
}

# ============================================================
# PASO 4: DEPENDENCIAS PYTHON
# ============================================================

Write-Header "PASO 4/6: Instalando dependencias Python"

Write-Step "Instalando librerías openai y colorama..."
try {
    python -m pip install --upgrade pip 2>&1 | Out-Null
    python -m pip install openai colorama 2>&1
    Write-Ok "openai y colorama instalados correctamente"
    Log "openai y colorama instalados"
} catch {
    Write-Err "Error al instalar dependencias: $_"
    Write-Info "Intenta manualmente: pip install openai colorama"
    Log "Error instalando dependencias: $_"
}

# ============================================================
# PASO 5: DESCARGAR MODELOS
# ============================================================

Write-Header "PASO 5/6: Modelos de IA"
Write-Host ""
Write-Host "  Los 3 modelos que necesitas son:" -ForegroundColor White
Write-Host ""

foreach ($modelo in $MODELOS) {
    Write-Host "  🤖 $($modelo.Nombre)" -ForegroundColor Cyan
    Write-Host "     Repo: $($modelo.Repo)" -ForegroundColor Gray
    Write-Host "     Rol:  $($modelo.Rol)" -ForegroundColor Gray
    Write-Host ""
}

if (Test-CommandExists "lms") {
    Write-Step "CLI de LM Studio detectado. Intentando descargar modelos..."
    
    foreach ($modelo in $MODELOS) {
        Write-Step "Descargando: $($modelo.Nombre)..."
        Write-Info "Esto puede tardar bastante según tu conexión"
        
        try {
            lms get $modelo.Repo 2>&1
            Write-Ok "$($modelo.Nombre) descargado"
            Log "Modelo descargado: $($modelo.Repo)"
        } catch {
            Write-Err "Error descargando $($modelo.Nombre)"
            Write-Info "Descárgalo manualmente en LM Studio: busca '$($modelo.Repo)'"
            Log "Error descargando $($modelo.Repo): $_"
        }
    }
} else {
    Write-Info "El CLI de LM Studio (lms) no está disponible."
    Write-Host ""
    Write-Host "  📥 DESCARGA MANUAL DE MODELOS:" -ForegroundColor Yellow
    Write-Host "  ─────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "  1. Abre LM Studio" -ForegroundColor White
    Write-Host "  2. Ve a la pestaña de búsqueda (icono de lupa)" -ForegroundColor White
    Write-Host "  3. Busca y descarga cada modelo:" -ForegroundColor White
    Write-Host ""
    
    foreach ($modelo in $MODELOS) {
        Write-Host "     Busca: $($modelo.Repo)" -ForegroundColor Cyan
        Write-Host "     → $($modelo.Rol)" -ForegroundColor Gray
        Write-Host ""
    }
    
    Log "Modelos requieren descarga manual"
}

# ============================================================
# PASO 6: CONFIGURAR SERVIDOR
# ============================================================

Write-Header "PASO 6/6: Configuración del servidor"

if (Test-CommandExists "lms") {
    Write-Step "Cargando modelos en LM Studio..."
    
    $modelosLMS = @(
        "p-e-w_qwen3-4b-instruct-2507-heretic",
        "p-e-w_gpt-oss-20b-heretic",
        "huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1"
    )
    
    foreach ($m in $modelosLMS) {
        Write-Step "Cargando: $m"
        try {
            lms load $m 2>&1
            Write-Ok "Cargado: $m"
        } catch {
            Write-Info "No se pudo cargar automáticamente: $m"
        }
    }
    
    Write-Step "Activando servidor..."
    try {
        lms server start 2>&1
        Write-Ok "Servidor activado en http://localhost:1234"
        Log "Servidor LM Studio activado"
    } catch {
        Write-Info "No se pudo activar automáticamente"
    }
} else {
    Write-Host ""
    Write-Host "  📋 CONFIGURACIÓN MANUAL DEL SERVIDOR:" -ForegroundColor Yellow
    Write-Host "  ─────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "  1. Abre LM Studio" -ForegroundColor White
    Write-Host "  2. Carga los 3 modelos (clic en cada uno en 'Your Models')" -ForegroundColor White
    Write-Host "  3. Ve a la pestaña 'Developer'" -ForegroundColor White
    Write-Host "  4. Haz clic en 'Start Server'" -ForegroundColor White
    Write-Host "  5. Verifica que diga 'Status: Running' con el toggle verde" -ForegroundColor White
    Write-Host "  6. Los 3 modelos deben aparecer como 'READY'" -ForegroundColor White
    Write-Host ""
    Log "Servidor requiere configuración manual"
}

# ============================================================
# COPIAR ARCHIVOS DEL PROYECTO
# ============================================================

Write-Header "Configurando archivos del proyecto"

# Copiar el script principal al directorio del proyecto
$scriptSource = Join-Path $PSScriptRoot "agentes_colaborativos_v2.py"
$scriptDest = Join-Path $PROYECTO_DIR "agentes_colaborativos_v2.py"

if (Test-Path $scriptSource) {
    Copy-Item $scriptSource $scriptDest -Force
    Write-Ok "Script copiado a: $scriptDest"
} else {
    Write-Info "Copia manualmente 'agentes_colaborativos_v2.py' a: $PROYECTO_DIR"
}

# Crear acceso directo en el escritorio
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Agentes Colaborativos.lnk"

try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "cmd.exe"
    $shortcut.Arguments = "/k cd /d `"$PROYECTO_DIR`" && python agentes_colaborativos_v2.py"
    $shortcut.WorkingDirectory = $PROYECTO_DIR
    $shortcut.Description = "Sistema de Agentes Colaborativos v2.0"
    $shortcut.Save()
    Write-Ok "Acceso directo creado en el escritorio"
    Log "Acceso directo creado: $shortcutPath"
} catch {
    Write-Info "No se pudo crear acceso directo: $_"
}

# ============================================================
# RESUMEN FINAL
# ============================================================

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host "  ✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green
Write-Host ""
Write-Host "  📂 Proyecto en:  $PROYECTO_DIR" -ForegroundColor White
Write-Host "  📂 Workspace en: $WORKSPACE_DIR" -ForegroundColor White
Write-Host "  📝 Log en:       $LOG_FILE" -ForegroundColor White
Write-Host ""
Write-Host "  🚀 PARA EJECUTAR:" -ForegroundColor Yellow
Write-Host "     Opción A: Doble clic en 'Agentes Colaborativos' en el escritorio" -ForegroundColor White
Write-Host "     Opción B: Doble clic en 'ejecutar_agentes.bat'" -ForegroundColor White
Write-Host "     Opción C: En terminal → cd $PROYECTO_DIR → python agentes_colaborativos_v2.py" -ForegroundColor White
Write-Host ""
Write-Host "  ⚠️  ANTES DE EJECUTAR:" -ForegroundColor Yellow
Write-Host "     1. Asegúrate de que LM Studio está abierto" -ForegroundColor White
Write-Host "     2. Los 3 modelos están cargados (READY)" -ForegroundColor White
Write-Host "     3. El servidor dice 'Status: Running'" -ForegroundColor White
Write-Host ""

Log "Instalación completada"

Write-Host "  Presiona cualquier tecla para cerrar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
