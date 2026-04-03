"""
Prueba de la barra de progreso animada
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentes_colaborativos_v2 import barra_progreso_animada, color, Color
import threading
import time

print("\n" + "="*60)
print("PRUEBA DE BARRA DE PROGRESO ANIMADA")
print("="*60)

# Simular un agente pensando
evento = threading.Event()
hilo = threading.Thread(
    target=barra_progreso_animada,
    args=("🧠 COORDINADOR pensando...", evento),
    daemon=True
)
hilo.start()

# Simular trabajo de 5 segundos
time.sleep(5)

# Detener la animación
evento.set()
hilo.join(timeout=1)

print(f"\r{' ' * 120}\r", end="", flush=True)
print(f"\n{color('✅ Prueba completada!', Color.VERDE)}\n")
