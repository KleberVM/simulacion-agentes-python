import random

class AgenteLimpiadorConMemoria:
    """Agente reactivo que limpia suciedad y recuerda lugares visitados"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suciedad_limpiada = 0
        self.lugares_visitados = set()  # Memoria: conjunto de coordenadas visitadas
        self.lugares_visitados.add((x, y))  # Agregar posición inicial

    def percibir(self, entorno):
        """Percibe si hay suciedad en su posición actual"""
        return entorno.hay_suciedad(self.x, self.y)

    def decidir_y_actuar(self, percepcion, entorno):
        """Lógica mejorada: SI hay suciedad ENTONCES limpiar, 
        SINO moverse hacia lugares no visitados preferentemente"""
        
        if percepcion:
            return "limpiar"
        else:
            # Obtener movimientos posibles hacia lugares no visitados
            movimientos_no_visitados = []
            movimientos_visitados = []
            
            # Revisar cada dirección posible
            direcciones = [
                ("arriba", self.x, self.y - 1),
                ("abajo", self.x, self.y + 1),
                ("izquierda", self.x - 1, self.y),
                ("derecha", self.x + 1, self.y)
            ]
            
            for direccion, nx, ny in direcciones:
                # Verificar si la posición es válida
                if entorno.es_valido(nx, ny):
                    if (nx, ny) not in self.lugares_visitados:
                        movimientos_no_visitados.append(direccion)
                    else:
                        movimientos_visitados.append(direccion)
            
            # Preferir lugares no visitados
            if movimientos_no_visitados:
                return random.choice(movimientos_no_visitados)
            elif movimientos_visitados:
                # Si todos están visitados, elegir al azar entre los válidos
                return random.choice(movimientos_visitados)
            else:
                # No hay movimientos válidos (muy raro)
                return "limpiar"

    def registrar_visita(self):
        """Registra la posición actual como visitada"""
        self.lugares_visitados.add((self.x, self.y))

    def obtener_estadisticas(self):
        """Retorna estadísticas del agente"""
        return {
            'suciedad_limpiada': self.suciedad_limpiada,
            'lugares_visitados': len(self.lugares_visitados),
            'cobertura': self.lugares_visitados
        }


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

    def es_valido(self, x, y):
        """Verifica si la coordenada está dentro de los límites del grid"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

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
        """Visualización simple en consola con indicador de lugares visitados"""
        print("    ", end="")
        for x in range(self.ancho):
            print(f"{x:2}", end=" ")
        print()
        
        for y in range(self.alto):
            print(f"{y:2}  ", end="")
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")  # Agente
                elif (x, y) in self.suciedad:
                    print("💩", end=" ")  # Suciedad
                elif (x, y) in agente.lugares_visitados:
                    print("✓ ", end=" ")  # Visitado (marca de verificación)
                else:
                    print("⬜", end=" ")  # No visitado
            print()
        print()


# --- Simulación ---
def simular_limpieza_con_memoria(pasos=30):
    # (Ancho, Alto, Cantidad de Suciedad)
    entorno = EntornoGrid(6, 6, 10) 
    # Posición inicial del agente (x, y)
    agente = AgenteLimpiadorConMemoria(0, 0)
    
    print("=" * 60)
    print("=== EJERCICIO 1: AGENTE LIMPIADOR CON MEMORIA ===")
    print("=" * 60)
    print("\nLeyenda:")
    print("  🤖 = Agente limpiador")
    print("  💩 = Suciedad")
    print("  ✓  = Lugar visitado")
    print("  ⬜ = Lugar no visitado")
    print()
    print("Estado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        # Ciclo: Percibir -> Decidir -> Actuar
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion, entorno)

        if accion == "limpiar":
            if entorno.limpiar(agente.x, agente.y):
                agente.suciedad_limpiada += 1
                print(f"Paso {paso + 1}: Limpiando en ({agente.x}, {agente.y})")
        else:
            # Si la acción no es limpiar, es moverse
            entorno.mover_agente(agente, accion)
            agente.registrar_visita()  # Registrar nueva posición
            print(f"Paso {paso + 1}: Moviéndose {accion} a ({agente.x}, {agente.y})")

        # Mostrar el grid cada 5 pasos
        if (paso + 1) % 5 == 0:
            print(f"\n--- Estado después del paso {paso + 1} ---")
            entorno.mostrar(agente)

        # Condición de salida: si ya no hay suciedad
        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break
    
    # Reporte final
    stats = agente.obtener_estadisticas()
    print(f"\n{'=' * 60}")
    print(f"--- ESTADO FINAL (después de {paso + 1} pasos) ---")
    print(f"{'=' * 60}")
    entorno.mostrar(agente)
    
    print(f"📊 ESTADÍSTICAS:")
    print(f"  • Suciedad limpiada: {stats['suciedad_limpiada']}")
    print(f"  • Suciedad restante: {len(entorno.suciedad)}")
    print(f"  • Lugares visitados: {stats['lugares_visitados']} de {entorno.ancho * entorno.alto}")
    cobertura_porcentaje = (stats['lugares_visitados'] / (entorno.ancho * entorno.alto)) * 100
    print(f"  • Cobertura del mapa: {cobertura_porcentaje:.1f}%")
    print()

# --- Ejecutar la simulación ---
if __name__ == "__main__":
    simular_limpieza_con_memoria()
