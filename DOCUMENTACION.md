# 🤖 Sistema de Agentes Colaborativos v2.1

## Documentación Completa (Español)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#33-sistemas-operativos-soportados)
[![Tests](https://img.shields.io/badge/Tests-24%20unitarios-brightgreen)](test_agentes.py)

---

## 1. ¿Qué es esto?

Un sistema que permite que **3 modelos de inteligencia artificial** instalados en tu computador trabajen juntos como un equipo. Cada IA tiene un rol especializado y pueden **leer archivos, escribir código, ejecutar comandos y colaborar entre sí** para resolver tareas complejas.

**Todo se ejecuta 100% local en tu máquina.** No se envía nada a internet. No se necesita cuenta ni suscripción.

### Características principales

- 🤝 **Colaboración real**: Los 3 agentes trabajan juntos, no de forma aislada
- 📂 **Gestión de archivos**: Leer, crear, modificar y listar archivos del workspace
- ⚡ **Ejecución de comandos**: Ejecutar comandos del sistema con tu confirmación
- 🛡️ **Seguridad integrada**: Comandos prohibidos, rutas bloqueadas, backups automáticos
- 🎛️ **Configuración externa**: Cambia modelos, URLs y límites sin tocar el código
- 🔄 **Recuperación de errores**: Si un agente falla, otro toma su lugar automáticamente
- 📊 **Gestión de contexto**: Token counting y truncación automática
- 🎨 **Interfaz visual**: Paneles decorativos, barras de progreso, colores por agente

### Novedades en v2.1

- **Configuración externa** (`config.json`): Cambia modelos, URLs, workspace y límites sin tocar el código
- **Recuperación de errores**: Si un agente falla, otro toma su lugar automáticamente
- **Gestión de contexto**: Token counting y truncación automática para evitar desbordamientos
- **Soporte Linux/macOS**: Scripts `instalar.sh` y `ejecutar_agentes.sh`
- **Tests unitarios**: 24 tests cubriendo seguridad, análisis de comandos y gestión de contexto
- **Interfaz mejorada**: Paneles decorativos, barras de progreso, indicadores de carga, colores por agente
- **Compatibilidad Windows**: UTF-8 forzado + colorama para que los colores y caracteres se vean bien
- **.gitignore**: Excluye logs, backups y archivos generados automáticamente

---

## 2. Descripción detallada de cada archivo

### 2.1 `INSTALAR.bat`

**Tipo:** Archivo ejecutable de Windows (Batch)
**Función:** Puerta de entrada al instalador. Configura UTF-8 (`chcp 65001`) y lanza `instalar.ps1`.

**Qué hace exactamente:**
- Configura la consola en UTF-8 para que los caracteres especiales se vean bien
- Verifica privilegios de administrador
- Ejecuta `instalar.ps1` con política `Bypass`

---

### 2.2 `instalar.ps1`

**Tipo:** Script de PowerShell
**Función:** Instalador real para Windows. Configura UTF-8 e instala todo paso a paso.

**Qué hace exactamente (en orden):**

1. **Configura UTF-8:** `[Console]::OutputEncoding = UTF8` para que los caracteres se vean bien.
2. **Verifica/instala Python:** Busca `python`. Si no existe, lo instala via `winget`.
3. **Verifica/instala Windows Terminal:** Busca `Microsoft.WindowsTerminal`. Si no existe, lo instala.
4. **Verifica/instala LM Studio:** Busca el ejecutable. Si no existe, lo instala via `winget` o da enlace.
5. **Instala dependencias Python:** Ejecuta `pip install openai colorama`. **colorama** es esencial para que los colores funcionen en Windows.
6. **Descarga los 3 modelos:** Si `lms` está disponible, descarga automática. Si no, muestra los nombres.
7. **Configura el servidor:** Intenta cargar modelos y activar servidor via CLI.
8. **Copia archivos y crea acceso directo:** Copia `agentes_colaborativos_v2.py` y `config.json` al proyecto.

**Todo queda registrado en:** `C:\Users\TuNombre\AgentesColaborativos\instalacion.log`

---

### 2.3 `instalar.sh` (NUEVO en v2.1)

**Tipo:** Script de Bash (Linux/macOS)
**Función:** Instalador para sistemas Unix. Detecta automáticamente el SO y usa el gestor de paquetes apropiado.

**Qué hace exactamente (en orden):**

1. **Detecta el SO:** Linux (apt, dnf, pacman) o macOS (Homebrew).
2. **Verifica/instala Python:** Usa el gestor de paquetes del SO.
3. **Verifica LM Studio:** Busca instalación existente o da instrucciones.
4. **Instala dependencias:** `python3 -m pip install openai colorama`.
5. **Muestra los modelos necesarios:** Lista los 3 modelos con sus repos.
6. **Copia archivos:** Script principal y `config.json` al directorio del proyecto.
7. **Crea script ejecutable:** Genera `ejecutar_agentes.sh`.

**Ejecutar:** `chmod +x instalar.sh && ./instalar.sh` (o `sudo` para instalar software).

---

### 2.4 `EJECUTAR_AGENTES.bat`

**Tipo:** Archivo ejecutable de Windows (Batch)
**Función:** Lanza el sistema con verificaciones previas. Configura UTF-8.

**Qué hace exactamente (en orden):**

1. **Configura UTF-8:** `chcp 65001` para caracteres correctos.
2. **Verifica Python:** `python --version`.
3. **Verifica dependencias:** `import openai, colorama`. Si faltan, las instala.
4. **Verifica LM Studio:** Conecta a `http://localhost:1234`. Si falla, muestra checklist.
5. **Busca y ejecuta el script:** Lanza `python agentes_colaborativos_v2.py`.

---

### 2.5 `ejecutar_agentes.sh` (NUEVO en v2.1)

**Tipo:** Script de Bash (Linux/macOS)
**Función:** Lanzador para Unix con verificaciones previas.

**Qué hace exactamente (en orden):**

1. **Verifica Python3:** Comprueba que está disponible.
2. **Verifica dependencias:** `import openai, colorama`. Si faltan, las instala.
3. **Verifica LM Studio:** Conecta a `http://localhost:1234`.
4. **Ejecuta el script:** `python3 agentes_colaborativos_v2.py`.

**Ejecutar:** `chmod +x ejecutar_agentes.sh && ./ejecutar_agentes.sh`

---

### 2.6 `agentes_colaborativos_v2.py`

**Tipo:** Script de Python (el corazón del sistema)
**Función:** Contiene toda la lógica del sistema de agentes colaborativos.

**Estructura interna del archivo:**

**Sección COMPATIBILIDAD DE ENTORNO (~líneas 30-75):**
- `_init_entorno()`: Fuerza UTF-8 en stdout/stderr (`sys.stdout.reconfigure`)
- Intenta `colorama.init()` para colores en Windows
- Fallback: activa `ENABLE_VIRTUAL_TERMINAL_PROCESSING` via ctypes en Windows 10+

**Sección CARGA DE CONFIGURACIÓN (~líneas 78-130):**
- `_cargar_config()`: Busca y carga `config.json` desde el directorio del script o actual
- `LM_STUDIO_URL`, `WORKSPACE`, `MAX_TOKENS`, `MAX_CONTEXT_TOKENS` (desde config o valores por defecto)
- `RUTAS_PROHIBIDAS`, `COMANDOS_PROHIBIDOS`, `MODELOS` (desde config o valores por defecto)

**Sección COLORES Y UI (~líneas 135-175):**
- Clase `Color` con códigos ANSI (añadidos: `GRIS`, `SUBRAYADO`, `INVERTIDO`)
- `color()`: Aplica colores al texto
- `caja()`: Crea una caja decorativa alrededor del texto
- `separador()`: Línea separadora con caracteres Unicode (`─`, `═`)
- `spinner()`: Indicador de carga ("⏳ Pensando como...")
- `spinner_ok()`: Indicador de éxito ("✅ Respondió en X.Xs")
- `barra_progreso()`: Barra de progreso visual (`[████████░░░░░░░░░░░░░░░░░░░░] 33%`)

**Sección SISTEMA DE LOGS (~líneas 180-195):**
- Crea un archivo de log por sesión con marca de tiempo
- `log()` registra cada acción

**Sección GESTIÓN DE CONTEXTO (~líneas 200-245):**
- `estimar_tokens()`: Estima tokens (~1 token ≈ 3.5 caracteres)
- `truncar_contexto()`: Trunca historial si excede el límite, preserva system prompt

**Sección SISTEMA DE SEGURIDAD (~líneas 250-285):**
- `ruta_es_segura()`: Verifica ruta dentro del workspace (usa `os.path.normpath`)
- `comando_es_seguro()`: Verifica comando no prohibido (bloqueos específicos Windows/Unix)
- `hacer_backup()`: Crea copia de respaldo antes de modificar archivo

**Sección ANÁLISIS DE COMANDOS (~líneas 290-395):**
- `analizar_comando()`: Clasifica comando, asigna riesgo, genera ventajas/desventajas
- `mostrar_analisis_y_confirmar()`: Muestra info y espera decisión (sí/no/editar)

**Sección EJECUTOR DE ACCIONES (~líneas 400-515):**
- Clase `EjecutorAcciones`:
  - `leer_archivo()`: Lee archivos del workspace
  - `escribir_archivo()`: Crea/modifica archivos (preview, confirmación, backup)
  - `ejecutar_comando()`: Ejecuta comandos (timeout 2 min, bash en Unix)
  - `listar_workspace()`: Muestra árbol de archivos

**Sección PROMPTS DE SISTEMA (~líneas 520-590):**
- Define la "personalidad" de cada agente
- Incluye capacidades de acción disponibles
- Cada agente recibe prompt diferente según su rol

**Sección MOTOR DE AGENTES (~líneas 595-680):**
- `extraer_acciones()`: Regex para encontrar `[ACCION:TIPO]...[/ACCION]`
- `procesar_acciones()`: Ejecuta cada acción encontrada
- `llamar_agente()`: Envía mensaje al modelo, recibe respuesta, procesa acciones. **v2.1**: reintentos automáticos (hasta 2), gestión de contexto, detección errores de longitud, spinner de carga, respuesta en caja decorada, colores por agente

**Sección FLUJOS DE TRABAJO (~líneas 685-870):**
- `flujo_completo()`: 3 fases con barras de progreso. Recuperación: si agente falla, otro toma su lugar
- `flujo_codigo()`: 3 pasos con progreso. Recuperación: analista → coordinador, desarrollador → analista
- `flujo_debate()`: 3 opiniones con progreso. Recuperación individual por agente
- `flujo_libre()`: Chat directo con agente, selector visual con iconos

**Sección MENÚ PRINCIPAL (~líneas 875-970):**
- Header con caja decorativa
- Panel de agentes con colores individuales
- Panel de capacidades
- Panel de menú con opciones numeradas
- Info inferior en gris (workspace, SO, log)
- Input estilizado con prompt coloreado

**Sección EJECUCIÓN (~líneas 975-1010):**
- Header con versión
- Spinner de conexión a LM Studio
- Lista de modelos disponibles
- Lanza menú principal

---

### 2.7 `config.json` (NUEVO en v2.1)

**Tipo:** Archivo de configuración JSON
**Función:** Centraliza todos los parámetros configurables sin tocar el código Python.

| Clave | Qué controla | Valor por defecto |
|-------|-------------|-------------------|
| `lm_studio_url` | URL del servidor LM Studio | `http://localhost:1234/v1` |
| `workspace` | Carpeta de trabajo de los agentes | `~/agentes_workspace` |
| `max_tokens` | Tokens máximos por respuesta | `4096` |
| `max_context_tokens` | Tokens máximos de contexto | `3500` |
| `temperature` | Temperatura por defecto | `0.7` |
| `modelos.coordinador.nombre` | Nombre del modelo coordinador | `p-e-w_qwen3-4b-instruct-2507-heretic` |
| `modelos.coordinador.temperatura` | Temperatura del coordinador | `0.3` |
| `modelos.analista.nombre` | Nombre del modelo analista | `p-e-w_gpt-oss-20b-heretic` |
| `modelos.analista.temperatura` | Temperatura del analista | `0.7` |
| `modelos.desarrollador.nombre` | Nombre del modelo desarrollador | `huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1` |
| `modelos.desarrollador.temperatura` | Temperatura del desarrollador | `0.5` |
| `rutas_prohibidas` | Rutas bloqueadas | Lista de rutas de sistema |
| `comandos_prohibidos` | Comandos bloqueados | Lista de comandos peligrosos |

**Cómo editarlo:** Abre `config.json` con cualquier editor. Los cambios se aplican al reiniciar. Si no existe, se usan valores por defecto.

---

### 2.8 `test_agentes.py` (NUEVO en v2.1)

**Tipo:** Tests unitarios (Python)
**Función:** 24 tests que verifican seguridad, análisis de comandos, gestión de contexto y executor.

| Clase | Tests | Qué verifica |
|-------|-------|-------------|
| `TestRutaSegura` | 3 | Rutas seguras dentro del workspace, externas bloqueadas |
| `TestComandoSeguro` | 3 | Comandos peligrosos bloqueados, seguros pasan |
| `TestAnalizarComando` | 7 | Clasificación de riesgo correcta por tipo |
| `TestEstimarTokens` | 3 | Estimación de tokens razonable |
| `TestTruncarContexto` | 4 | Truncación correcta, system prompt preservado |
| `TestConfiguracion` | 2 | Valores por defecto sin config.json |
| `TestEjecutorAcciones` | 2 | Crear archivos y listar workspace |

**Ejecutar:** `python test_agentes.py`

---

### 2.9 `.gitignore` (NUEVO en v2.1)

**Tipo:** Archivo Git ignore
**Función:** Excluye del control de versiones archivos generados automáticamente.

**Excluye:**
- Logs (`agentes_workspace/.logs/`, `*.log`)
- Backups (`agentes_workspace/.backups/`, `*.bak`)
- Archivos de proyecto creados por agentes
- Cachés Python (`__pycache__/`, `*.pyc`)
- Entornos virtuales (`venv/`, `.venv/`)
- IDE (`.vscode/`, `.idea/`)
- SO (`.DS_Store`, `Thumbs.db`)

---

### 2.10 Archivos generados automáticamente

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| `instalacion.log` | `AgentesColaborativos/` | Registro del instalador |
| `sesion_YYYYMMDD_HHMMSS.log` | `agentes_workspace/.logs/` | Registro de cada sesión |
| `*.bak` | `agentes_workspace/.backups/` | Copias de seguridad automáticas |

---

## 3. Componentes del sistema

### 3.1 Los 3 agentes

| Agente | Modelo | ID en LM Studio | Tamaño | Rol | Color UI |
|--------|--------|------------------|--------|-----|----------|
| Coordinador | P-E-W Qwen3 4B Instruct 2507 Heretic | `p-e-w_qwen3-4b-instruct-2507-heretic` | 8.05 GB | Organiza, integra | Cyan |
| Analista | P-E-W GPT Oss 20B Heretic | `p-e-w_gpt-oss-20b-heretic` | 22.19 GB | Razona, planifica | Magenta |
| Desarrollador | Huihui Qwen3 Coder 30B A3B | `huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1` | 14.71 GB | Escribe código | Azul |

### 3.2 Software necesario

- **Python 3.10+** → Ejecuta el script principal
- **LM Studio 0.4.8+** → Hospeda y sirve los modelos
- **colorama** (Python) → Colores en terminal de Windows
- **Windows Terminal** (recomendado en Windows) → Soporte de colores y emojis

### 3.3 Sistemas operativos soportados

| SO | Instalador | Lanzador |
|----|-----------|----------|
| Windows 10/11 | `INSTALAR.bat` + `instalar.ps1` | `EJECUTAR_AGENTES.bat` |
| Linux (Ubuntu, Fedora, Arch) | `instalar.sh` | `ejecutar_agentes.sh` |
| macOS | `instalar.sh` | `ejecutar_agentes.sh` |

### 3.4 Hardware recomendado

- **GPU**: NVIDIA RTX 4080 Super (16 GB VRAM) o superior
- **RAM**: 48 GB (mínimo 32 GB)
- **Disco**: ~50 GB libres para los modelos
- **SO**: Windows 10/11, Linux o macOS

---

## 4. Instalación paso a paso

### 4.1 Instalación automática (Windows)

1. Descarga todos los archivos en una misma carpeta
2. **Clic derecho** en `INSTALAR.bat` → **Ejecutar como administrador**
3. Sigue las instrucciones

### 4.2 Instalación automática (Linux/macOS)

1. Descarga todos los archivos en una misma carpeta
2. Ejecuta: `chmod +x instalar.sh && ./instalar.sh`
3. Si necesitas instalar software: `sudo ./instalar.sh`

### 4.3 Instalación manual

#### Paso 1: Python

**Windows:** https://www.python.org/downloads/ → marca ✅ "Add Python to PATH"

**Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y python3 python3-pip`

**Linux (Fedora):** `sudo dnf install -y python3 python3-pip`

**macOS:** `brew install python3`

#### Paso 2: LM Studio

1. Ve a https://lmstudio.ai
2. Descarga e instala para tu SO
3. Abre LM Studio

#### Paso 3: Descargar modelos

En LM Studio, busca y descarga:

```
bartowski/P-E-W-Qwen3-4B-Instruct-2507-Heretic-GGUF
bartowski/P-E-W-Gpt-Oss-20B-Heretic-GGUF
mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Cuantización recomendada: **Q4_K_M** (balance), **Q6_K_L** (calidad), **BF16** (máxima).

#### Paso 4: Cargar modelos y activar servidor

1. En LM Studio → "Your Models" → carga cada modelo
2. Ve a **Developer** → **Start Server**
3. Verifica que los 3 digan **READY** en verde
4. Servidor debe mostrar: `Reachable at http://localhost:1234`

#### Paso 5: Instalar dependencias

```
pip install openai colorama
```

#### Paso 6: Configurar modelos (opcional)

Si los nombres en LM Studio difieren, edita `config.json` → sección `"modelos"` → campo `"nombre"`.

---

## 5. Cómo ejecutar

### Windows

**Opción A:** Doble clic en `EJECUTAR_AGENTES.bat`

**Opción B:** Acceso directo en el escritorio (si usaste el instalador)

**Opción C:** `cd C:\ruta\del\archivo && python agentes_colaborativos_v2.py`

### Linux/macOS

**Opción A:** `./ejecutar_agentes.sh`

**Opción B:** `cd /ruta/del/archivo && python3 agentes_colaborativos_v2.py`

---

## 6. Flujos de trabajo

### 6.1 Tarea completa (opción 1)

Los 3 agentes colaboran **secuencialmente** (1 a 1, no en paralelo):

```
TÚ → Coordinador (planifica) → Analista y/o Desarrollador (ejecutan) → Coordinador (integra) → TÚ
```

**Ejemplo:** "Crea una API REST en Python para gestionar una lista de tareas"

**Fases con progreso:**
- **FASE 1/3: PLANIFICACIÓN** `[██████████████████████████████] 33%` — Coordinador
- **FASE 2/3: EJECUCIÓN** `[██████████████████████████████] 66%` — Analista + Desarrollador
- **FASE 3/3: INTEGRACIÓN** `[██████████████████████████████] 100%` — Coordinador

**Recuperación de errores:** Si un agente falla, otro toma su lugar automáticamente.

**¿Por qué secuencial y no en paralelo?**
- Cada agente lee el resultado del anterior (contexto acumulado)
- Tú confirmas cada acción antes de que se ejecute
- LM Studio procesa 1 petición a la vez (API síncrona)
- **Ahorra VRAM**: solo 1 modelo activo a la vez (~16 GB máx vs ~32 GB en paralelo)

### 6.2 Desarrollo de código (opción 2)

```
Analista (especificaciones) → Desarrollador (implementación) → Coordinador (revisión)
```

**Ejemplo:** "Un juego de snake en Python con pygame"

**Recuperación:** Analista → Coordinador. Desarrollador → Analista.

### 6.3 Debate/evaluación (opción 3)

```
Analista (análisis) → Desarrollador (perspectiva técnica) → Coordinador (síntesis)
```

**Ejemplo:** "¿Es mejor usar React o Vue para un proyecto de dashboard?"

**Recuperación:** Cada agente tiene respaldo individual del coordinador.

### 6.4 Chat libre (opción 4)

Hablas directamente con un agente. Escribe "cambiar" para cambiar de agente. Selector visual con iconos y colores.

---

## 7. Sistema de acciones (archivos y comandos)

### 7.1 Acciones disponibles

| Acción | Qué hace |
|--------|----------|
| LEER | Lee un archivo del workspace |
| ESCRIBIR | Crea o modifica un archivo |
| EJECUTAR | Ejecuta un comando del sistema |
| LISTAR | Muestra el contenido del workspace |

### 7.2 Sistema de confirmación

Cada acción muestra: tipo, riesgo, ventajas, desventajas, reversibilidad.

Opciones: **[s]í** ejecuta, **[n]o** cancela, **[e]ditar** modifica el comando.

### 7.3 Niveles de riesgo

| Nivel | Color | Ejemplos |
|-------|-------|----------|
| BAJO | 🟢 Verde | Leer archivos, listar directorios, git status |
| MEDIO | 🟡 Amarillo | Crear archivos, instalar paquetes, copiar/mover |
| ALTO | 🔴 Rojo | Eliminar archivos, ejecutar scripts, comandos desconocidos |

---

## 8. Sistema de seguridad

### 8.1 Carpeta segura (workspace)

Todo se crea en: `C:\Users\TuNombre\agentes_workspace\` (Windows) o `~/agentes_workspace/` (Linux/macOS).
Los agentes **no pueden** acceder fuera de esta carpeta.

**¿Qué significa esto en la práctica?**

| Situación | Resultado |
|-----------|-----------|
| Leer `archivo.txt` dentro del workspace | ✅ El agente lee el archivo normalmente |
| Leer `C:\Users\Nombre\Documentos\proyecto.py` | ❌ **Error:** ruta fuera del workspace bloqueada |
| Usar `cd ..` para salir del workspace | ❌ **Bloqueado** por seguridad |
| Acceder a `C:\Windows`, `/usr/bin`, etc. | ❌ **Bloqueado** (rutas prohibidas) |

**¿Necesitas que el agente use un archivo externo?**
Cópialo al workspace primero:

```
# Windows
copy "C:\ruta\mi_archivo.py" "%USERPROFILE%\agentes_workspace\"

# Linux/macOS
cp /ruta/mi_archivo.py ~/agentes_workspace/
```

### 8.2 Comandos prohibidos (bloqueados siempre)

```
format, del /s, rm -rf /, rmdir /s, shutdown, reboot,
reg delete, taskkill /f /im explorer, net user, net localgroup,
powershell -enc, dd if=, mkfs
```

**Adicionalmente en Windows:** `reg add`, `sc config`, `schtasks`

**Adicionalmente en Linux/macOS:** `sudo`, `su -`, `visudo`, `passwd`

### 8.3 Backups automáticos

Antes de modificar cualquier archivo: `agentes_workspace/.backups/`

### 8.4 Logs de sesión

Cada acción registrada en: `agentes_workspace/.logs/`

### 8.5 Limpieza de contenido generado por IA

El sistema incluye una función `limpiar_respuesta()` que:
- **Extrae código de bloques markdown**: Si el agente genera código dentro de ```` ```python ```` o similar, extrae SOLO el código
- **Elimina textos no deseados**: Remueve marcadores como `[CONTENIDO DEL ARCHIVO]`, `[ARCHIVO]`, etc.
- **Formatea correctamente**: Elimina líneas vacías múltiples y formatea el resultado

---

## 9. Gestión de contexto (NUEVO en v2.1)

### 9.1 Estimación de tokens

El sistema estima automáticamente tokens: ~1 token ≈ 3.5 caracteres. Se muestra en cada llamada de agente.

### 9.2 Truncación automática

Si el contexto excede `max_context_tokens` (por defecto 3500):
- Se preserva siempre el **system prompt**
- Se eliminan los mensajes más **antiguos** primero
- Se mantienen los más **recientes**
- Se registra en el log

### 9.3 Recuperación de errores de contexto

Si la API devuelve "context_length_exceeded":
1. Reduce el límite a la mitad
2. Trunca con el nuevo límite
3. Reintenta la llamada

### 9.4 Cómo ajustar los límites

Edita `config.json`:
```json
{
    "max_tokens": 4096,
    "max_context_tokens": 3500
}
```

- **Aumentar** si tu modelo soporta contextos largos
- **Reducir** si tienes poca VRAM/RAM

---

## 10. Rendimiento y optimización

### Con RTX 4080 Super (16 GB VRAM) + 48 GB RAM

| Configuración | Rendimiento | VRAM utilizada |
|---------------|-------------|----------------|
| 3 modelos cargados | Funcional pero lento (3-10 tokens/s) | ~16 GB máx |
| 2 modelos (4B + uno grande) | Más rápido | ~12-14 GB |
| Contexto reducido (2048 vs 4096) | Mejora memoria | ~2-3 GB menos |

### VRAM por agente (ejecución secuencial)

| Agente | Modelo | VRAM aproximada |
|--------|--------|----------------|
| Coordinador (4B) | Qwen3 4B Instruct | ~4 GB |
| Analista (20B) | GPT-OSS 20B | ~12 GB |
| Desarrollador (30B) | Qwen3 Coder 30B A3B | ~16 GB |

**Nota importante:** Como los agentes se ejecutan **secuencialmente** (1 a la vez), solo el modelo activo consume VRAM. No hay sobrecarga por múltiples modelos en memoria.

### Optimizaciones recomendadas

1. **Carga selectiva:** Si no necesitas los 3 agentes, carga solo 2 en LM Studio
2. **Ajusta `max_context_tokens`:** Reducir a 2048 mejora rendimiento en hardware limitado
3. **Temperaturas individuales:** Cada agente tiene su temperatura en `config.json`
   - Coordinador: 0.3 (preciso y conciso)
   - Analista: 0.7 (creativo en análisis)
   - Desarrollador: 0.5 (equilibrado)
4. **Cierra otras aplicaciones:** Libera VRAM y RAM para los modelos
5. **Quantización recomendada:** Q4_K_M (balance), Q6_K_L (calidad), BF16 (máxima)

---

## 11. Estructura de archivos

```
📁 Proyecto Agentes Colaborativos/
│
├── 📄 agentes_colaborativos_v2.py    → Script principal (el cerebro del sistema)
├── 📄 config.json                    → Configuración externa (modelos, URLs, límites)
├── 📄 INSTALAR.bat                   → Instalador Windows (doble clic como admin)
├── 📄 instalar.ps1                   → Lógica del instalador Windows (PowerShell)
├── 📄 instalar.sh                    → Instalador Linux/macOS (Bash)
├── 📄 EJECUTAR_AGENTES.bat           → Lanzador Windows (doble clic para usar)
├── 📄 ejecutar_agentes.sh            → Lanzador Linux/macOS (Bash)
├── 📄 test_agentes.py                → Tests unitarios (24 tests)
├── 📄 test_limpieza.py               → Tests específicos de limpieza de contenido
├── 📄 test_progress_bar.py           → Tests de la barra de progreso animada
├── 📄 .gitignore                     → Git ignore
├── 📄 DOCUMENTACION.md               → Documentación completa en español (este archivo)
├── 📄 DOCUMENTATION_EN.md            → Documentación completa en inglés
└── 📄 README.md                      → Guía rápida bilingüe
│
📁 agentes_workspace/                  (se crea automáticamente al usar el sistema)
├── 📁 .backups/                       → Respaldos automáticos antes de modificar archivos
├── 📁 .logs/                          → Logs detallados de cada sesión
│   └── sesion_YYYYMMDD_HHMMSS.log     → Log individual con timestamp
└── 📁 (proyectos creados por agentes) → Archivos generados durante el trabajo
```

### Archivos generados automáticamente

| Archivo/ carpeta | Ubicación | Función |
|------------------|-----------|---------|
| `instalacion.log` | `AgentesColaborativos/` (Windows) | Registro completo del proceso de instalación |
| `sesion_*.log` | `agentes_workspace/.logs/` | Registro detallado de cada sesión de trabajo |
| `*.bak` | `agentes_workspace/.backups/` | Copias de seguridad automáticas antes de sobrescribir |
| `__pycache__/` | Directorio del proyecto | Caché de compilación de Python (excluido por .gitignore) |

---

## 12. Solución de problemas

### "No se puede conectar a LM Studio"
1. Abre LM Studio → Developer → verifica "Status: Running"
2. Al menos 1 modelo debe decir READY
3. Servidor en `http://localhost:1234`

### "Modelo no encontrado"
1. En Developer, copia el nombre exacto del modelo
2. Edita `config.json` → `"modelos"` → `"nombre"` del agente correspondiente

### "El agente no ejecuta las acciones"
- Sé explícito: "Crea un archivo llamado main.py con el código"
- El modelo de 30B es el más preciso para seguir formatos

### "Va muy lento"
1. Carga solo 2 modelos
2. Reduce `max_context_tokens` a 2048 en `config.json`
3. Cierra otras aplicaciones

### "pip install openai colorama falla"
```
python -m pip install --upgrade pip
python -m pip install openai colorama
```

### "Python no se reconoce como comando"
Reinstala Python marcando ✅ "Add Python to PATH"

### "Aparecen caracteres raros (←[93m, ΓòÉ)"
- El sistema ya configura UTF-8 automáticamente (`chcp 65001` en Windows)
- **colorama** está instalado para traducir códigos ANSI a Windows
- Si persiste, usa **Windows Terminal** en lugar de CMD clásico

### "Los tests fallan"
```
python test_agentes.py
```
Verifica que `config.json` tenga el formato correcto y el workspace sea accesible.

---

## 13. Personalización avanzada

### Desde config.json (recomendado)
- **Cambiar modelos:** Edita `"modelos"` → `"nombre"` de cada agente
- **Cambiar temperaturas:** Edita `"temperatura"` (0.0 = preciso, 1.0 = creativo)
- **Cambiar workspace:** Edita `"workspace"`
- **Otro servidor:** Cambia `"lm_studio_url"` (ej: `http://192.168.100.57:1234/v1`)
- **Ajustar tokens:** Cambia `"max_tokens"` y `"max_context_tokens"`
- **Comandos prohibidos:** Edita `"comandos_prohibidos"`
- **Rutas prohibidas:** Edita `"rutas_prohibidas"`

### Desde el código Python (avanzado)
- **Cambiar roles:** Edita `SYSTEM_PROMPTS` en el script
- **Añadir agentes:** Añade a `MODELOS` en `config.json` y crea su prompt en `SYSTEM_PROMPTS`
- **Cambiar reintentos:** Modifica `max_reintentos` en `llamar_agente()` (por defecto 2)

---

## 14. Glosario

| Término | Significado |
|---------|-------------|
| GGUF | Formato de modelos cuantizados, optimizado para CPU/GPU |
| VRAM | Memoria de la tarjeta gráfica (16 GB en la 4080 Super) |
| RAM | Memoria del sistema (48 GB) |
| Token | Unidad mínima de texto (~0.75 palabras en inglés, ~3.5 caracteres en español) |
| MoE | Mixture of Experts: activa solo partes del modelo, más eficiente |
| Cuantización | Reducción de precisión para menor consumo de memoria |
| API | Interfaz que permite a scripts comunicarse con LM Studio |
| Workspace | Carpeta segura donde los agentes trabajan |
| Offloading | Parte del modelo en RAM en vez de VRAM |
| Batch (.bat) | Archivo ejecutable de Windows con comandos |
| PowerShell | Terminal avanzada de Windows con scripting |
| Bash | Terminal de Linux/macOS con scripting |
| Contexto | Historial de mensajes enviados al modelo |
| Truncación | Eliminación de mensajes antiguos para mantener el contexto dentro del límite |
| Reintento | Intento automático tras un error (hasta 2 por defecto) |
| colorama | Librería Python que traduce códigos ANSI a colores nativos de Windows |
| UTF-8 | Codificación de caracteres que soporta emojis y símbolos Unicode |
| Ejecución secuencial | Los agentes se ejecutan 1 a 1, no en paralelo (ahorra VRAM) |
| Quantización Q4_K_M | Balance entre calidad y tamaño (recomendado) |
| Quantización Q6_K_L | Mayor calidad, mayor consumo de memoria |
| Quantización BF16 | Máxima calidad (Brain Float 16-bit) |
| Barra de progreso animada | Indicador visual que muestra el avance estimado durante la generación |
| Limpieza de contenido | Función que extrae código de bloques markdown y elimina marcadores no deseados |
| Sistema de confirmación | Mecanismo que requiere aprobación del usuario antes de cada acción |

---

*Sistema de Agentes Colaborativos v2.1 — Abril 2026*
