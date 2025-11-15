import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import deque


class AgenteEvitaObstaculos:
    """Agente que planifica rutas evitando obstáculos usando BFS"""
    
    def __init__(self, x, y, entorno):
        self.x = x
        self.y = y
        self.entorno = entorno
        self.comida_recolectada = 0
        self.plan = []  # Lista de movimientos planificados
        self.objetivo_actual = None

    def percibir(self):
        """Percibe comida visible en el entorno"""
        return self.entorno.obtener_comida_visible(self.x, self.y, radio=6)

    def planificar_ruta_bfs(self, objetivo):
        """Búsqueda en Amplitud (BFS) para encontrar camino evitando obstáculos"""
        if objetivo is None:
            return []

        cola = deque([(self.x, self.y, [])])
        visitados = set([(self.x, self.y)])

        while cola:
            x, y, camino = cola.popleft()

            # ¿Llegó al objetivo?
            if (x, y) == objetivo:
                return camino

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

    def decidir(self):
        """Decide la próxima acción"""
        # Si no tiene plan, crear uno nuevo
        if not self.plan:
            comida_visible = self.percibir()
            if comida_visible:
                # Elegir la comida más cercana
                objetivo = min(comida_visible, 
                             key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
                self.objetivo_actual = objetivo
                self.plan = self.planificar_ruta_bfs(objetivo)

        # Ejecutar siguiente paso del plan
        if self.plan:
            return self.plan.pop(0)
        else:
            # Movimiento aleatorio si no hay plan
            self.objetivo_actual = None
            return random.choice(["arriba", "abajo", "izquierda", "derecha"])

    def actuar(self, accion):
        """Ejecuta la acción de movimiento"""
        nueva_x, nueva_y = self.x, self.y
        
        if accion == "arriba":
            nueva_y = self.y - 1
        elif accion == "abajo":
            nueva_y = self.y + 1
        elif accion == "izquierda":
            nueva_x = self.x - 1
        elif accion == "derecha":
            nueva_x = self.x + 1

        # Solo mover si es válido y no hay obstáculo
        if (self.entorno.es_valido(nueva_x, nueva_y) and 
            not self.entorno.hay_obstaculo(nueva_x, nueva_y)):
            self.x = nueva_x
            self.y = nueva_y

        # Recolectar comida si está en esta posición
        if self.entorno.hay_comida(self.x, self.y):
            self.entorno.recolectar_comida(self.x, self.y)
            self.comida_recolectada += 1
            self.plan = []  # Limpiar plan para buscar nuevo objetivo
            self.objetivo_actual = None


class EntornoConObstaculos:
    """Entorno con comida y obstáculos fijos"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        self.obstaculos = set()

        # Generar obstáculos (muro vertical y horizontal)
        # Muro vertical en el centro
        for y in range(2, alto - 2):
            self.obstaculos.add((ancho // 2, y))
        
        # Algunos obstáculos aleatorios
        for _ in range(10):
            x, y = random.randint(0, ancho - 1), random.randint(0, alto - 1)
            if (x, y) not in self.obstaculos:
                self.obstaculos.add((x, y))

        # Generar comida evitando obstáculos
        for _ in range(15):
            intentos = 0
            while intentos < 100:
                x = random.randint(0, ancho - 1)
                y = random.randint(0, alto - 1)
                if (x, y) not in self.obstaculos and (x, y) not in self.comida:
                    self.comida.add((x, y))
                    break
                intentos += 1

    def es_valido(self, x, y):
        """Verifica si la coordenada está dentro de los límites"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def hay_obstaculo(self, x, y):
        """Verifica si hay un obstáculo en la posición"""
        return (x, y) in self.obstaculos

    def hay_comida(self, x, y):
        """Verifica si hay comida en la posición"""
        return (x, y) in self.comida

    def recolectar_comida(self, x, y):
        """Recolecta comida de una posición"""
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False

    def obtener_comida_visible(self, x, y, radio):
        """Retorna comida visible dentro del radio"""
        visible = []
        for (fx, fy) in self.comida:
            dist = abs(fx - x) + abs(fy - y)
            if dist <= radio:
                visible.append((fx, fy))
        return visible


class VisualizadorObstaculos:
    """Visualizador para el ejercicio 3"""
    
    def __init__(self, entorno, agente):
        self.entorno = entorno
        self.agente = agente
        self.fig, self.axes = plt.subplots(1, 2, figsize=(15, 7))
        self.ax_grid = self.axes[0]
        self.ax_stats = self.axes[1]
        self.paso_actual = 0
        
        self.fig.suptitle('Ejercicio 3: Agente que Evita Obstáculos', 
                         fontsize=16, fontweight='bold')

    def actualizar(self):
        """Actualiza la visualización"""
        self.ax_grid.clear()
        self.ax_stats.clear()
        
        # --- Panel izquierdo: Grid ---
        self.ax_grid.set_xlim(-0.5, self.entorno.ancho - 0.5)
        self.ax_grid.set_ylim(-0.5, self.entorno.alto - 0.5)
        self.ax_grid.set_aspect('equal')
        self.ax_grid.set_title(f'Entorno - Paso {self.paso_actual}', fontsize=14, fontweight='bold')
        self.ax_grid.invert_yaxis()
        
        # Dibujar celdas
        for x in range(self.entorno.ancho):
            for y in range(self.entorno.alto):
                rect = Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, 
                               facecolor='white', edgecolor='gray', linewidth=0.5)
                self.ax_grid.add_patch(rect)
        
        # Dibujar obstáculos
        for (x, y) in self.entorno.obstaculos:
            rect = Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, 
                           facecolor='#2F4F4F', edgecolor='black', linewidth=1)
            self.ax_grid.add_patch(rect)
        
        # Dibujar comida
        for (x, y) in self.entorno.comida:
            circulo = plt.Circle((x, y), 0.3, color='#FF6347', alpha=0.8)
            self.ax_grid.add_patch(circulo)
        
        # Dibujar objetivo actual (si existe)
        if self.agente.objetivo_actual:
            ox, oy = self.agente.objetivo_actual
            rect = Rectangle((ox - 0.45, oy - 0.45), 0.9, 0.9, 
                           fill=False, edgecolor='yellow', linewidth=3, linestyle='--')
            self.ax_grid.add_patch(rect)
        
        # Dibujar agente
        agente_circulo = plt.Circle((self.agente.x, self.agente.y), 0.4, 
                                   color='#4169E1', alpha=0.9, zorder=4)
        self.ax_grid.add_patch(agente_circulo)
        
        # Grid
        self.ax_grid.set_xticks(range(self.entorno.ancho))
        self.ax_grid.set_yticks(range(self.entorno.alto))
        self.ax_grid.grid(True, alpha=0.3)
        
        # --- Panel derecho: Estadísticas ---
        self.ax_stats.axis('off')
        
        y_pos = 0.95
        self.ax_stats.text(0.5, y_pos, 'ESTADÍSTICAS', ha='center', fontsize=14, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos = 0.85
        self.ax_stats.text(0.1, y_pos, f'Paso: {self.paso_actual}', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        y_pos -= 0.08
        self.ax_stats.text(0.1, y_pos, f'Posición: ({self.agente.x}, {self.agente.y})', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        y_pos -= 0.08
        self.ax_stats.text(0.1, y_pos, f'Comida recolectada: {self.agente.comida_recolectada}', 
                          fontsize=12, fontweight='bold', color='green', 
                          transform=self.ax_stats.transAxes)
        y_pos -= 0.08
        self.ax_stats.text(0.1, y_pos, f'Comida restante: {len(self.entorno.comida)}', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        y_pos -= 0.08
        self.ax_stats.text(0.1, y_pos, f'Obstáculos: {len(self.entorno.obstaculos)}', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        
        y_pos -= 0.12
        if self.agente.objetivo_actual:
            self.ax_stats.text(0.1, y_pos, f'Objetivo actual: {self.agente.objetivo_actual}', 
                              fontsize=11, color='orange', transform=self.ax_stats.transAxes)
            y_pos -= 0.06
            self.ax_stats.text(0.1, y_pos, f'Pasos del plan: {len(self.agente.plan)}', 
                              fontsize=11, transform=self.ax_stats.transAxes)
        else:
            self.ax_stats.text(0.1, y_pos, 'Explorando...', 
                              fontsize=11, color='gray', transform=self.ax_stats.transAxes)
        
        # Leyenda
        y_pos = 0.3
        self.ax_stats.text(0.5, y_pos, 'LEYENDA', ha='center', fontsize=12, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        y_pos -= 0.08
        
        # Cuadros de colores
        elementos = [
            (0.4, '#4169E1', 'Agente'),
            (0.3, '#FF6347', 'Comida'),
            (0.2, '#2F4F4F', 'Obstáculo'),
        ]
        
        for y_offset, color, texto in elementos:
            rect = Rectangle((0.08, y_offset - 0.015), 0.03, 0.04, 
                           facecolor=color, transform=self.ax_stats.transAxes)
            self.ax_stats.add_patch(rect)
            self.ax_stats.text(0.13, y_offset, f'= {texto}', 
                             fontsize=10, transform=self.ax_stats.transAxes)
        
        y_pos = 0.1
        self.ax_stats.text(0.1, y_pos, 'Borde amarillo = Objetivo actual', 
                          fontsize=9, color='orange', transform=self.ax_stats.transAxes)
        
        plt.tight_layout()


def simular_evitar_obstaculos(pasos=150, velocidad=0.2):
    """Ejecuta la simulación del ejercicio 3"""
    
    entorno = EntornoConObstaculos(12, 12)
    
    # Asegurar que el agente no empiece en un obstáculo
    pos_inicial = (0, 0)
    while pos_inicial in entorno.obstaculos:
        pos_inicial = (random.randint(0, 11), random.randint(0, 11))
    
    agente = AgenteEvitaObstaculos(pos_inicial[0], pos_inicial[1], entorno)
    visualizador = VisualizadorObstaculos(entorno, agente)
    
    print("=" * 70)
    print("EJERCICIO 3: AGENTE QUE EVITA OBSTÁCULOS")
    print("=" * 70)
    print("\nEl agente usa BFS (Búsqueda en Amplitud) para planificar rutas")
    print("que evitan obstáculos fijos en el entorno.\n")
    print("Iniciando simulación...")
    print("Cierra la ventana de matplotlib para terminar.\n")
    
    plt.ion()
    visualizador.actualizar()
    plt.pause(1)
    
    for paso in range(pasos):
        visualizador.paso_actual = paso + 1
        
        # Ciclo del agente
        accion = agente.decidir()
        agente.actuar(accion)
        
        # Actualizar visualización
        visualizador.actualizar()
        plt.pause(velocidad)
        
        # Verificar si la ventana fue cerrada
        if not plt.fignum_exists(visualizador.fig.number):
            print("\nSimulación detenida por el usuario.")
            break
        
        # Condición de salida
        if len(entorno.comida) == 0:
            print("\n¡Toda la comida ha sido recolectada!")
            break
    
    # Reporte final
    print("\n" + "=" * 70)
    print("REPORTE FINAL")
    print("=" * 70)
    print(f"Pasos totales: {visualizador.paso_actual}")
    print(f"Comida recolectada: {agente.comida_recolectada}")
    print(f"Comida restante: {len(entorno.comida)}")
    print(f"Obstáculos evitados: {len(entorno.obstaculos)}")
    print("=" * 70)
    
    print("\nCierra la ventana de matplotlib para finalizar.")
    plt.show()


if __name__ == "__main__":
    simular_evitar_obstaculos(pasos=200, velocidad=0.15)
