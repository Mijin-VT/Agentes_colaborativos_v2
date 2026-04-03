@echo off
:: ============================================================
:: INSTALADOR - Agentes Colaborativos v2.0
:: ============================================================
:: Doble clic para ejecutar. Abrirá PowerShell con el instalador.
:: Se recomienda: clic derecho → Ejecutar como administrador
:: ============================================================

title Instalador - Agentes Colaborativos v2.1

:: Configurar codificación UTF-8
chcp 65001 >nul 2>&1

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Instalador - Agentes Colaborativos v2.1           ║
echo  ╠══════════════════════════════════════════════════════╣
echo  ║   Esto instalará:                                    ║
echo  ║     - Python 3.x                                     ║
echo  ║     - Windows Terminal                                ║
echo  ║     - LM Studio (última versión)                     ║
echo  ║     - Dependencias Python                             ║
echo  ║     - 3 modelos de IA (~42 GB)                        ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Verificar si se ejecuta como admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠  No tienes privilegios de administrador.
    echo     Se recomienda: clic derecho → Ejecutar como administrador
    echo.
    set /p CONTINUAR="  ¿Continuar de todas formas? (s/n): "
    if /i not "%CONTINUAR%"=="s" exit /b 0
)

:: Ejecutar el script de PowerShell
echo  Iniciando instalación...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"

if %errorlevel% neq 0 (
    echo.
    echo  ❌ Hubo un error durante la instalación.
    echo     Revisa el log en: %USERPROFILE%\AgentesColaborativos\instalacion.log
    echo.
    pause
)
