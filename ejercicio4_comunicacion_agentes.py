import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


class AgenteCooperativo:
    """Agente que se comunica con otros para evitar ir al mismo objetivo"""
    
    def __init__(self, id, x, y, entorno, color):
        self.id = id
        self.x = x
        self.y = y
        self.entorno = entorno
        self.color = color
        self.comida_recolectada = 0
        self.objetivo = None  # Coordenada de comida objetivo
        self.objetivos_reservados = set()  # Objetivos de otros agentes
        self.mensajes = []

    def enviar_mensaje(self, destinatarios, tipo, contenido):
        """Envía un mensaje a otros agentes"""
        for agente in destinatarios:
            if agente.id != self.id:
                agente.recibir_mensaje(self.id, tipo, contenido)

    def recibir_mensaje(self, remitente, tipo, contenido):
        """Recibe un mensaje de otro agente"""
        self.mensajes.append({
            'de': remitente,
            'tipo': tipo,
            'contenido': contenido
        })

    def procesar_mensajes(self):
        """Procesa mensajes recibidos"""
        self.objetivos_reservados.clear()
        
        for msg in self.mensajes:
            if msg['tipo'] == 'objetivo_reservado':
                # Otro agente ya va hacia esta comida
                self.objetivos_reservados.add(msg['contenido'])
        
        self.mensajes.clear()

    def percibir(self):
        """Percibe comida cercana"""
        return self.entorno.obtener_comida_cercana(self.x, self.y, radio=8)

    def decidir_objetivo(self, otros_agentes):
        """Decide hacia qué comida ir, evitando objetivos de otros"""
        # Procesar comunicaciones
        self.procesar_mensajes()
        
        # Percibir comida
        comida_visible = self.percibir()
        
        # Filtrar comida que ya tiene otro agente como objetivo
        comida_disponible = [c for c in comida_visible 
                            if c not in self.objetivos_reservados]
        
        if comida_disponible:
            # Elegir la más cercana
            self.objetivo = min(comida_disponible,
                              key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
            
            # Informar a otros agentes sobre nuestro objetivo
            self.enviar_mensaje(otros_agentes, 'objetivo_reservado', self.objetivo)
        else:
            self.objetivo = None

    def actuar(self):
        """Ejecuta movimiento hacia el objetivo"""
        if self.objetivo:
            # ¿Ya llegó?
            if (self.x, self.y) == self.objetivo:
                if self.entorno.recolectar_comida(self.x, self.y):
                    self.comida_recolectada += 1
                self.objetivo = None
            else:
                # Moverse hacia el objetivo
                dx = 1 if self.objetivo[0] > self.x else -1 if self.objetivo[0] < self.x else 0
                dy = 1 if self.objetivo[1] > self.y else -1 if self.objetivo[1] < self.y else 0

                # Mover en X o Y (no diagonal)
                if dx != 0:
                    nueva_x = self.x + dx
                    if self.entorno.es_valido(nueva_x, self.y):
                        self.x = nueva_x
                elif dy != 0:
                    nueva_y = self.y + dy
                    if self.entorno.es_valido(self.x, nueva_y):
                        self.y = nueva_y
        else:
            # Movimiento aleatorio
            direccion = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = self.x + direccion[0], self.y + direccion[1]
            if self.entorno.es_valido(nx, ny):
                self.x, self.y = nx, ny


class EntornoMultiAgente:
    """Entorno para múltiples agentes"""

    def __init__(self, ancho, alto, num_comida):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        
        # Generar comida
        for _ in range(num_comida):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            self.comida.add((x, y))

    def es_valido(self, x, y):
        """Verifica si la coordenada es válida"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_comida_cercana(self, x, y, radio):
        """Retorna comida dentro del radio"""
        return [pos for pos in self.comida 
                if abs(pos[0] - x) + abs(pos[1] - y) <= radio]

    def recolectar_comida(self, x, y):
        """Recolecta comida de una posición"""
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False


class VisualizadorMultiAgente:
    """Visualizador para múltiples agentes cooperativos"""
    
    def __init__(self, entorno, agentes):
        self.entorno = entorno
        self.agentes = agentes
        self.fig, self.axes = plt.subplots(1, 2, figsize=(15, 7))
        self.ax_grid = self.axes[0]
        self.ax_stats = self.axes[1]
        self.paso_actual = 0
        
        self.fig.suptitle('Ejercicio 4: Comunicación entre Agentes Recolectores', 
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
                               facecolor='#F5F5F5', edgecolor='gray', linewidth=0.5)
                self.ax_grid.add_patch(rect)
        
        # Dibujar comida
        for (x, y) in self.entorno.comida:
            circulo = plt.Circle((x, y), 0.3, color='#FF6347', alpha=0.8)
            self.ax_grid.add_patch(circulo)
        
        # Dibujar líneas de objetivo (agente -> objetivo)
        for agente in self.agentes:
            if agente.objetivo and agente.objetivo in self.entorno.comida:
                ox, oy = agente.objetivo
                self.ax_grid.plot([agente.x, ox], [agente.y, oy], 
                                color=agente.color, linestyle='--', 
                                linewidth=2, alpha=0.5)
                # Marcar objetivo
                rect = Rectangle((ox - 0.45, oy - 0.45), 0.9, 0.9, 
                               fill=False, edgecolor=agente.color, 
                               linewidth=2, linestyle='--')
                self.ax_grid.add_patch(rect)
        
        # Dibujar agentes
        for agente in self.agentes:
            circulo = plt.Circle((agente.x, agente.y), 0.4, 
                               color=agente.color, alpha=0.9, zorder=4)
            self.ax_grid.add_patch(circulo)
            # Número del agente
            self.ax_grid.text(agente.x, agente.y, str(agente.id), 
                            ha='center', va='center', 
                            fontsize=12, fontweight='bold', color='white', zorder=5)
        
        # Grid
        self.ax_grid.set_xticks(range(self.entorno.ancho))
        self.ax_grid.set_yticks(range(self.entorno.alto))
        self.ax_grid.grid(True, alpha=0.3)
        
        # --- Panel derecho: Estadísticas ---
        self.ax_stats.axis('off')
        
        y_pos = 0.95
        self.ax_stats.text(0.5, y_pos, 'ESTADÍSTICAS', ha='center', fontsize=14, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos = 0.88
        self.ax_stats.text(0.1, y_pos, f'Paso: {self.paso_actual}', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        
        y_pos -= 0.08
        total = sum(a.comida_recolectada for a in self.agentes)
        self.ax_stats.text(0.1, y_pos, f'Total recolectado: {total}', 
                          fontsize=12, fontweight='bold', color='green',
                          transform=self.ax_stats.transAxes)
        
        y_pos -= 0.08
        self.ax_stats.text(0.1, y_pos, f'Comida restante: {len(self.entorno.comida)}', 
                          fontsize=12, transform=self.ax_stats.transAxes)
        
        # Información por agente
        y_pos -= 0.12
        self.ax_stats.text(0.5, y_pos, 'AGENTES', ha='center', fontsize=13, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos -= 0.08
        for agente in self.agentes:
            # Círculo de color
            circulo = Circle((0.1, y_pos), 0.02, color=agente.color, 
                           transform=self.ax_stats.transAxes)
            self.ax_stats.add_patch(circulo)
            
            # Info del agente
            objetivo_str = f"→ {agente.objetivo}" if agente.objetivo else "Explorando"
            self.ax_stats.text(0.15, y_pos, 
                             f"Agente {agente.id}: {agente.comida_recolectada} comida  {objetivo_str}", 
                             fontsize=10, transform=self.ax_stats.transAxes,
                             verticalalignment='center')
            y_pos -= 0.06
        
        # Comunicación
        y_pos -= 0.08
        self.ax_stats.text(0.5, y_pos, 'COMUNICACIÓN', ha='center', fontsize=13, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos -= 0.06
        self.ax_stats.text(0.1, y_pos, 
                          'Los agentes se comunican sus objetivos', 
                          fontsize=9, style='italic', transform=self.ax_stats.transAxes)
        y_pos -= 0.05
        self.ax_stats.text(0.1, y_pos, 
                          'para evitar ir a la misma comida.', 
                          fontsize=9, style='italic', transform=self.ax_stats.transAxes)
        
        # Conflictos evitados
        y_pos -= 0.08
        objetivos_actuales = [a.objetivo for a in self.agentes if a.objetivo]
        conflictos_evitados = len(objetivos_actuales) == len(set(objetivos_actuales))
        
        if objetivos_actuales:
            if conflictos_evitados:
                self.ax_stats.text(0.1, y_pos, 
                                  '✓ Sin conflictos: Cada agente va a diferente objetivo', 
                                  fontsize=9, color='green', fontweight='bold',
                                  transform=self.ax_stats.transAxes)
            else:
                self.ax_stats.text(0.1, y_pos, 
                                  '⚠ Conflicto detectado', 
                                  fontsize=9, color='orange', fontweight='bold',
                                  transform=self.ax_stats.transAxes)
        
        # Leyenda
        y_pos = 0.15
        self.ax_stats.text(0.5, y_pos, 'LEYENDA', ha='center', fontsize=12, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        y_pos -= 0.06
        
        rect = Rectangle((0.08, y_pos - 0.015), 0.03, 0.04, 
                       facecolor='#FF6347', transform=self.ax_stats.transAxes)
        self.ax_stats.add_patch(rect)
        self.ax_stats.text(0.13, y_pos, '= Comida', 
                         fontsize=10, transform=self.ax_stats.transAxes)
        
        y_pos -= 0.05
        self.ax_stats.text(0.1, y_pos, 'Línea punteada = Objetivo del agente', 
                          fontsize=9, transform=self.ax_stats.transAxes)
        
        plt.tight_layout()


def simular_comunicacion_agentes(num_agentes=4, pasos=150, velocidad=0.2):
    """Ejecuta la simulación del ejercicio 4"""
    
    entorno = EntornoMultiAgente(12, 12, num_comida=20)
    agentes = []
    
    # Colores para los agentes
    colores = ['#4169E1', '#32CD32', '#FF1493', '#FF8C00', '#9370DB']
    
    # Crear agentes en posiciones aleatorias
    for i in range(num_agentes):
        x = random.randint(0, entorno.ancho - 1)
        y = random.randint(0, entorno.alto - 1)
        color = colores[i % len(colores)]
        agentes.append(AgenteCooperativo(i + 1, x, y, entorno, color))
    
    visualizador = VisualizadorMultiAgente(entorno, agentes)
    
    print("=" * 70)
    print("EJERCICIO 4: COMUNICACIÓN ENTRE AGENTES RECOLECTORES")
    print("=" * 70)
    print(f"\n{num_agentes} agentes cooperan para recolectar comida.")
    print("Se comunican entre sí para evitar ir al mismo objetivo.\n")
    print("Iniciando simulación...")
    print("Cierra la ventana de matplotlib para terminar.\n")
    
    plt.ion()
    visualizador.actualizar()
    plt.pause(1)
    
    for paso in range(pasos):
        visualizador.paso_actual = paso + 1
        
        # Cada agente decide su objetivo comunicándose con los demás
        for agente in agentes:
            otros = [a for a in agentes if a.id != agente.id]
            agente.decidir_objetivo(otros)
        
        # Cada agente actúa
        for agente in agentes:
            agente.actuar()
        
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
    print(f"\nComida recolectada por agente:")
    total = 0
    for agente in agentes:
        print(f"  Agente {agente.id}: {agente.comida_recolectada} unidades")
        total += agente.comida_recolectada
    print(f"\nTotal recolectado: {total}")
    print(f"Comida restante: {len(entorno.comida)}")
    print("=" * 70)
    
    print("\nCierra la ventana de matplotlib para finalizar.")
    plt.show()


if __name__ == "__main__":
    simular_comunicacion_agentes(num_agentes=4, pasos=200, velocidad=0.15)
