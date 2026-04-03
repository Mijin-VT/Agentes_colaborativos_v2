@echo off
:: ============================================================
:: EJECUTAR - Agentes Colaborativos v2.0
:: ============================================================
:: Doble clic para iniciar el sistema de agentes.
:: Requisitos:
::   - Python instalado
::   - LM Studio abierto con servidor activo
::   - Al menos un modelo cargado
:: ============================================================

title 🤖 Agentes Colaborativos v2.1

:: Configurar codificación UTF-8 y colores
chcp 65001 >nul 2>&1
color 0F

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║       🤖 Agentes Colaborativos v2.0                  ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: --- Verificar Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ Python no encontrado.
    echo     Ejecuta INSTALAR.bat primero.
    echo.
    pause
    exit /b 1
)

:: --- Verificar que openai y colorama están instalados ---
python -c "import openai, colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠  Dependencias no encontradas. Instalando...
    pip install openai colorama
    echo.
)

:: --- Verificar conexión con LM Studio ---
echo  Verificando conexión con LM Studio...
python -c "from openai import OpenAI; c=OpenAI(base_url='http://localhost:1234/v1',api_key='lm-studio'); c.models.list(); print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ❌ No se puede conectar a LM Studio.
    echo.
    echo  Verifica que:
    echo    1. LM Studio está abierto
    echo    2. Ve a la pestaña "Developer"
    echo    3. El servidor dice "Status: Running" (toggle verde)
    echo    4. Al menos un modelo está cargado (dice "READY")
    echo.
    echo  ¿Quieres intentar ejecutar de todas formas?
    set /p CONTINUAR="  (s/n): "
    if /i not "%CONTINUAR%"=="s" exit /b 1
)

echo  ✅ Todo listo. Iniciando agentes...
echo.

:: --- Buscar el script ---
:: Primero buscar en el directorio actual
if exist "%~dp0agentes_colaborativos_v2.py" (
    python "%~dp0agentes_colaborativos_v2.py"
    goto :fin
)

:: Buscar en el directorio del proyecto
if exist "%USERPROFILE%\AgentesColaborativos\agentes_colaborativos_v2.py" (
    python "%USERPROFILE%\AgentesColaborativos\agentes_colaborativos_v2.py"
    goto :fin
)

:: No encontrado
echo  ❌ No se encontró 'agentes_colaborativos_v2.py'
echo     Ubicaciones buscadas:
echo       - %~dp0
echo       - %USERPROFILE%\AgentesColaborativos\
echo.
echo     Coloca el archivo .py en una de estas ubicaciones.

:fin
echo.
echo  Sesión terminada.
pause
