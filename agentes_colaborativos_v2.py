"""
Sistema de Agentes Colaborativos con LM Studio v2.1
=====================================================
Ahora con capacidad de:
  - Leer, crear y modificar archivos (en carpeta segura)
  - Ejecutar comandos del sistema (CON tu confirmación)
  - Explicar ventajas/desventajas antes de cada acción
  - Configuración externa via config.json
  - Gestión de contexto (token counting, truncación)
  - Recuperación de errores en flujos de trabajo

Requisitos:
  pip install openai

Configuración en LM Studio:
  1. Activa el servidor en Developer → Start Server
  2. Carga al menos un modelo
"""

from openai import OpenAI
import json
import time
import os
import subprocess
import shutil
import re
import math
import sys
import threading
import itertools
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================
# COMPATIBILIDAD DE COLORES Y CODIFICACIÓN EN WINDOWS
# ============================================================

def _init_entorno():
    """Inicializa colores y codificación UTF-8 en terminal."""
    # Forzar UTF-8 en stdout/stderr (Python 3.7+)
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    # Configurar colorama para colores
    try:
        import colorama
        colorama.init()
        return True
    except ImportError:
        pass
    # Fallback: activar VT processing en Windows 10+
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, mode)
            return True
        except Exception:
            pass
    return False

_init_entorno()

# ============================================================
# CARGA DE CONFIGURACIÓN EXTERNA
# ============================================================

def _cargar_config():
    """Carga config.json desde el directorio del script o directorio actual."""
    config_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
        os.path.join(os.getcwd(), "config.json"),
    ]
    for path in config_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

_config = _cargar_config()

LM_STUDIO_URL = _config.get("lm_studio_url", "http://localhost:1234/v1")
WORKSPACE = os.path.expanduser(_config.get("workspace", "~/agentes_workspace"))
BACKUPS_DIR = os.path.join(WORKSPACE, ".backups")
MAX_TOKENS = _config.get("max_tokens", 4096)
MAX_CONTEXT_TOKENS = _config.get("max_context_tokens", 3500)
RUTAS_PROHIBIDAS = _config.get("rutas_prohibidas", [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "/usr", "/bin", "/etc", "/boot", "/sys",
    os.path.expanduser("~\\AppData"),
    os.path.expanduser("~/.config"),
])
COMANDOS_PROHIBIDOS = _config.get("comandos_prohibidos", [
    "format", "del /s", "rm -rf /", "rm -rf ~", "rmdir /s",
    "shutdown", "reboot", "mkfs", "dd if=", "reg delete",
    ":(){:|:&};:", "fork bomb", "taskkill /f /im explorer",
    "net user", "net localgroup", "icacls",
    "powershell -enc", "base64 -d",
])

MODELOS = _config.get("modelos", {
    "coordinador": {
        "nombre": "p-e-w_qwen3-4b-instruct-2507-heretic",
        "descripcion": "Qwen3 4B - Coordina, resume y decide",
    },
    "analista": {
        "nombre": "p-e-w_gpt-oss-20b-heretic",
        "descripcion": "GPT Oss 20B - Análisis profundo y planificación",
    },
    "desarrollador": {
        "nombre": "huihui-qwen3-coder-30b-a3b-instruct-abliterated-i1",
        "descripcion": "Qwen3 Coder 30B - Especialista en código",
    },
})

# ============================================================
# COLORES PARA LA TERMINAL
# ============================================================

class Color:
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BLANCO = "\033[97m"
    GRIS = "\033[90m"
    NEGRITA = "\033[1m"
    SUBRAYADO = "\033[4m"
    INVERTIDO = "\033[7m"
    RESET = "\033[0m"

def color(texto, c):
    return f"{c}{texto}{Color.RESET}"

def caja(texto, ancho=60, borde_color=Color.CYAN, titulo=""):
    """Crea una caja decorativa alrededor del texto."""
    lineas = texto.split("\n")
    borde_sup = f"{color('┌' + '─' * (ancho - 2) + '┐', borde_color)}"
    if titulo:
        borde_sup = f"{color('┌' + '─' * (ancho - 2) + '┐', borde_color)}"
        titulo_linea = f"{color('│', borde_color)} {color(titulo, Color.NEGRITA)}"
        padding = ancho - len(titulo_linea.replace('\033[0m', '').replace('\033[1m', '').replace('\033[96m', '')) - 2
        # Simplified: just put title on the border
    resultado = [borde_sup]
    for linea in lineas:
        # Truncate long lines
        if len(linea) > ancho - 4:
            linea = linea[:ancho-7] + "..."
        padding = ancho - 4 - len(linea)
        resultado.append(f"{color('│', borde_color)} {linea}{' ' * padding} {color('│', borde_color)}")
    resultado.append(color('└' + '─' * (ancho - 2) + '┘', borde_color))
    return "\n".join(resultado)

def separador(ancho=60, char='─', c=Color.CYAN):
    """Crea una línea separadora."""
    return color(char * ancho, c)

def spinner(mensaje):
    """Muestra un indicador de carga simple."""
    print(f"\r{color('⏳', Color.AMARILLO)} {mensaje}...", end="", flush=True)

def spinner_ok(mensaje):
    print(f"\r{color('✅', Color.VERDE)} {mensaje}{' ' * 20}")

def barra_progreso(actual, total, ancho=30):
    """Muestra una barra de progreso."""
    if total == 0:
        pct = 100
    else:
        pct = int((actual / total) * 100)
    llenos = int(ancho * actual / max(total, 1))
    vacios = ancho - llenos
    barra = "█" * llenos + "░" * vacios
    return f"{color('[' + barra + ']', Color.CYAN)} {color(f'{pct}%', Color.AMARILLO)}"

