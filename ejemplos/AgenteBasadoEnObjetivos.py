import math
import random
from collections import deque

class AgenteRecolector:
    """Agente que planifica rutas hacia comida usando búsqueda (BFS)"""
    """Escenario:  Un  agente  que  busca  comida  usando  búsqueda  de  caminos. """

    def __init__(self, x, y, entorno):
        self.x = x
        self.y = y
        self.entorno = entorno
        self.energia = 100
        self.comida_recolectada = 0
        self.plan = []  # Secuencia de acciones planificadas (ej: ["abajo", "derecha"])

    def percibir(self):
        """Percibe la comida visible en el entorno dentro de un radio"""
        return self.entorno.obtener_comida_visible(self.x, self.y, radio=5)

    def planificar_ruta(self, objetivo):
        """Búsqueda en Amplitud (BFS) para encontrar el camino más corto al objetivo"""
        if objetivo is None:
            return []

        cola = deque([(self.x, self.y, [])]) # (x, y, camino_hasta_aqui)
        visitados = set([(self.x, self.y)])

        while cola:
            x, y, camino = cola.popleft()

            # ¿Llegó al objetivo?
            if (x, y) == objetivo:
                return camino  # Retorna la lista de acciones (direcciones)

            # Explorar vecinos (arriba, abajo, izquierda, derecha)
            for dx, dy, direccion in [(0, -1, "arriba"), (0, 1, "abajo"), 
                                      (-1, 0, "izquierda"), (1, 0, "derecha")]:
                nx, ny = x + dx, y + dy

                # Verificar si la nueva posición es válida
                if (self.entorno.es_valido(nx, ny) and
                        (nx, ny) not in visitados and
                        not self.entorno.hay_obstaculo(nx, ny)):
                    
                    visitados.add((nx, ny))
                    nuevo_camino = camino + [direccion]
                    cola.append((nx, ny, nuevo_camino))

        return []  # No se encontró camino

    def decidir(self, comida_visible):
        """Decide qué comida perseguir y planifica la ruta"""
        
        # Si no tiene un plan, crea uno nuevo
        if not self.plan:
            if comida_visible:
                # 1. Elegir la comida más cercana (distancia Manhattan)
                objetivo = min(comida_visible, 
                               key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
                
                # 2. Planificar la ruta hacia ese objetivo
                self.plan = self.planificar_ruta(objetivo)

        # Si tiene un plan, ejecuta el siguiente paso
        if self.plan:
            return self.plan.pop(0) # Retorna y elimina la primera acción del plan
        else:
            # Si no hay plan (y no vio comida), se mueve al azar
            return random.choice(["arriba", "abajo", "izquierda", "derecha"])

    def actuar(self, accion):
        """Ejecuta la acción de movimiento y recolecta comida si la encuentra"""
        
        # Moverse
        if accion == "arriba" and self.y > 0:
            self.y -= 1
        elif accion == "abajo" and self.y < self.entorno.alto - 1:
            self.y += 1
        elif accion == "izquierda" and self.x > 0:
            self.x -= 1
        elif accion == "derecha" and self.x < self.entorno.ancho - 1:
            self.x += 1
        
        # Gastar energía por moverse
        self.energia -= 1

        # Recolectar comida si está en esta posición
        if self.entorno.hay_comida(self.x, self.y):
            self.entorno.recolectar_comida(self.x, self.y)
            self.comida_recolectada += 1
            self.energia += 20  # Gana energía
            self.plan = []  # Limpiar plan actual para buscar nuevo objetivo

    def update(self):
        """Ciclo completo: Percibir -> Decidir -> Actuar"""
        if self.energia > 0:
            percepcion = self.percibir()
            decision = self.decidir(percepcion)
            self.actuar(decision)


class EntornoRecoleccion:
    """Entorno con comida y obstáculos"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = {}  # Usamos un dict: {(x, y): valor} (aunque el valor no se usa aquí)
        self.obstaculos = set()

        # Generar comida
        for _ in range(10):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            self.comida[(x, y)] = random.randint(1, 3) # Valor de la comida

        # Generar obstáculos
        for _ in range(8):
            x, y = random.randint(0, ancho-1), random.randint(0, alto-1)
            # Asegurarse de que el obstáculo no esté sobre la comida
            if (x, y) not in self.comida:
                self.obstaculos.add((x, y))

    def es_valido(self, x, y):
        """Verifica si la coordenada está dentro de los límites del grid"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def hay_obstaculo(self, x, y):
        return (x, y) in self.obstaculos

    def hay_comida(self, x, y):
        return (x, y) in self.comida

    def recolectar_comida(self, x, y):
        if (x, y) in self.comida:
            del self.comida[(x, y)]
            return True
        return False

    def obtener_comida_visible(self, x, y, radio):
        """Retorna una lista de coordenadas de comida dentro del radio de visión"""
        visible = []
        for (fx, fy) in self.comida:
            # Distancia Manhattan
            dist = abs(fx - x) + abs(fy - y)
            if dist <= radio:
                visible.append((fx, fy))
        return visible

    def mostrar(self, agente):
        """Visualización del entorno"""
        for y in range(self.alto):
            fila = ""
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    fila += "😀 "  # Agente
                elif (x, y) in self.obstaculos:
                    fila += "⬛️ "  # Obstáculo
                elif (x, y) in self.comida:
                    fila += "🍎 "  # Comida
                else:
                    fila += "⬜️ "  # Vacío
            print(fila)
        print() # Deja un espacio


# --- Simulación ---
def simular_recoleccion(pasos=30):
    entorno = EntornoRecoleccion(8, 8)
    agente = AgenteRecolector(0, 0, entorno) # Agente empieza en (0, 0)

    print("=== SIMULACIÓN: AGENTE BASADO EN OBJETIVOS ===\n")
    print("Estado inicial:")
    entorno.mostrar(agente)
    print(f"Comida: {agente.comida_recolectada} | Energia: {agente.energia}")

    for paso in range(pasos):
        agente.update() # El agente ejecuta su ciclo (percibir, decidir, actuar)

        # Mostrar el estado cada 5 pasos
        if (paso + 1) % 5 == 0:
            print(f"\n--- Paso {paso + 1} ---")
            entorno.mostrar(agente)
            print(f"Comida: {agente.comida_recolectada} | Energia: {agente.energia}")

        # Condiciones de salida
        if agente.energia <= 0:
            print("\n¡El agente se quedó sin energía!")
            break
        if len(entorno.comida) == 0:
            print("\n¡Toda la comida ha sido recolectada!")
            break

    print(f"\n--- Resultado final ---")
    print(f"Comida recolectada: {agente.comida_recolectada}")
    print(f"Energia restante: {agente.energia}")

# --- Ejecutar la simulación ---
simular_recoleccion()