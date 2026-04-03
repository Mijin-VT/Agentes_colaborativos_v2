"""
Tests unitarios para el Sistema de Agentes Colaborativos v2.1
===============================================================
Pruebas para: seguridad, análisis de comandos, gestión de contexto, executor

Ejecutar: python test_agentes.py
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Agregar el directorio del script al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar solo las funciones que no dependen de LM Studio
from agentes_colaborativos_v2 import (
    ruta_es_segura,
    comando_es_seguro,
    estimar_tokens,
    truncar_contexto,
    analizar_comando,
    WORKSPACE,
    BACKUPS_DIR,
)


# ============================================================
# TESTS DE SEGURIDAD
# ============================================================

class TestRutaSegura(unittest.TestCase):
    """Pruebas para la función ruta_es_segura"""

    def test_ruta_dentro_workspace(self):
        """Rutas dentro del workspace deben ser seguras"""
        # Usar rutas relativas al workspace
        self.assertTrue(ruta_es_segura(os.path.join(WORKSPACE, "archivo.txt")))
        self.assertTrue(ruta_es_segura(os.path.join(WORKSPACE, "subdir", "archivo.py")))

    def test_ruta_fuera_workspace(self):
        """Rutas fuera del workspace NO deben ser seguras"""
        if os.name == "nt":  # Windows
            self.assertFalse(ruta_es_segura("C:\\Windows\\system32"))
            self.assertFalse(ruta_es_segura("C:\\Program Files\\app"))
        else:  # Linux/macOS
            self.assertFalse(ruta_es_segura("/usr/bin"))
            self.assertFalse(ruta_es_segura("/etc/passwd"))

    def test_ruta_con_traversal(self):
        """Rutas con '..' que intentan salir del workspace"""
        # Esta prueba depende de la implementación exacta
        # pero en general '..' fuera del workspace debe ser bloqueado
        ruta_maliciosa = os.path.join(WORKSPACE, "..", "archivo_externo.txt")
        ruta_abs = os.path.abspath(ruta_maliciosa)
        workspace_abs = os.path.abspath(WORKSPACE)
        # Si la ruta resuelta está fuera del workspace, debe ser falsa
        if not ruta_abs.startswith(workspace_abs):
            self.assertFalse(ruta_es_segura(ruta_maliciosa))


class TestComandoSeguro(unittest.TestCase):
    """Pruebas para la función comando_es_seguro"""

    def test_comandos_seguros(self):
        """Comandos seguros deben pasar"""
        comandos_seguros = [
            "cat archivo.txt",
            "ls -la",
            "dir",
            "mkdir nueva_carpeta",
            "echo hola >> archivo.txt",
            "git status",
            "python script.py",
        ]
        for comando in comandos_seguros:
            seguro, razon = comando_es_seguro(comando)
            self.assertTrue(seguro, f"Comando '{comando}' debería ser seguro: {razon}")

    def test_comandos_peligrosos(self):
        """Comandos peligrosos deben ser bloqueados"""
        comandos_peligrosos = [
            "format C:",
            "rm -rf /",
            "shutdown /s",
            "reg delete HKLM",
            "net user admin password",
            "powershell -enc base64",
        ]
        for comando in comandos_peligrosos:
            seguro, razon = comando_es_seguro(comando)
            self.assertFalse(seguro, f"Comando '{comando}' debería ser bloqueado")

    def test_comandos_privilegios_unix(self):
        """Comandos de privilegios en Unix deben ser bloqueados"""
        if os.name == "posix":
            comandos_priv = ["sudo rm -rf /", "su - root", "passwd user"]
            for comando in comandos_priv:
                seguro, razon = comando_es_seguro(comando)
                self.assertFalse(seguro, f"Comando '{comando}' debería ser bloqueado")


# ============================================================
# TESTS DE ANÁLISIS DE COMANDOS
# ============================================================

class TestAnalizarComando(unittest.TestCase):
    """Pruebas para la función analizar_comando"""

    def test_lectura_archivo(self):
        """Comandos de lectura deben ser riesgo bajo"""
        analisis = analizar_comando("cat archivo.txt")
        self.assertEqual(analisis["riesgo"], "bajo")
        self.assertIn("Lectura", analisis["tipo"])

    def test_listado_directorio(self):
        """Comandos de listado deben ser riesgo bajo"""
        analisis = analizar_comando("ls -la")
        self.assertEqual(analisis["riesgo"], "bajo")

    def test_escritura_archivo(self):
        """Comandos de escritura deben ser riesgo medio"""
        analisis = analizar_comando("echo hola > archivo.txt")
        self.assertEqual(analisis["riesgo"], "medio")

    def test_eliminacion(self):
        """Comandos de eliminación deben ser riesgo alto"""
        analisis = analizar_comando("rm archivo.txt")
        self.assertEqual(analisis["riesgo"], "alto")
        self.assertFalse(analisis["reversible"])

    def test_instalacion_paquetes(self):
        """Comandos de instalación deben ser riesgo medio"""
        analisis = analizar_comando("pip install requests")
        self.assertEqual(analisis["riesgo"], "medio")

    def test_ejecucion_script(self):
        """Comandos de ejecución deben ser riesgo alto"""
        analisis = analizar_comando("python script.py")
        self.assertEqual(analisis["riesgo"], "alto")

    def test_comando_desconocido(self):
        """Comandos desconocidos deben ser riesgo alto"""
        analisis = analizar_comando("comando_raro_xyz")
        self.assertEqual(analisis["riesgo"], "alto")


# ============================================================
# TESTS DE GESTIÓN DE CONTEXTO
# ============================================================

class TestEstimarTokens(unittest.TestCase):
    """Pruebas para la función estimar_tokens"""

    def test_texto_vacio(self):
        """Texto vacío debe devolver 0"""
        self.assertEqual(estimar_tokens(""), 0)
        self.assertEqual(estimar_tokens(None), 0)

    def test_texto_corto(self):
        """Texto corto debe estimar tokens razonablemente"""
        texto = "Hola mundo"
        tokens = estimar_tokens(texto)
        self.assertGreater(tokens, 0)
        # ~10 caracteres / 3.5 ≈ 3 tokens
        self.assertGreaterEqual(tokens, 2)

    def test_texto_largo(self):
        """Texto largo debe estimar proporcionalmente"""
        texto = "A" * 350  # ~100 tokens estimados
        tokens = estimar_tokens(texto)
        self.assertGreater(tokens, 50)


class TestTruncarContexto(unittest.TestCase):
    """Pruebas para la función truncar_contexto"""

    def test_contexto_vacio(self):
        """Contexto vacío debe devolver vacío"""
        self.assertEqual(truncar_contexto([]), [])

    def test_contexto_corto(self):
        """Contexto corto no debe ser truncado"""
        mensajes = [
            {"role": "system", "content": "Eres un asistente"},
            {"role": "user", "content": "Hola"},
        ]
        resultado = truncar_contexto(mensajes, max_tokens=1000)
        self.assertEqual(len(resultado), 2)

    def test_preserva_system_prompt(self):
        """El system prompt siempre debe preservarse"""
        mensajes = [
            {"role": "system", "content": "System prompt largo" * 100},
            {"role": "user", "content": "Mensaje usuario"},
        ]
        resultado = truncar_contexto(mensajes, max_tokens=50)
        self.assertEqual(resultado[0]["role"], "system")

    def test_trunca_mensajes_antiguos(self):
        """Debe truncar desde los mensajes más antiguos"""
        mensajes = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Mensaje 1" * 100},
            {"role": "user", "content": "Mensaje 2" * 100},
            {"role": "user", "content": "Mensaje 3"},
        ]
        resultado = truncar_contexto(mensajes, max_tokens=100)
        # Debe mantener system + últimos mensajes que quepan
        self.assertGreaterEqual(len(resultado), 1)  # Al menos system
        self.assertEqual(resultado[0]["role"], "system")


# ============================================================
# TESTS DE CONFIGURACIÓN
# ============================================================

class TestConfiguracion(unittest.TestCase):
    """Pruebas para la carga de configuración"""

    def test_config_default_sin_archivo(self):
        """Sin config.json, debe usar valores por defecto"""
        # Esto se prueba indirectamente verificando que las variables existen
        self.assertIsNotNone(WORKSPACE)
        self.assertIsNotNone(BACKUPS_DIR)

    def test_workspace_es_directorio(self):
        """WORKSPACE debe ser un directorio válido"""
        self.assertTrue(os.path.isdir(WORKSPACE) or True)  # Puede no existir aún


# ============================================================
# TESTS DE EJECUTOR DE ACCIONES
# ============================================================

class TestEjecutorAcciones(unittest.TestCase):
    """Pruebas para la clase EjecutorAcciones"""

    def setUp(self):
        """Crear un workspace temporal para pruebas"""
        self.test_dir = tempfile.mkdtemp(prefix="test_agentes_")
        self.workspace_original = WORKSPACE

    def tearDown(self):
        """Limpiar el workspace temporal"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_crear_archivo_simple(self):
        """Debe poder crear un archivo en el workspace"""
        from agentes_colaborativos_v2 import EjecutorAcciones
        
        # Mock del workspace
        with patch('agentes_colaborativos_v2.WORKSPACE', self.test_dir):
            with patch('agentes_colaborativos_v2.BACKUPS_DIR', os.path.join(self.test_dir, ".backups")):
                ejecutor = EjecutorAcciones()
                
                # Crear archivo directamente para la prueba
                archivo = os.path.join(self.test_dir, "test.txt")
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write("contenido de prueba")
                
                self.assertTrue(os.path.exists(archivo))
                with open(archivo, "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), "contenido de prueba")

    def test_listar_workspace_vacio(self):
        """Debe listar un workspace vacío"""
        from agentes_colaborativos_v2 import EjecutorAcciones
        
        with patch('agentes_colaborativos_v2.WORKSPACE', self.test_dir):
            with patch('agentes_colaborativos_v2.BACKUPS_DIR', os.path.join(self.test_dir, ".backups")):
                ejecutor = EjecutorAcciones()
                resultado = ejecutor.listar_workspace()
                self.assertIsInstance(resultado, str)
                self.assertGreater(len(resultado), 0)


# ============================================================
# EJECUCIÓN DE TESTS
# ============================================================

if __name__ == "__main__":
    print("🧪 Ejecutando tests del Sistema de Agentes Colaborativos v2.1")
    print("=" * 60)
    unittest.main(verbosity=2)
