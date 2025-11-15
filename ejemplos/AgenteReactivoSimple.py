import random

class SimpleLimpiezaAgente:
    """Agente reactivo que limpia suciedad cuando la detecta"""
    "Escenario: Un robot limpiador en un grid que detecta y limpia suciedad."
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suciedad_limpiada = 0

    def percibir(self, entorno):
        """Percibe si hay suciedad en su posición actual"""
        return entorno.hay_suciedad(self.x, self.y)

    def decidir_y_actuar(self, percepcion):
        """Lógica simple: SI hay suciedad ENTONCES limpiar"""
        if percepcion:
            return "limpiar"
        else:
            # Si no hay suciedad, se mueve al azar
            return random.choice(["arriba", "abajo", "izquierda", "derecha"])

class EntornoGrid:
    """Entorno: Grid 2D con suciedad"""

    def __init__(self, ancho, alto, num_suciedad):
        self.ancho = ancho
        self.alto = alto
        self.suciedad = set()
        
        # Generar suciedad aleatoria
        for _ in range(num_suciedad):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            self.suciedad.add((x, y))

    def hay_suciedad(self, x, y):
        """Verifica si hay suciedad en una coordenada"""
        return (x, y) in self.suciedad

    def limpiar(self, x, y):
        """Limpia la suciedad de una coordenada si existe"""
        if (x, y) in self.suciedad:
            self.suciedad.remove((x, y))
            return True
        return False

    def mover_agente(self, agente, direccion):
        """Mueve el agente en la dirección especificada, validando límites"""
        if direccion == "arriba" and agente.y > 0:
            agente.y -= 1
        elif direccion == "abajo" and agente.y < self.alto - 1:
            agente.y += 1
        elif direccion == "izquierda" and agente.x > 0:
            agente.x -= 1
        elif direccion == "derecha" and agente.x < self.ancho - 1:
            agente.x += 1

    def mostrar(self, agente):
        """Visualización simple en consola"""
        for y in range(self.alto):
            fila = ""
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    fila += "🤖 "  # Agente
                elif (x, y) in self.suciedad:
                    fila += "💩 "  # Suciedad
                else:
                    fila += "⬜️ "  # Limpio
            print(fila)
        print() # Deja un espacio

# --- Simulación ---
def simular_limpieza(pasos=20):
    # (Ancho, Alto, Cantidad de Suciedad)
    entorno = EntornoGrid(5, 5, 8) 
    # Posición inicial del agente (x, y)
    agente = SimpleLimpiezaAgente(2, 2)
    
    print("=== SIMULACIÓN: AGENTE REACTIVO SIMPLE ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        # Ciclo: Percibir -> Decidir -> Actuar
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion)

        if accion == "limpiar":
            if entorno.limpiar(agente.x, agente.y):
                agente.suciedad_limpiada += 1
                print(f"Paso {paso + 1}: Limpiando en ({agente.x}, {agente.y})")
        else:
            # Si la acción no es limpiar, es moverse
            entorno.mover_agente(agente, accion)
            print(f"Paso {paso + 1}: Moviéndose {accion}")

        # Condición de salida: si ya no hay suciedad
        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break
    
    # Reporte final
    print(f"\n--- Estado final después de {paso + 1} pasos ---")
    entorno.mostrar(agente)
    print(f"Suciedad limpiada: {agente.suciedad_limpiada}")
    print(f"Suciedad restante: {len(entorno.suciedad)}")

# --- Ejecutar la simulación ---
simular_limpieza()