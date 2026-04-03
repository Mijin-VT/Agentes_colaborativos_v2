"""
Prueba de que el código se extrae correctamente de los bloques markdown
"""
from agentes_colaborativos_v2 import limpiar_respuesta

# Caso 1: Agente genera código dentro de bloque markdown
contenido_sucio_1 = """[CONTENIDO DEL ARCHIVO]:
```cpp
#include <iostream>
#include <string>

class MiClase {
public:
    void saludar() {
        std::cout << "Hola Mundo" << std::endl;
    }
};
```
"""

print("CASO 1: Código dentro de bloque markdown")
print("=" * 60)
print("ENTRADA:")
print(contenido_sucio_1)
print("=" * 60)

resultado_1 = limpiar_respuesta(contenido_sucio_1)
print("\nSALIDA (código extraído, sin markdown):")
print(resultado_1)
print("=" * 60)

# Verificar que el código está limpio
assert "[CONTENIDO DEL ARCHIVO]" not in resultado_1, "❌ Aún contiene [CONTENIDO DEL ARCHIVO]"
assert "```" not in resultado_1, "❌ Aún contiene bloques markdown"
assert "#include <iostream>" in resultado_1, "❌ Falta el código C++"
assert "class MiClase" in resultado_1, "❌ Falta la clase"
print("✅ CASO 1 EXITOSO: Código extraído correctamente\n")

# Caso 2: Agente genera solo texto sin bloques
contenido_sucio_2 = """[CONTENIDO DEL ARCHIVO]:
Este es un archivo de configuración en formato JSON."""

print("CASO 2: Solo texto sin bloques markdown")
print("=" * 60)
print("ENTRADA:")
print(contenido_sucio_2)
print("=" * 60)

resultado_2 = limpiar_respuesta(contenido_sucio_2)
print("\nSALIDA:")
print(resultado_2)
print("=" * 60)

assert "[CONTENIDO DEL ARCHIVO]" not in resultado_2, "❌ Aún contiene [CONTENIDO DEL ARCHIVO]"
print("✅ CASO 2 EXITOSO: Texto limpio sin artefactos\n")

print("\n🎉 TODAS LAS PRUEBAS PASARON!")