def barra_progreso_animada(mensaje, evento_detencion):
    """Muestra una barra de progreso animada con porcentaje que avanza mientras el agente piensa."""
    caracteres = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    inicio = time.time()
    progreso = 0
    velocidad = 0.5  # Porcentaje de avance por ciclo
    
    while not evento_detencion.is_set():
        # Calcular progreso basado en tiempo transcurrido (estimación)
        tiempo_transcurrido = time.time() - inicio
        # Simular progreso que avanza lentamente hasta 95% (nunca llega a 100 hasta que termine)
        progreso = min(int((tiempo_transcurrido / 30) * 95), 95)  # Asume 30 segundos como máximo
        
        # Crear barra visual
        ancho_barra = 30
        llenos = int(ancho_barra * progreso / 100)
        vacios = ancho_barra - llenos
        barra = "█" * llenos + "░" * vacios
        
        # Spinner rotatorio
        spinner_char = caracteres[int(tiempo_transcurrido * 5) % len(caracteres)]
        
        # Tiempo transcurrido formateado
        if tiempo_transcurrido < 60:
            tiempo_str = f"{tiempo_transcurrido:.0f}s"
        else:
            mins = int(tiempo_transcurrido // 60)
            secs = int(tiempo_transcurrido % 60)
            tiempo_str = f"{mins}m{secs}s"
        
        print(f"\r{color(spinner_char, Color.AMARILLO)} {color(mensaje, Color.CYAN)} {color('[' + barra + ']', Color.CYAN)} {color(f'{progreso}%', Color.AMARILLO)} {color(f'({tiempo_str})', Color.GRIS)}", end="", flush=True)
        time.sleep(0.2)
    
    # Limpiar línea al finalizar
    print(f"\r{' ' * 120}\r", end="", flush=True)

# ============================================================
# SISTEMA DE LOGS
# ============================================================

LOG_FILE = None

def iniciar_log():
    global LOG_FILE
    os.makedirs(WORKSPACE, exist_ok=True)
    log_path = os.path.join(WORKSPACE, ".logs")
    os.makedirs(log_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = os.path.join(log_path, f"sesion_{timestamp}.log")

def log(mensaje: str):
    if LOG_FILE:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {mensaje}\n")

# ============================================================
# GESTIÓN DE CONTEXTO (token counting y truncación)
# ============================================================

def estimar_tokens(texto: str) -> int:
    """Estima tokens usando la regla: ~1 token ≈ 4 caracteres en inglés, ~3 en español."""
    if not texto:
        return 0
    return math.ceil(len(texto) / 3.5)

def truncar_contexto(mensajes: list, max_tokens: int = MAX_CONTEXT_TOKENS) -> list:
    """Trunca el historial de mensajes si excede el límite de tokens, preservando el system prompt."""
    if not mensajes:
        return mensajes

    system_prompt = mensajes[0] if mensajes[0]["role"] == "system" else None
    historial = mensajes[1:] if system_prompt else mensajes[:]

    tokens_system = estimar_tokens(system_prompt["content"]) if system_prompt else 0
    tokens_disponibles = max_tokens - tokens_system

    if tokens_disponibles <= 0:
        return [system_prompt] if system_prompt else []

    # Truncar desde el más antiguo, manteniendo los más recientes
    mensajes_truncados = []
    tokens_acumulados = 0
    for msg in reversed(historial):
        tokens_msg = estimar_tokens(msg["content"])
        if tokens_acumulados + tokens_msg > tokens_disponibles:
            break
        mensajes_truncados.insert(0, msg)
        tokens_acumulados += tokens_msg

    if system_prompt:
        mensajes_truncados.insert(0, system_prompt)

    if len(mensajes_truncados) < len(mensajes):
        tokens_total = estimar_tokens("".join(m["content"] for m in mensajes_truncados))
        log(f"CONTEXTO TRUNCADO: {len(mensajes)} → {len(mensajes_truncados)} mensajes ({tokens_total} tokens)")

    return mensajes_truncados

# ============================================================
# SISTEMA DE SEGURIDAD
# ============================================================

def ruta_es_segura(ruta: str) -> bool:
    ruta_abs = os.path.abspath(os.path.normpath(ruta))
    workspace_abs = os.path.abspath(os.path.normpath(WORKSPACE))
    if not ruta_abs.startswith(workspace_abs):
        return False
    for prohibida in RUTAS_PROHIBIDAS:
        prohibida_abs = os.path.abspath(os.path.normpath(os.path.expanduser(prohibida)))
        if ruta_abs.startswith(prohibida_abs):
            return False
    return True

def comando_es_seguro(comando: str) -> tuple:
    cmd_lower = comando.lower().strip()
    for prohibido in COMANDOS_PROHIBIDOS:
        if prohibido.lower() in cmd_lower:
            return False, f"Comando contiene '{prohibido}' que está en la lista de prohibidos"
    # Bloquear navegación fuera del workspace en todos los SO
    if ".." in comando and ("cd" in cmd_lower or "chdir" in cmd_lower):
        return False, "Intento de navegar fuera del workspace con '..'"
    # Bloquear pipes recursivamente
    if "|" in comando:
        partes = comando.split("|")
        for parte in partes:
            es_seguro, razon = comando_es_seguro(parte.strip())
            if not es_seguro:
                return False, f"Pipe a comando inseguro: {razon}"
    # Bloquear comandos específicos de Windows que no están en la lista
    if os.name == "nt" and any(cmd in cmd_lower for cmd in ["reg add", "sc config", "schtasks"]):
        return False, "Comando de sistema Windows bloqueado por seguridad"
    # Bloquear comandos específicos de Linux/macOS
    if os.name == "posix" and any(cmd in cmd_lower for cmd in ["sudo ", "su -", "visudo", "passwd"]):
        return False, "Comando de privilegios Unix/Linux bloqueado por seguridad"
    return True, "OK"

def hacer_backup(ruta: str):
    if os.path.exists(ruta):
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        nombre = os.path.basename(ruta)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUPS_DIR, f"{nombre}.{timestamp}.bak")
        shutil.copy2(ruta, backup_path)
        log(f"BACKUP: {ruta} → {backup_path}")
        return backup_path
    return None

# ============================================================
# ANÁLISIS DE COMANDOS
# ============================================================

def analizar_comando(comando: str) -> dict:
    cmd_lower = comando.lower().strip()
    analisis = {
        "comando": comando,
        "tipo": "desconocido",
        "ventajas": [],
        "desventajas": [],
        "riesgo": "medio",
        "reversible": True,
    }

    if any(cmd in cmd_lower for cmd in ["cat ", "type ", "more ", "head ", "tail ", "less "]):
        analisis["tipo"] = "📖 Lectura de archivo"
        analisis["ventajas"] = ["Solo lee, no modifica nada", "Permite verificar contenido antes de actuar"]
        analisis["desventajas"] = ["Si el archivo es muy grande, puede llenar la terminal"]
        analisis["riesgo"] = "bajo"

    elif any(cmd in cmd_lower for cmd in ["ls", "dir", "tree"]):
        analisis["tipo"] = "📂 Listado de directorio"
        analisis["ventajas"] = ["Solo lista, no modifica nada", "Útil para explorar la estructura"]
        analisis["desventajas"] = ["Ninguna significativa"]
        analisis["riesgo"] = "bajo"

    elif any(cmd in cmd_lower for cmd in ["mkdir", "touch", "echo ", ">>", "> "]):
        analisis["tipo"] = "📝 Creación/escritura de archivo"
        analisis["ventajas"] = ["Crea nuevos archivos o carpetas", "Permite guardar el trabajo"]
        analisis["desventajas"] = ["Si el archivo ya existe, '>' lo SOBRESCRIBE", "'>>' añade al final (más seguro)"]
        analisis["riesgo"] = "medio"
        if ">" in comando and ">>" not in comando:
            analisis["desventajas"].append("⚠️ Usa '>' que sobrescribe. Se hará backup automático")

    elif any(cmd in cmd_lower for cmd in ["rm ", "del ", "remove", "rmdir", "rd "]):
        analisis["tipo"] = "🗑️ Eliminación"
        analisis["ventajas"] = ["Limpia archivos innecesarios"]
        analisis["desventajas"] = ["⚠️ ELIMINA archivos permanentemente", "Se hará backup automático"]
        analisis["riesgo"] = "alto"
        analisis["reversible"] = False

    elif any(cmd in cmd_lower for cmd in ["cp ", "copy ", "mv ", "move ", "rename "]):
        analisis["tipo"] = "📋 Copiar/Mover archivo"
        analisis["ventajas"] = ["Organiza archivos del proyecto", "Copiar no destruye el original"]
        analisis["desventajas"] = ["Mover elimina el archivo de la ubicación original", "Si el destino ya existe, puede sobrescribirse"]
        analisis["riesgo"] = "medio"

    elif any(cmd in cmd_lower for cmd in ["pip install", "npm install", "apt install", "brew install"]):
        analisis["tipo"] = "📦 Instalación de paquete"
        analisis["ventajas"] = ["Instala dependencias necesarias para el proyecto"]
        analisis["desventajas"] = ["Descarga software de internet", "Puede instalar dependencias adicionales", "Verificar nombre del paquete"]
        analisis["riesgo"] = "medio"

    elif any(cmd in cmd_lower for cmd in ["python ", "node ", "bash ", "sh ", "./"]):
        analisis["tipo"] = "🚀 Ejecución de script"
        analisis["ventajas"] = ["Permite probar el código creado"]
        analisis["desventajas"] = ["El script podría hacer cualquier cosa", "Revisar el código antes de ejecutar"]
        analisis["riesgo"] = "alto"

    elif "git " in cmd_lower:
        analisis["tipo"] = "🔀 Git (control de versiones)"
        analisis["ventajas"] = ["Registra cambios en el código", "Permite revertir a versiones anteriores"]
        analisis["desventajas"] = ["'git push' sube código a internet", "'git reset --hard' puede perder cambios"]
        analisis["riesgo"] = "bajo" if "push" not in cmd_lower else "medio"

    elif any(cmd in cmd_lower for cmd in ["curl ", "wget ", "invoke-webrequest"]):
        analisis["tipo"] = "🌐 Descarga de internet"
        analisis["ventajas"] = ["Permite descargar recursos necesarios"]
        analisis["desventajas"] = ["Descarga archivos de internet (verificar URL)", "Podría descargar contenido no deseado"]
        analisis["riesgo"] = "medio"

    else:
        analisis["tipo"] = "❓ Comando no reconocido"
        analisis["ventajas"] = ["No se pudo analizar automáticamente"]
        analisis["desventajas"] = ["⚠️ Comando desconocido, revisar con cuidado"]
        analisis["riesgo"] = "alto"

    return analisis

def mostrar_analisis_y_confirmar(comando: str) -> bool:
    es_seguro, razon = comando_es_seguro(comando)
    if not es_seguro:
        print(f"\n{color('🚫 COMANDO BLOQUEADO', Color.ROJO)}")
        print(f"   Razón: {razon}")
        print(f"   Comando: {comando}")
        log(f"BLOQUEADO: {comando} - Razón: {razon}")
        return False

    analisis = analizar_comando(comando)
    color_riesgo = {"bajo": Color.VERDE, "medio": Color.AMARILLO, "alto": Color.ROJO}
    c = color_riesgo.get(analisis["riesgo"], Color.AMARILLO)

    print(f"\n{'─' * 60}")
    print(f"{color('⚡ UN AGENTE QUIERE EJECUTAR UN COMANDO', Color.NEGRITA)}")
    print(f"{'─' * 60}")
    print(f"  {color('Comando:', Color.CYAN)}  {comando}")
    print(f"  {color('Tipo:', Color.CYAN)}     {analisis['tipo']}")
    print(f"  {color('Riesgo:', Color.CYAN)}   {color(analisis['riesgo'].upper(), c)}")
    print()
    print(f"  {color('✅ VENTAJAS:', Color.VERDE)}")
    for v in analisis["ventajas"]:
        print(f"     + {v}")
    print(f"\n  {color('⚠️  DESVENTAJAS:', Color.AMARILLO)}")
    for d in analisis["desventajas"]:
        print(f"     - {d}")

    if not analisis["reversible"]:
        print(f"\n  {color('🔴 Esta acción NO es fácilmente reversible', Color.ROJO)}")
    else:
        print(f"\n  {color('🟢 Esta acción es reversible', Color.VERDE)}")

    print(f"{'─' * 60}")

    while True:
        respuesta = input(f"  {color('¿Ejecutar? [s]í / [n]o / [e]ditar comando: ', Color.NEGRITA)}").strip().lower()
        if respuesta in ["s", "si", "sí", "y", "yes"]:
            log(f"APROBADO: {comando}")
            return True
        elif respuesta in ["n", "no"]:
            log(f"RECHAZADO: {comando}")
            print(f"  {color('Comando cancelado.', Color.AMARILLO)}")
            return False
        elif respuesta in ["e", "editar", "edit"]:
            nuevo = input("  Escribe el comando corregido: ").strip()
            if nuevo:
                return mostrar_analisis_y_confirmar(nuevo)
            return False
        else:
            print("  Responde: s (sí), n (no), o e (editar)")

# ============================================================
# FUNCIONES DE LIMPIEZA DE CONTENIDO
# ============================================================

def limpiar_respuesta(texto: str) -> str:
    """
    Limpia el contenido de archivos generados por el agente IA.
    
    Si el agente genera código dentro de bloques markdown ```, extrae SOLO el código
    y elimina los marcadores markdown y textos como [CONTENIDO DEL ARCHIVO].
    
    Si no hay bloques markdown, elimina los textos [CONTENIDO DEL ARCHIVO] y similares.
    """
    # Primero, intentar extraer código de bloques markdown
    # Buscar patrón: ```cpp\n...código...\n```
    bloques_codigo = re.findall(r'```[a-zA-Z]*\n(.*?)```', texto, re.DOTALL)
    
    if bloques_codigo:
        # Si hay bloques de código, extraer SOLO el código (sin markdown)
        codigo_extraido = []
        for bloque in bloques_codigo:
            codigo_extraido.append(bloque.strip())
        
        # Unir todos los bloques de código extraídos
        resultado = '\n\n'.join(codigo_extraido)
        
        # Si también hay texto descriptivo fuera de los bloques, agregarlo
        texto_sin_bloques = re.sub(r'```[a-zA-Z]*\n.*?```', '', texto, flags=re.DOTALL).strip()
        texto_sin_bloques = re.sub(r'\[CONTENIDO DEL ARCHIVO\]:?\s*', '', texto_sin_bloques, flags=re.IGNORECASE)
        texto_sin_bloques = re.sub(r'\[CONTENIDO\]:?\s*', '', texto_sin_bloques, flags=re.IGNORECASE)
        texto_sin_bloques = re.sub(r'\[ARCHIVO\]:?\s*', '', texto_sin_bloques, flags=re.IGNORECASE)
        texto_sin_bloques = texto_sin_bloques.strip()
        
        if texto_sin_bloques and not resultado:
            resultado = texto_sin_bloques
        elif texto_sin_bloques and resultado:
            resultado = texto_sin_bloques + '\n\n' + resultado
        
        return resultado
    
    # Si NO hay bloques de código markdown, solo limpiar textos no deseados
    texto = re.sub(r'\[CONTENIDO DEL ARCHIVO\]:?\s*', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\[CONTENIDO\]:?\s*', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\[ARCHIVO\]:?\s*', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\[ARCHIVO GENERADO\]:?\s*', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'contenido del archivo:?\s*', '', texto, flags=re.IGNORECASE)
    
    # Limpiar líneas vacías múltiples
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()

# ============================================================
# EJECUTOR DE ACCIONES
# ============================================================

class EjecutorAcciones:
    def __init__(self):
        os.makedirs(WORKSPACE, exist_ok=True)
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        self.historial = []

    def leer_archivo(self, ruta: str) -> str:
        ruta_completa = os.path.join(WORKSPACE, ruta) if not os.path.isabs(ruta) else ruta
        if not ruta_es_segura(ruta_completa):
            return f"❌ Error: La ruta '{ruta}' está fuera del workspace seguro ({WORKSPACE})"
        if not os.path.exists(ruta_completa):
            return f"❌ Error: El archivo '{ruta}' no existe"
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                contenido = f.read()
            log(f"LEER: {ruta_completa}")
            return contenido
        except Exception as e:
            return f"❌ Error al leer: {e}"

    def escribir_archivo(self, ruta: str, contenido: str) -> str:
        ruta_completa = os.path.join(WORKSPACE, ruta) if not os.path.isabs(ruta) else ruta
        if not ruta_es_segura(ruta_completa):
            return f"❌ Error: La ruta '{ruta}' está fuera del workspace seguro ({WORKSPACE})"

        # LIMPIAR el contenido antes de mostrarlo y guardarlo
        contenido = limpiar_respuesta(contenido)

        accion = "SOBRESCRIBIR" if os.path.exists(ruta_completa) else "CREAR"
        print(f"\n{'─' * 60}")
        print(f"{color(f'📝 UN AGENTE QUIERE {accion} UN ARCHIVO', Color.NEGRITA)}")
        print(f"  {color('Archivo:', Color.CYAN)} {ruta_completa}")
        print(f"  {color('Tamaño:', Color.CYAN)}  {len(contenido)} caracteres, {contenido.count(chr(10))+1} líneas")

        lineas = contenido.split("\n")
        preview = "\n".join(lineas[:15])
        if len(lineas) > 15:
            preview += f"\n  ... (+{len(lineas)-15} líneas más)"
        print(f"\n  {color('Vista previa:', Color.CYAN)}")
        for linea in preview.split("\n"):
            print(f"    {color('│', Color.AZUL)} {linea}")

        print(f"\n  {color('✅ Ventajas:', Color.VERDE)}")
        print(f"     + Guarda el trabajo del agente en disco")
        print(f"     + Podrás editar el archivo después")
        if accion == "SOBRESCRIBIR":
            print(f"\n  {color('⚠️ Desventajas:', Color.AMARILLO)}")
            print(f"     - El archivo ya existe y será sobrescrito")
            print(f"     - Se creará backup automático")
        print(f"{'─' * 60}")

        respuesta = input(f"  {color(f'¿{accion}? [s]í / [n]o / [v]er todo: ', Color.NEGRITA)}").strip().lower()
        if respuesta in ["v", "ver"]:
            print(f"\n{color('Contenido completo:', Color.CYAN)}")
            print(contenido)
            respuesta = input(f"\n  {color(f'¿{accion}? [s]í / [n]o: ', Color.NEGRITA)}").strip().lower()

        if respuesta not in ["s", "si", "sí", "y", "yes"]:
            log(f"RECHAZADO escribir: {ruta_completa}")
            return "❌ Cancelado por el usuario"

        try:
            if os.path.exists(ruta_completa):
                backup = hacer_backup(ruta_completa)
                print(f"  {color(f'💾 Backup: {backup}', Color.VERDE)}")
            directorio = os.path.dirname(ruta_completa)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write(contenido)
            log(f"ESCRITO: {ruta_completa} ({len(contenido)} chars)")
            return f"✅ Archivo guardado: {ruta_completa}"
        except Exception as e:
            return f"❌ Error al escribir: {e}"

    def ejecutar_comando(self, comando: str) -> str:
        if not mostrar_analisis_y_confirmar(comando):
            return "❌ Comando cancelado por el usuario"
        try:
            # Usar shell apropiado según SO
            shell_cmd = True
            if os.name == "posix":
                # En Linux/macOS, asegurar que usa bash
                comando = f"bash -c {comando!r}"
                shell_cmd = False
            resultado = subprocess.run(
                comando, shell=shell_cmd, cwd=WORKSPACE,
                capture_output=True, text=True, timeout=120,
            )
            salida = ""
            if resultado.stdout:
                salida += f"📤 Salida:\n{resultado.stdout}"
            if resultado.stderr:
                salida += f"\n⚠️ Errores:\n{resultado.stderr}"
            if resultado.returncode != 0:
                salida += f"\n❌ Código de salida: {resultado.returncode}"
            else:
                salida += f"\n✅ Ejecutado correctamente"
            log(f"EJECUTADO: {comando} (código: {resultado.returncode})")
            return salida if salida.strip() else "✅ Ejecutado (sin salida)"
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT: {comando}")
            return "❌ Comando cancelado: excedió el límite de 2 minutos"
        except Exception as e:
            log(f"ERROR: {comando} - {e}")
            return f"❌ Error: {e}"

    def listar_workspace(self) -> str:
        resultado = [f"📂 Workspace: {WORKSPACE}\n"]
        for root, dirs, files in os.walk(WORKSPACE):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            nivel = root.replace(WORKSPACE, "").count(os.sep)
            indentacion = "  " * nivel
            carpeta = os.path.basename(root)
            resultado.append(f"{indentacion}📁 {carpeta}/")
            for archivo in files:
                ruta_archivo = os.path.join(root, archivo)
                tamano = os.path.getsize(ruta_archivo)
                resultado.append(f"{indentacion}  📄 {archivo} ({tamano:,} bytes)")
        return "\n".join(resultado) if len(resultado) > 1 else "📂 Workspace vacío"

# ============================================================
# PROMPTS DE SISTEMA
# ============================================================

CAPACIDADES_TEXTO = f"""
CAPACIDADES DISPONIBLES:
Puedes solicitar acciones con el formato indicado:

1. LEER ARCHIVO:
   [ACCION:LEER] ruta/del/archivo.ext [/ACCION]

2. ESCRIBIR ARCHIVO:
   [ACCION:ESCRIBIR] ruta/del/archivo.ext
   contenido del archivo aquí
   [/ACCION]

3. EJECUTAR COMANDO:
   [ACCION:EJECUTAR] comando aquí [/ACCION]

4. LISTAR ARCHIVOS:
   [ACCION:LISTAR] [/ACCION]

REGLAS:
- Todas las rutas son relativas al workspace: {WORKSPACE}
- NO puedes acceder a archivos fuera del workspace
- El usuario debe CONFIRMAR cada acción
- Explica POR QUÉ necesitas cada acción
"""

SYSTEM_PROMPTS = {
    "coordinador": f"""Eres el COORDINADOR del equipo de agentes IA. Tu trabajo es:
1. Recibir la tarea del usuario y descomponerla en subtareas
2. Decidir qué agente debe hacer cada parte (ANALISTA o DESARROLLADOR)
3. Revisar el trabajo final

{CAPACIDADES_TEXTO}

Responde en formato JSON:
{{
    "plan": "descripción general",
    "tareas": [
        {{"agente": "analista|desarrollador", "instruccion": "qué hacer", "orden": 1}}
    ],
    "nota": "consideraciones"
}}""",

    "analista": f"""Eres el ANALISTA del equipo. Tu trabajo es:
- Analizar problemas en profundidad
- Crear planes y especificaciones detalladas
- Evaluar pros y contras
- Revisar trabajo de otros agentes

{CAPACIDADES_TEXTO}

Sé exhaustivo y estructurado.""",

    "desarrollador": f"""Eres el DESARROLLADOR del equipo. Tu trabajo es:
- Escribir código limpio y documentado
- Implementar soluciones técnicas
- Depurar y optimizar

{CAPACIDADES_TEXTO}

IMPORTANTE: Cuando crees archivos de código, usa [ACCION:ESCRIBIR].
No solo muestres el código, GUÁRDALO en un archivo.""",

    "revisor_final": f"""Eres el COORDINADOR en REVISIÓN FINAL.
Integra todas las respuestas en un resultado coherente para el usuario.

{CAPACIDADES_TEXTO}""",
}

# ============================================================
# MOTOR DE AGENTES
# ============================================================

client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")
ejecutor = EjecutorAcciones()

def extraer_acciones(texto: str) -> list:
    acciones = []
    patron = r'\[ACCION:(LEER|ESCRIBIR|EJECUTAR|LISTAR)\](.*?)\[/ACCION\]'
    matches = re.findall(patron, texto, re.DOTALL)
    for tipo, contenido in matches:
        contenido = contenido.strip()
        if tipo == "LEER":
            acciones.append({"tipo": "leer", "ruta": contenido})
        elif tipo == "ESCRIBIR":
            lineas = contenido.split("\n", 1)
            ruta = lineas[0].strip()
            datos = lineas[1] if len(lineas) > 1 else ""
            acciones.append({"tipo": "escribir", "ruta": ruta, "contenido": datos})
        elif tipo == "EJECUTAR":
            acciones.append({"tipo": "ejecutar", "comando": contenido})
        elif tipo == "LISTAR":
            acciones.append({"tipo": "listar"})
    return acciones

def procesar_acciones(acciones: list) -> str:
    if not acciones:
        return ""
    resultados = []
    for i, accion in enumerate(acciones):
        print(f"\n{color(f'Acción {i+1}/{len(acciones)}:', Color.MAGENTA)}")
        if accion["tipo"] == "leer":
            resultado = ejecutor.leer_archivo(accion["ruta"])
        elif accion["tipo"] == "escribir":
            resultado = ejecutor.escribir_archivo(accion["ruta"], accion["contenido"])
        elif accion["tipo"] == "ejecutar":
            resultado = ejecutor.ejecutar_comando(accion["comando"])
        elif accion["tipo"] == "listar":
            resultado = ejecutor.listar_workspace()
        else:
            resultado = f"❌ Acción desconocida: {accion['tipo']}"
        resultados.append(f"[Resultado acción {i+1} ({accion['tipo']})]: {resultado}")
    return "\n\n".join(resultados)

def llamar_agente(
    agente: str,
    prompt_usuario: str,
    contexto_extra: Optional[str] = None,
    temperatura: float = None,
    ejecutar_acciones_flag: bool = True,
    max_reintentos: int = 2,
) -> str:
    modelo = MODELOS[agente]["nombre"]
    system_prompt = SYSTEM_PROMPTS.get(agente, SYSTEM_PROMPTS["analista"])

    # Usar temperatura del config si no se especifica
    if temperatura is None:
        temperatura = MODELOS[agente].get("temperatura", 0.7)

    mensajes = [{"role": "system", "content": system_prompt}]
    contenido = prompt_usuario
    if contexto_extra:
        contenido = f"[CONTEXTO DEL EQUIPO]\n{contexto_extra}\n\n[TU TAREA]\n{prompt_usuario}"
    mensajes.append({"role": "user", "content": contenido})

    # Gestionar contexto: truncar si excede el límite
    mensajes = truncar_contexto(mensajes, MAX_CONTEXT_TOKENS)

    # Colores por agente
    colores_agente = {
        "coordinador": Color.CYAN,
        "analista": Color.MAGENTA,
        "desarrollador": Color.AZUL,
    }
    c_agente = colores_agente.get(agente, Color.BLANCO)

    print(f"\n{separador()}")
    print(f"  🤖 {color(agente.upper(), c_agente)} {color(f'({MODELOS[agente]["descripcion"]})', Color.GRIS)}")
    print(f"  📦 Modelo: {color(modelo, Color.GRIS)}")
    tokens_est = estimar_tokens("".join(m["content"] for m in mensajes))
    print(f"  🔢 Tokens: {color(str(tokens_est), Color.AMARILLO)}")
    print(separador())

    # Animación de carga con barra de progreso
    evento_detencion = threading.Event()
    hilo_progreso = threading.Thread(
        target=barra_progreso_animada,
        args=(f"🧠 {agente.upper()} pensando...", evento_detencion),
        daemon=True
    )
    hilo_progreso.start()

    ultimo_error = None
    for intento in range(1, max_reintentos + 1):
        try:
            inicio = time.time()
            respuesta = client.chat.completions.create(
                model=modelo, messages=mensajes,
                temperature=temperatura, max_tokens=MAX_TOKENS,
            )
            duracion = time.time() - inicio
            
            # Detener la animación
            evento_detencion.set()
            hilo_progreso.join(timeout=1)
            
            texto = respuesta.choices[0].message.content
            
            # Limpiar la respuesta de bloques de código y [CONTENIDO DEL ARCHIVO]
            texto = limpiar_respuesta(texto)

            spinner_ok(f"✅ {agente.upper()} respondió en {duracion:.1f}s")

            # Mostrar respuesta en caja
            print(f"\n{caja(texto, ancho=65, borde_color=c_agente, titulo=f' {agente.upper()} ')}")

            if ejecutar_acciones_flag:
                acciones = extraer_acciones(texto)
                if acciones:
                    print(f"\n  {color(f'📋 {len(acciones)} acción(es) solicitada(s):', Color.AMARILLO)}")
                    for i, acc in enumerate(acciones):
                        print(f"    {color(f'{i+1}.', Color.CYAN)} {acc['tipo'].upper()}")
                    resultados = procesar_acciones(acciones)
                    if resultados:
                        print(f"\n{caja(resultados[:500], ancho=65, borde_color=Color.VERDE, titulo=' RESULTADOS ')}")
                        # Asegurar que la animación se detiene
                        evento_detencion.set()
                        hilo_progreso.join(timeout=0.5)
                        return texto + "\n\n[RESULTADOS DE ACCIONES]:\n" + resultados

            # Asegurar que la animación se detiene
            evento_detencion.set()
            hilo_progreso.join(timeout=0.5)
            return texto

        except Exception as e:
            ultimo_error = e
            error_msg = str(e)
            
            # Detener la animación en caso de error
            evento_detencion.set()
            hilo_progreso.join(timeout=1)
            
            log(f"ERROR {agente} (intento {intento}/{max_reintentos}): {error_msg}")

            if "context_length" in error_msg.lower() or "maximum" in error_msg.lower():
                print(f"\r{color('⚠️ Contexto largo, truncando...', Color.AMARILLO)}{' ' * 20}")
                MAX_CONTEXT_TOKENS_GLOBAL = MAX_CONTEXT_TOKENS // 2
                mensajes = truncar_contexto(mensajes, MAX_CONTEXT_TOKENS_GLOBAL)
                # Reiniciar animación para el reintento
                evento_detencion.clear()
                hilo_progreso = threading.Thread(
                    target=barra_progreso_animada,
                    args=(f"🧠 {agente.upper()} reintentando...", evento_detencion),
                    daemon=True
                )
                hilo_progreso.start()
                continue

            if intento < max_reintentos:
                print(f"\r{color(f'⚠️ Reintento {intento}/{max_reintentos}...', Color.AMARILLO)}{' ' * 20}")
                time.sleep(3)
                # Reiniciar animación para el reintento
                evento_detencion.clear()
                hilo_progreso = threading.Thread(
                    target=barra_progreso_animada,
                    args=(f"🧠 {agente.upper()} reintentando...", evento_detencion),
                    daemon=True
                )
                hilo_progreso.start()
            else:
                print(f"\r{color(f'❌ Error: {ultimo_error}', Color.ROJO)}{' ' * 20}")

    return f"❌ Error tras {max_reintentos} intentos: {ultimo_error}"

# ============================================================
# FLUJOS DE TRABAJO
# ============================================================

def flujo_completo(tarea: str) -> str:
    print(f"\n{separador(65, '═', Color.CYAN)}")
    print(f"  {color('🚀 FLUJO COLABORATIVO COMPLETO', Color.NEGRITA)}")
    print(separador(65, '═', Color.CYAN))
    print(f"  📋 {color(tarea, Color.AMARILLO)}")
    print(f"  📂 {color(WORKSPACE, Color.GRIS)}")
    print(separador(65, '─', Color.GRIS))

    # Fase 1: Planificación
    print(f"\n  {color('FASE 1/3: PLANIFICACIÓN', Color.CYAN)} {barra_progreso(1, 3)}")
    plan_raw = llamar_agente("coordinador", tarea, ejecutar_acciones_flag=False)

    try:
        inicio_json = plan_raw.find("{")
        fin_json = plan_raw.rfind("}") + 1
        if inicio_json != -1:
            plan = json.loads(plan_raw[inicio_json:fin_json])
        else:
            raise json.JSONDecodeError("No JSON found", plan_raw, 0)
    except (json.JSONDecodeError, AttributeError):
        print(f"\n  {color('⚠️ Plan no válido, usando plan por defecto', Color.AMARILLO)}")
        plan = {"tareas": [
            {"agente": "analista", "instruccion": tarea, "orden": 1},
            {"agente": "desarrollador", "instruccion": tarea, "orden": 2},
        ]}

    # Fase 2: Ejecución con recuperación de errores
    print(f"\n  {color('FASE 2/3: EJECUCIÓN', Color.CYAN)} {barra_progreso(2, 3)}")
    resultados = []
    contexto_acumulado = f"Workspace: {WORKSPACE}\n"

    tareas = sorted(plan.get("tareas", []), key=lambda t: t.get("orden", 0))
    total_tareas = len(tareas)
    for idx, tarea_item in enumerate(tareas):
        agente = tarea_item.get("agente", "analista")
        instruccion = tarea_item.get("instruccion", tarea)
        if agente not in MODELOS:
            agente = "analista"

        print(f"\n  {color(f'Tarea {idx+1}/{total_tareas}:', Color.CYAN)} {instruccion[:60]}...")
        resultado = llamar_agente(agente, instruccion, contexto_extra=contexto_acumulado)

        # Recuperación: si el agente falla, intentar con otro agente
        if resultado.startswith("❌ Error"):
            print(f"\n  {color(f'⚠️ {agente} falló, usando agente alternativo...', Color.AMARILLO)}")
            agente_alt = "desarrollador" if agente != "desarrollador" else "analista"
            print(f"  {color(f'🔄 Reintentando con {agente_alt}...', Color.CYAN)}")
            resultado = llamar_agente(agente_alt, instruccion, contexto_extra=contexto_acumulado)
            log(f"RECUPERACIÓN: {agente} → {agente_alt} para tarea: {instruccion[:50]}...")

        resultados.append({"agente": agente, "resultado": resultado})
        contexto_acumulado += f"\n[{agente.upper()}]: {resultado}"

    # Fase 3: Integración
    print(f"\n  {color('FASE 3/3: INTEGRACIÓN', Color.CYAN)} {barra_progreso(3, 3)}")
    resumen = "\n\n".join([f"### {r['agente'].upper()}:\n{r['resultado']}" for r in resultados])

    final = llamar_agente(
        "coordinador",
        "Integra todo en una respuesta final coherente.",
        contexto_extra=f"TAREA: {tarea}\n\nRESULTADOS:\n{resumen}",
    )
    return final

def flujo_codigo(descripcion: str) -> str:
    print(f"\n{separador(65, '═', Color.MAGENTA)}")
    print(f"  {color('💻 FLUJO DE DESARROLLO', Color.NEGRITA)}")
    print(separador(65, '═', Color.MAGENTA))
    print(f"  📋 {color(descripcion, Color.AMARILLO)}")
    print(f"  📂 {color(WORKSPACE, Color.GRIS)}")
    print(separador(65, '─', Color.GRIS))

    # Paso 1: Especificaciones
    print(f"\n  {color('PASO 1/3: ESPECIFICACIONES', Color.MAGENTA)} {barra_progreso(1, 3)}")
    specs = llamar_agente("analista",
        f"Crea especificaciones técnicas para: {descripcion}. "
        f"Primero usa [ACCION:LISTAR][/ACCION] para ver qué hay en el workspace."
    )

    # Recuperación: si el analista falla, el coordinador hace las specs
    if specs.startswith("❌ Error"):
        print(f"\n  {color('⚠️ Analista falló, coordinador toma el relevo...', Color.AMARILLO)}")
        specs = llamar_agente("coordinador",
            f"Crea especificaciones técnicas para: {descripcion}"
        )

    # Paso 2: Implementación
    print(f"\n  {color('PASO 2/3: IMPLEMENTACIÓN', Color.MAGENTA)} {barra_progreso(2, 3)}")
    codigo = llamar_agente("desarrollador",
        f"Implementa según estas especificaciones. GUARDA todos los archivos con [ACCION:ESCRIBIR].",
        contexto_extra=f"Descripción: {descripcion}\nSpecs:\n{specs}",
    )

    # Recuperación: si el desarrollador falla, intentar con analista
    if codigo.startswith("❌ Error"):
        print(f"\n  {color('⚠️ Desarrollador falló, analista implementa...', Color.AMARILLO)}")
        codigo = llamar_agente("analista",
            f"Implementa el código para: {descripcion}",
            contexto_extra=f"Specs:\n{specs}",
        )

    # Paso 3: Revisión
    print(f"\n  {color('PASO 3/3: REVISIÓN', Color.MAGENTA)} {barra_progreso(3, 3)}")
    revision = llamar_agente("coordinador",
        "Revisa el trabajo. Lista los archivos creados. ¿Está completo?",
        contexto_extra=f"Specs:\n{specs}\nDesarrollo:\n{codigo}",
    )
    return revision

def flujo_debate(tema: str) -> str:
    print(f"\n{separador(65, '═', Color.AMARILLO)}")
    print(f"  {color('💬 FLUJO DE DEBATE', Color.NEGRITA)}")
    print(separador(65, '═', Color.AMARILLO))
    print(f"  📋 {color(tema, Color.AMARILLO)}")
    print(separador(65, '─', Color.GRIS))

    # Opinión del analista
    print(f"\n  {color('OPINIÓN 1/3: ANALISTA', Color.MAGENTA)} {barra_progreso(1, 3)}")
    opinion_analista = llamar_agente("analista", f"Da tu análisis profundo sobre: {tema}")

    # Recuperación: si analista falla, usar coordinador
    if opinion_analista.startswith("❌ Error"):
        print(f"\n  {color('⚠️ Analista falló, coordinador opina...', Color.AMARILLO)}")
        opinion_analista = llamar_agente("coordinador", f"Da tu análisis sobre: {tema}")

    # Opinión del desarrollador
    print(f"\n  {color('OPINIÓN 2/3: DESARROLLADOR', Color.AZUL)} {barra_progreso(2, 3)}")
    opinion_dev = llamar_agente("desarrollador",
        f"Desde una perspectiva técnica/práctica, opina sobre: {tema}",
        contexto_extra=f"El analista opinó:\n{opinion_analista}",
    )

    # Recuperación: si desarrollador falla, usar coordinador
    if opinion_dev.startswith("❌ Error"):
        print(f"\n  {color('⚠️ Desarrollador falló, coordinador opina...', Color.AMARILLO)}")
        opinion_dev = llamar_agente("coordinador",
            f"Desde una perspectiva técnica, opina sobre: {tema}",
            contexto_extra=f"El analista opinó:\n{opinion_analista}",
        )

    # Síntesis
    print(f"\n  {color('SÍNTESIS 3/3: COORDINADOR', Color.CYAN)} {barra_progreso(3, 3)}")
    sintesis = llamar_agente("coordinador",
        f"Sintetiza las opiniones del equipo sobre: {tema}",
        contexto_extra=f"Analista:\n{opinion_analista}\n\nDesarrollador:\n{opinion_dev}",
    )
    return sintesis

def flujo_libre():
    print(f"\n{separador(65, '═', Color.AMARILLO)}")
    print(f"  {color('💬 MODO LIBRE - Chat con agentes', Color.NEGRITA)}")
    print(separador(65, '═', Color.AMARILLO))
    print(f"  📂 {color(WORKSPACE, Color.GRIS)}")
    print(f"  {color("Escribe 'cambiar' para cambiar de agente", Color.GRIS)}")
    print(f"  {color("Escribe 'salir' para volver al menú", Color.GRIS)}")
    print(separador(65, '─', Color.GRIS))

    agentes = ["coordinador", "analista", "desarrollador"]
    colores_chat = [Color.CYAN, Color.MAGENTA, Color.AZUL]
    agente_actual = "desarrollador"
    idx_actual = 2

    print(f"\n  Agente: {color(agente_actual.upper(), colores_chat[idx_actual])}")

    while True:
        print(f"\n  {color('┌─', Color.GRIS)}")
        msg = input(f"  {color('│', Color.GRIS)} {color(f'[{agente_actual}]', colores_chat[idx_actual])} Tú: ").strip()
        print(f"  {color('└─', Color.GRIS)}")

        if msg.lower() == "salir":
            break
        elif msg.lower() == "cambiar":
            print(f"\n  {color('Elige agente:', Color.CYAN)}")
            for i, ag in enumerate(agentes):
                icono = ["📋", "🔍", "💻"][i]
                marca = " ← actual" if ag == agente_actual else ""
                print(f"    {color(f'{i+1}.', Color.CYAN)} {icono} {ag.capitalize()}{marca}")
            sel = input(f"  {color('Número: ', Color.NEGRITA)}").strip()
            if sel in ["1", "2", "3"]:
                idx_actual = int(sel) - 1
                agente_actual = agentes[idx_actual]
                print(f"  {color(f'→ {agente_actual.upper()}', Color.VERDE)}")
            continue
        if msg:
            llamar_agente(agente_actual, msg)

# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu_principal():
    iniciar_log()

    # Detectar SO para mostrar info apropiada
    so_info = "Windows" if os.name == "nt" else "Linux/macOS"

    # Header con estilo
    print()
    print(color('╔═══════════════════════════════════════════════════════════╗', Color.CYAN))
    print(color('║', Color.CYAN) + color('           🤖 AGENTES COLABORATIVOS v2.1 🤖              ', Color.NEGRITA) + color('║', Color.CYAN))
    print(color('╠═══════════════════════════════════════════════════════════╣', Color.CYAN))
    print(color('║', Color.CYAN) + color('  Sistema multi-agente local con LM Studio                ', Color.CYAN) + color('║', Color.CYAN))
    print(color('╚═══════════════════════════════════════════════════════════╝', Color.CYAN))
    print()

    # Panel de agentes
    print(color('  ┌─────────────────────────────────────────────────────┐', Color.CYAN))
    print(color('  │', Color.CYAN) + color('  EQUIPO DE AGENTES', Color.NEGRITA) + color(' ' * 30, Color.CYAN) + color('│', Color.CYAN))
    print(color('  ├─────────────────────────────────────────────────────┤', Color.CYAN))
    print(color('  │', Color.CYAN) + color('  📋 Coordinador  ', Color.CYAN) + color(': Qwen3 4B   (organiza)       ', Color.BLANCO) + color('  │', Color.CYAN))
    print(color('  │', Color.CYAN) + color('  🔍 Analista     ', Color.MAGENTA) + color(': GPT Oss 20B (razona)        ', Color.BLANCO) + color('  │', Color.CYAN))
    print(color('  │', Color.CYAN) + color('  💻 Desarrollador', Color.AZUL) + color(': Qwen3 30B  (codifica)       ', Color.BLANCO) + color('  │', Color.CYAN))
    print(color('  └─────────────────────────────────────────────────────┘', Color.CYAN))
    print()

    # Capacidades
    print(color('  ┌─────────────────────────────────────────────────────┐', Color.VERDE))
    print(color('  │', Color.VERDE) + color('  CAPACIDADES', Color.NEGRITA) + color(' ' * 34, Color.VERDE) + color('│', Color.VERDE))
    print(color('  ├─────────────────────────────────────────────────────┤', Color.VERDE))
    print(color('  │', Color.VERDE) + color('  📂 Leer y crear archivos (carpeta segura)         ', Color.BLANCO) + color('  │', Color.VERDE))
    print(color('  │', Color.VERDE) + color('  ⚡ Ejecutar comandos (confirmas cada uno)         ', Color.BLANCO) + color('  │', Color.VERDE))
    print(color('  │', Color.VERDE) + color('  💾 Backups automáticos antes de cambios           ', Color.BLANCO) + color('  │', Color.VERDE))
    print(color('  └─────────────────────────────────────────────────────┘', Color.VERDE))
    print()

    # Menú de opciones
    print(color('  ┌─────────────────────────────────────────────────────┐', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  MENÚ PRINCIPAL', Color.NEGRITA) + color(' ' * 32, Color.AMARILLO) + color('│', Color.AMARILLO))
    print(color('  ├─────────────────────────────────────────────────────┤', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  1.', Color.NEGRITA) + color(' Tarea completa   (3 agentes colaboran)          ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  2.', Color.NEGRITA) + color(' Desarrollo código (specs → código → revisión)   ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  3.', Color.NEGRITA) + color(' Debate/evaluación (análisis multi-perspectiva)  ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  4.', Color.NEGRITA) + color(' Chat libre       (habla con un agente)          ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  5.', Color.NEGRITA) + color(' Ver workspace    (explorar archivos)            ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  │', Color.AMARILLO) + color('  6.', Color.NEGRITA) + color(' Salir                                             ', Color.BLANCO) + color('  │', Color.AMARILLO))
    print(color('  └─────────────────────────────────────────────────────┘', Color.AMARILLO))
    print()

    # Info inferior
    print(f"  {color('📂', Color.GRIS)} {color(WORKSPACE, Color.GRIS)}")
    print(f"  {color('💻', Color.GRIS)} {color(so_info, Color.GRIS)}")
    print(f"  {color('📝', Color.GRIS)} {color(str(LOG_FILE), Color.GRIS)}")
    print()

    while True:
        print(f"  {color('─' * 50, Color.GRIS)}")
        opcion = input(f"  {color('Elige una opción', Color.NEGRITA)} {color('[1-6]', Color.AMARILLO)}{color(': ', Color.NEGRITA)}").strip()

        if opcion == "6":
            limpiar_sesion()
            print(f"\n  {color('👋 ¡Hasta luego!', Color.VERDE)}")
            break
        elif opcion == "1":
            tarea = input(f"\n  {color('📋 Describe tu tarea:', Color.CYAN)} ").strip()
            if tarea:
                resultado = flujo_completo(tarea)
                print(f"\n{caja(resultado[:1000], ancho=65, borde_color=Color.VERDE, titulo=' RESULTADO FINAL ')}")
        elif opcion == "2":
            desc = input(f"\n  {color('💻 ¿Qué quieres desarrollar?', Color.MAGENTA)} ").strip()
            if desc:
                flujo_codigo(desc)
        elif opcion == "3":
            tema = input(f"\n  {color('💬 ¿Sobre qué tema quieres debatir?', Color.AMARILLO)} ").strip()
            if tema:
                resultado = flujo_debate(tema)
                print(f"\n{caja(resultado[:1000], ancho=65, borde_color=Color.AMARILLO, titulo=' SÍNTESIS ')}")
        elif opcion == "4":
            flujo_libre()
        elif opcion == "5":
            print(f"\n{caja(ejecutor.listar_workspace(), ancho=65, borde_color=Color.CYAN, titulo=' WORKSPACE ')}")
        else:
            print(f"  {color('⚠️ Opción no válida. Elige 1-6.', Color.ROJO)}")


# ============================================================
# LIMPIEZA DE SESIÓN AL SALIR
# ============================================================

def limpiar_sesion():
    """Elimina logs y backups al cerrar la aplicación para no generar basura."""
    print(f"\n  {color('🧹 Limpiando archivos de sesión...', Color.GRIS)}")
    
    # Limpiar logs
    logs_dir = os.path.join(WORKSPACE, ".logs")
    if os.path.exists(logs_dir):
        try:
            archivos_eliminados = 0
            for archivo in os.listdir(logs_dir):
                ruta_archivo = os.path.join(logs_dir, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    archivos_eliminados += 1
            if archivos_eliminados > 0:
                print(f"  {color(f'✅ {archivos_eliminados} log(s) eliminado(s)', Color.VERDE)}")
            else:
                print(f"  {color('✅ No había logs para eliminar', Color.GRIS)}")
        except Exception as e:
            print(f"  {color(f'⚠️ Error limpiando logs: {e}', Color.AMARILLO)}")
    
    # Limpiar backups
    backups_dir = BACKUPS_DIR
    if os.path.exists(backups_dir):
        try:
            archivos_eliminados = 0
            for archivo in os.listdir(backups_dir):
                ruta_archivo = os.path.join(backups_dir, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    archivos_eliminados += 1
            if archivos_eliminados > 0:
                print(f"  {color(f'✅ {archivos_eliminados} backup(s) eliminado(s)', Color.VERDE)}")
            else:
                print(f"  {color('✅ No había backups para eliminar', Color.GRIS)}")
        except Exception as e:
            print(f"  {color(f'⚠️ Error limpiando backups: {e}', Color.AMARILLO)}")


if __name__ == "__main__":
    print()
    print(color('╔═══════════════════════════════════════════════════════════╗', Color.CYAN))
    print(color('║', Color.CYAN) + color('           🤖 AGENTES COLABORATIVOS v2.1 🤖              ', Color.NEGRITA) + color('║', Color.CYAN))
    print(color('╚═══════════════════════════════════════════════════════════╝', Color.CYAN))
    print()

    spinner(f"Conectando a LM Studio ({LM_STUDIO_URL})")
    try:
        modelos = client.models.list()
        num_modelos = len(modelos.data)
        spinner_ok(f"Conectado a LM Studio")

        if num_modelos == 0:
            print(f"\n  {color('⚠️ Ningún modelo cargado', Color.AMARILLO)}")
            print(f"  {color('Abre LM Studio → Developer → Start Server', Color.GRIS)}")
            print(f"  {color('y carga al menos 1 modelo', Color.GRIS)}")
        else:
            print(f"\n  {color(f'📦 {num_modelos} modelo(s) disponible(s):', Color.VERDE)}")
            for m in modelos.data:
                print(f"    {color('•', Color.CYAN)} {m.id}")

        print()
        menu_principal()
    except Exception as e:
        print(f"\r{color('❌ Error de conexión', Color.ROJO)}{' ' * 30}")
        print(f"\n  {color('No se pudo conectar a LM Studio:', Color.ROJO)}")
        print(f"  {color(str(e), Color.GRIS)}")
        print(f"\n  {color('Verifica:', Color.AMARILLO)}")
        print(f"    {color('1.', Color.CYAN)} LM Studio está abierto")
        print(f"    {color('2.', Color.CYAN)} Developer → Start Server activado")
        print(f"    {color('3.', Color.CYAN)} Al menos 1 modelo cargado (READY)")
        print(f"    {color('4.', Color.CYAN)} URL: {color(LM_STUDIO_URL, Color.AMARILLO)}")
        print()
        exit(1)
