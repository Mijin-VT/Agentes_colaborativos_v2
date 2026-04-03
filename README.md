# 🤖 Agentes Colaborativos v2.1 / Collaborative Agents v2.1

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#requisitos--requirements)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-0.4.8+-orange)](https://lmstudio.ai/)

> **Sistema de inteligencia artificial local que permite que 3 modelos trabajen juntos como un equipo colaborativo.**
>
> **Local AI system that enables 3 models to work together as a collaborative team.**

---

## 🇪🇸 Español

### ¿Qué es esto?

Un sistema que permite que **3 modelos de inteligencia artificial** instalados en tu computador trabajen juntos como un equipo. Cada IA tiene un rol especializado y pueden **leer archivos, escribir código, ejecutar comandos y colaborar entre sí** para resolver tareas complejas.

✅ **100% local** — Nada se envía a internet
✅ **Sin cuentas ni suscripciones** — Todo funciona en tu máquina
✅ **Seguro** — Los agentes trabajan en una carpeta aislada con confirmación de acciones
✅ **Configurable** — Cambia modelos, URLs y límites sin tocar el código

### Funciones completas del sistema

#### 🤝 Colaboración entre agentes

| Función | Descripción |
|---------|-------------|
| **Planificación automática** | El coordinador descompone tareas en subtareas y asigna agentes |
| **Ejecución secuencial** | Los agentes trabajan 1 a la vez, leyendo el resultado del anterior |
| **Recuperación de errores** | Si un agente falla, otro toma su lugar automáticamente |
| **Contexto acumulado** | Cada agente recibe el historial completo del trabajo anterior |
| **Integración final** | El coordinador une todos los resultados en una respuesta coherente |

#### 📂 Gestión de archivos

| Función | Descripción |
|---------|-------------|
| **Leer archivos** | Los agentes leen archivos del workspace con validación de ruta |
| **Crear archivos** | Generan archivos nuevos con confirmación y vista previa |
| **Modificar archivos** | Sobrescribe con backup automático antes de cada cambio |
| **Listar workspace** | Explora la estructura de archivos y carpetas del proyecto |
| **Limpieza de contenido** | Extrae código de bloques markdown y elimina marcadores no deseados |

#### ⚡ Ejecución de comandos

| Función | Descripción |
|---------|-------------|
| **Ejecutar comandos** | Corre comandos del sistema con timeout de 2 minutos |
| **Análisis de riesgo** | Clasifica cada comando: bajo 🟢, medio 🟡, alto 🔴 |
| **Confirmación obligatoria** | El usuario debe aprobar cada comando antes de ejecutar |
| **Edición de comandos** | Permite corregir el comando antes de aprobarlo |
| **Detección de pipes** | Analiza recursivamente cada parte de un comando con pipe |

#### 🛡️ Seguridad integrada

| Función | Descripción |
|---------|-------------|
| **Workspace aislado** | Los agentes solo acceden a `~/agentes_workspace/` |
| **Rutas prohibidas** | Bloquea `C:\Windows`, `/usr/bin`, `/etc`, etc. |
| **Comandos prohibidos** | Bloquea `format`, `rm -rf /`, `shutdown`, `sudo`, etc. |
| **Backups automáticos** | Copia de seguridad antes de modificar cualquier archivo |
| **Logs de sesión** | Cada acción queda registrada con timestamp |
| **Limpieza al salir** | Elimina logs y backups al cerrar la aplicación |

#### 🎛️ Configuración externa

| Parámetro | Qué controla |
|-----------|-------------|
| `lm_studio_url` | URL del servidor LM Studio |
| `workspace` | Carpeta de trabajo de los agentes |
| `max_tokens` | Tokens máximos por respuesta |
| `max_context_tokens` | Tokens máximos de contexto |
| `temperature` | Temperatura por defecto |
| `modelos.*.nombre` | Nombre de cada modelo en LM Studio |
| `modelos.*.temperatura` | Temperatura individual por agente |
| `rutas_prohibidas` | Rutas bloqueadas del sistema |
| `comandos_prohibidos` | Comandos peligrosos bloqueados |

#### 📊 Gestión de contexto

| Función | Descripción |
|---------|-------------|
| **Token counting** | Estima tokens automáticamente (~1 token ≈ 3.5 caracteres) |
| **Truncación inteligente** | Preserva el system prompt, elimina mensajes antiguos |
| **Recuperación de contexto** | Si excede el límite, reduce y reintenta automáticamente |
| **Reintentos automáticos** | Hasta 2 reintentos con espera de 3 segundos |

#### 🎨 Interfaz visual

| Elemento | Descripción |
|----------|-------------|
| **Paneles decorativos** | Cajas con bordes Unicode alrededor del texto |
| **Barras de progreso** | Indicador visual `[████████░░░░] 66%` por fase |
| **Barras animadas** | Spinner rotatorio + progreso estimado durante generación |
| **Colores por agente** | Coordinador (cyan), Analista (magenta), Desarrollador (azul) |
| **Indicadores de carga** | "⏳ Coordinador pensando..." |
| **Indicadores de éxito** | "✅ COORDINADOR respondió en 2.3s" |
| **Iconos por flujo** | 🚀 Completo, 💻 Código, 💬 Debate, 💬 Chat libre |

#### 💬 Flujos de trabajo

| Flujo | Fases | Recuperación |
|-------|-------|-------------|
| 🎯 **Tarea completa** | Planificación → Ejecución → Integración | Agente alternativo si falla |
| 💻 **Desarrollo** | Especificaciones → Implementación → Revisión | Analista → Coordinador, Desarrollador → Analista |
| 💬 **Debate** | Análisis → Perspectiva técnica → Síntesis | Respaldo individual por agente |
| 💬 **Chat libre** | Conversación directa con selector visual | N/A |

#### 🌐 Acceso web indirecto

| Función | Descripción |
|---------|-------------|
| **Descarga con curl/wget** | El agente puede usar `curl` o `wget` para descargar contenido |
| **Confirmación requerida** | Clasificado como riesgo medio, requiere aprobación |
| **Contenido como referencia** | El HTML descargado se usa como fuente para el proyecto |

### Archivos incluidos

| Archivo | Descripción |
|---------|-------------|
| `INSTALAR.bat` | Instalador Windows (doble clic como administrador) |
| `instalar.ps1` | Lógica del instalador Windows (PowerShell, ejecutado por INSTALAR.bat) |
| `instalar.sh` | Instalador Linux/macOS (`chmod +x instalar.sh && ./instalar.sh`) |
| `EJECUTAR_AGENTES.bat` | Lanzador Windows (doble clic para usar) |
| `ejecutar_agentes.sh` | Lanzador Linux/macOS (`chmod +x ejecutar_agentes.sh && ./ejecutar_agentes.sh`) |
| `agentes_colaborativos_v2.py` | **Script principal** — El cerebro del sistema con 3 agentes colaborativos |
| `config.json` | **Configuración externa** — Modelos, URLs, workspace, tokens, comandos prohibidos |
| `test_agentes.py` | **Tests unitarios** — 24 tests de seguridad, análisis y gestión de contexto |
| `test_limpieza.py` | **Tests de limpieza** — Verifica extracción de código y limpieza de contenido |
| `test_progress_bar.py` | **Tests de progreso** — Verifica la barra de progreso animada |
| `.gitignore` | Excluye logs, backups, workspace y cachés del control de versiones |
| `DOCUMENTACION.md` | **Documentación completa en español** |
| `DOCUMENTATION_EN.md` | **Complete documentation in English** |

### Novedades en v2.1

- 🎛️ **Configuración externa** (`config.json`): Cambia modelos, URLs, workspace y límites sin tocar el código
- 🔄 **Recuperación de errores**: Si un agente falla, otro toma su lugar automáticamente
- 📊 **Gestión de contexto**: Token counting y truncación automática para evitar desbordamientos
- 🐧 **Soporte Linux/macOS**: Scripts `instalar.sh` y `ejecutar_agentes.sh`
- 🧪 **Tests unitarios**: 24 tests cubriendo seguridad, análisis de comandos y gestión de contexto
- 🎨 **Interfaz mejorada**: Paneles decorativos, barras de progreso animadas, indicadores de carga, colores por agente
- 🧹 **Limpieza de sesión**: Elimina logs y backups al cerrar para no acumular archivos
- 🪟 **Compatibilidad Windows**: UTF-8 forzado + colorama para colores y caracteres correctos
- 📁 **.gitignore**: Excluye logs, backups y archivos generados automáticamente

### Inicio rápido

```bash
# 1. Instalar (Windows: ejecutar como admin)
INSTALAR.bat

# 2. Abrir LM Studio → Cargar los 3 modelos → Developer → Start Server

# 3. Ejecutar el sistema
EJECUTAR_AGENTES.bat
```

### Menú principal

| Opción | Función |
|--------|---------|
| **1. Tarea completa** | Los 3 agentes colaboran secuencialmente en tu tarea |
| **2. Desarrollo código** | Especificaciones → Implementación → Revisión de código |
| **3. Debate/Evaluación** | 3 perspectivas sobre un tema con síntesis final |
| **4. Chat libre** | Conversación directa con el agente que elijas |
| **5. Ver workspace** | Explora archivos y carpetas del proyecto |
| **6. Salir** | Limpia sesión y cierra la aplicación |

### Requisitos del sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **GPU** | NVIDIA 12 GB VRAM | NVIDIA RTX 4080 Super (16 GB) |
| **RAM** | 32 GB | 48 GB |
| **Disco** | ~50 GB libres | SSD NVMe |
| **SO** | Windows 10/11, Linux, macOS | Windows 11, Ubuntu 22.04+, macOS 13+ |

### Modelos de IA

| Agente | Modelo | Tamaño | Rol | Temperatura |
|--------|--------|--------|-----|-------------|
| 🤖 Coordinador | Qwen3 4B Instruct Heretic | ~8 GB | Organiza, integra, decide | 0.3 |
| 🔍 Analista | GPT-OSS 20B Heretic | ~22 GB | Razona, planifica, analiza | 0.7 |
| 💻 Desarrollador | Qwen3 Coder 30B A3B | ~15 GB | Escribe código, ejecuta scripts | 0.5 |

### Si algo falla

Consulta la sección de solución de problemas en [`DOCUMENTACION.md`](DOCUMENTACION.md#12-solución-de-problemas)