import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

class TipoSuciedad:
    """Clase para definir tipos de suciedad con diferentes propiedades"""
    
    TIPOS = {
        'leve': {'valor': 1, 'color': '#FFE4B5', 'tiempo_limpieza': 1, 'nombre': 'Leve'},
        'moderada': {'valor': 2, 'color': '#FFA500', 'tiempo_limpieza': 2, 'nombre': 'Moderada'},
        'severa': {'valor': 3, 'color': '#8B4513', 'tiempo_limpieza': 3, 'nombre': 'Severa'},
        'toxica': {'valor': 5, 'color': '#228B22', 'tiempo_limpieza': 4, 'nombre': 'Tóxica'}
    }


class AgenteLimpiadorAvanzado:
    """Agente que limpia diferentes tipos de suciedad"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suciedad_limpiada = {}  # Contador por tipo
        self.puntos_totales = 0
        self.lugares_visitados = set()
        self.lugares_visitados.add((x, y))
        self.limpiando = None  # Tipo de suciedad que está limpiando
        self.tiempo_limpieza_restante = 0  # Pasos restantes para limpiar
        
        # Inicializar contadores
        for tipo in TipoSuciedad.TIPOS:
            self.suciedad_limpiada[tipo] = 0

    def percibir(self, entorno):
        """Percibe el tipo de suciedad en su posición actual"""
        return entorno.obtener_suciedad(self.x, self.y)

    def decidir_y_actuar(self, percepcion, entorno):
        """Lógica de decisión considerando tipos de suciedad"""
        
        # Si está en proceso de limpieza, continuar limpiando
        if self.tiempo_limpieza_restante > 0:
            return "limpiando"
        
        # Si hay suciedad nueva, empezar a limpiarla
        if percepcion:
            tipo_suciedad = percepcion
            self.limpiando = tipo_suciedad
            self.tiempo_limpieza_restante = TipoSuciedad.TIPOS[tipo_suciedad]['tiempo_limpieza']
            return "empezar_limpiar"
        else:
            # Buscar la suciedad más valiosa cercana
            suciedad_cercana = entorno.obtener_suciedad_cercana(self.x, self.y, radio=3)
            
            if suciedad_cercana:
                # Ordenar por valor (priorizar suciedad más valiosa)
                suciedad_cercana.sort(key=lambda s: TipoSuciedad.TIPOS[s[2]]['valor'], reverse=True)
                objetivo = suciedad_cercana[0]
                
                # Moverse hacia el objetivo
                return self._mover_hacia(objetivo[0], objetivo[1])
            else:
                # Explorar lugares no visitados
                return self._explorar_no_visitado(entorno)

    def _mover_hacia(self, target_x, target_y):
        """Calcula dirección de movimiento hacia un objetivo"""
        if target_x > self.x:
            return "derecha"
        elif target_x < self.x:
            return "izquierda"
        elif target_y > self.y:
            return "abajo"
        elif target_y < self.y:
            return "arriba"
        return None

    def _explorar_no_visitado(self, entorno):
        """Intenta moverse a lugares no visitados"""
        movimientos_no_visitados = []
        movimientos_visitados = []
        
        direcciones = [
            ("arriba", self.x, self.y - 1),
            ("abajo", self.x, self.y + 1),
            ("izquierda", self.x - 1, self.y),
            ("derecha", self.x + 1, self.y)
        ]
        
        for direccion, nx, ny in direcciones:
            if entorno.es_valido(nx, ny):
                if (nx, ny) not in self.lugares_visitados:
                    movimientos_no_visitados.append(direccion)
                else:
                    movimientos_visitados.append(direccion)
        
        if movimientos_no_visitados:
            return random.choice(movimientos_no_visitados)
        elif movimientos_visitados:
            return random.choice(movimientos_visitados)
        return None

    def registrar_visita(self):
        """Registra la posición actual como visitada"""
        self.lugares_visitados.add((self.x, self.y))


class EntornoMultiSuciedad:
    """Entorno con diferentes tipos de suciedad"""

    def __init__(self, ancho, alto, cantidad_por_tipo):
        self.ancho = ancho
        self.alto = alto
        self.suciedad = {}  # {(x, y): tipo}
        
        # Generar diferentes tipos de suciedad
        for tipo in TipoSuciedad.TIPOS:
            for _ in range(cantidad_por_tipo.get(tipo, 0)):
                intentos = 0
                while intentos < 100:  # Evitar bucle infinito
                    x = random.randint(0, ancho - 1)
                    y = random.randint(0, alto - 1)
                    if (x, y) not in self.suciedad:
                        self.suciedad[(x, y)] = tipo
                        break
                    intentos += 1

    def es_valido(self, x, y):
        """Verifica si la coordenada está dentro de los límites"""
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_suciedad(self, x, y):
        """Retorna el tipo de suciedad en una posición, o None"""
        return self.suciedad.get((x, y))

    def limpiar(self, x, y):
        """Limpia la suciedad de una coordenada si existe"""
        if (x, y) in self.suciedad:
            tipo = self.suciedad[(x, y)]
            del self.suciedad[(x, y)]
            return tipo
        return None

    def obtener_suciedad_cercana(self, x, y, radio):
        """Retorna lista de suciedad cercana como (x, y, tipo)"""
        cercana = []
        for (sx, sy), tipo in self.suciedad.items():
            dist = abs(sx - x) + abs(sy - y)
            if dist <= radio:
                cercana.append((sx, sy, tipo))
        return cercana

    def mover_agente(self, agente, direccion):
        """Mueve el agente en la dirección especificada"""
        if direccion == "arriba" and agente.y > 0:
            agente.y -= 1
        elif direccion == "abajo" and agente.y < self.alto - 1:
            agente.y += 1
        elif direccion == "izquierda" and agente.x > 0:
            agente.x -= 1
        elif direccion == "derecha" and agente.x < self.ancho - 1:
            agente.x += 1


class VisualizadorMatplotlib:
    """Clase para visualizar la simulación con matplotlib"""
    
    def __init__(self, entorno, agente):
        self.entorno = entorno
        self.agente = agente
        self.fig, self.axes = plt.subplots(1, 2, figsize=(16, 7))
        self.ax_grid = self.axes[0]
        self.ax_stats = self.axes[1]
        self.paso_actual = 0
        self.historial_puntos = []
        
        # Configurar la figura
        self.fig.suptitle('Ejercicio 2: Agente Limpiador con Múltiples Tipos de Suciedad', 
                         fontsize=16, fontweight='bold')

    def actualizar(self):
        """Actualiza la visualización"""
        self.ax_grid.clear()
        self.ax_stats.clear()
        
        # --- Panel izquierdo: Grid del entorno ---
        self.ax_grid.set_xlim(-0.5, self.entorno.ancho - 0.5)
        self.ax_grid.set_ylim(-0.5, self.entorno.alto - 0.5)
        self.ax_grid.set_aspect('equal')
        self.ax_grid.set_title(f'Entorno - Paso {self.paso_actual}', fontsize=14, fontweight='bold')
        self.ax_grid.set_xlabel('X')
        self.ax_grid.set_ylabel('Y')
        
        # Invertir eje Y para que (0,0) esté arriba-izquierda
        self.ax_grid.invert_yaxis()
        
        # Dibujar grid
        for x in range(self.entorno.ancho):
            for y in range(self.entorno.alto):
                # Color de fondo según visitado o no
                if (x, y) in self.agente.lugares_visitados:
                    color_fondo = '#E8F4F8'  # Celeste claro para visitados
                else:
                    color_fondo = 'white'
                
                rect = Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, 
                               facecolor=color_fondo, edgecolor='gray', linewidth=0.5)
                self.ax_grid.add_patch(rect)
        
        # Dibujar suciedad
        for (x, y), tipo in self.entorno.suciedad.items():
            color = TipoSuciedad.TIPOS[tipo]['color']
            circulo = plt.Circle((x, y), 0.35, color=color, alpha=0.8, zorder=2)
            self.ax_grid.add_patch(circulo)
            # Añadir valor
            valor = TipoSuciedad.TIPOS[tipo]['valor']
            self.ax_grid.text(x, y, str(valor), ha='center', va='center', 
                            fontsize=10, fontweight='bold', color='white', zorder=3)
        
        # Dibujar agente
        agente_circulo = plt.Circle((self.agente.x, self.agente.y), 0.4, 
                                   color='#4169E1', alpha=0.9, zorder=4)
        self.ax_grid.add_patch(agente_circulo)
        self.ax_grid.text(self.agente.x, self.agente.y, '🤖', ha='center', va='center', 
                        fontsize=20, zorder=5)
        
        # Si está limpiando, mostrar indicador
        if self.agente.tiempo_limpieza_restante > 0:
            progress_circle = plt.Circle((self.agente.x, self.agente.y), 0.48, 
                                       fill=False, edgecolor='red', linewidth=3, zorder=6)
            self.ax_grid.add_patch(progress_circle)
        
        # Grid lines
        self.ax_grid.set_xticks(range(self.entorno.ancho))
        self.ax_grid.set_yticks(range(self.entorno.alto))
        self.ax_grid.grid(True, alpha=0.3)
        
        # --- Panel derecho: Estadísticas ---
        self.ax_stats.axis('off')
        
        # Título de estadísticas
        self.ax_stats.text(0.5, 0.95, 'ESTADÍSTICAS', ha='center', fontsize=14, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        
        # Información del agente
        y_pos = 0.88
        self.ax_stats.text(0.1, y_pos, f'Paso actual: {self.paso_actual}', 
                          fontsize=11, transform=self.ax_stats.transAxes)
        y_pos -= 0.06
        self.ax_stats.text(0.1, y_pos, f'Posición: ({self.agente.x}, {self.agente.y})', 
                          fontsize=11, transform=self.ax_stats.transAxes)
        y_pos -= 0.06
        self.ax_stats.text(0.1, y_pos, f'Puntos totales: {self.agente.puntos_totales}', 
                          fontsize=11, fontweight='bold', transform=self.ax_stats.transAxes)
        
        # Suciedad limpiada por tipo
        y_pos -= 0.1
        self.ax_stats.text(0.1, y_pos, 'Suciedad Limpiada:', 
                          fontsize=12, fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos -= 0.06
        for tipo, info in TipoSuciedad.TIPOS.items():
            cantidad = self.agente.suciedad_limpiada[tipo]
            # Cuadrado de color
            rect = Rectangle((0.08, y_pos - 0.015), 0.03, 0.04, 
                           facecolor=info['color'], transform=self.ax_stats.transAxes)
            self.ax_stats.add_patch(rect)
            # Texto
            self.ax_stats.text(0.13, y_pos, f"{info['nombre']}: {cantidad} (Valor: {info['valor']})", 
                             fontsize=10, transform=self.ax_stats.transAxes)
            y_pos -= 0.05
        
        # Suciedad restante
        y_pos -= 0.06
        total_restante = len(self.entorno.suciedad)
        self.ax_stats.text(0.1, y_pos, f'Suciedad restante: {total_restante}', 
                          fontsize=11, fontweight='bold', transform=self.ax_stats.transAxes)
        
        # Cobertura
        y_pos -= 0.06
        cobertura = len(self.agente.lugares_visitados)
        total_celdas = self.entorno.ancho * self.entorno.alto
        porcentaje = (cobertura / total_celdas) * 100
        self.ax_stats.text(0.1, y_pos, f'Cobertura: {cobertura}/{total_celdas} ({porcentaje:.1f}%)', 
                          fontsize=11, transform=self.ax_stats.transAxes)
        
        # Leyenda
        y_pos = 0.05
        self.ax_stats.text(0.5, y_pos, 'LEYENDA', ha='center', fontsize=11, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        y_pos -= 0.05
        self.ax_stats.text(0.1, y_pos, '🤖 = Agente | Fondo celeste = Visitado', 
                          fontsize=9, transform=self.ax_stats.transAxes)
        
        plt.tight_layout()

    def mostrar(self):
        """Muestra la ventana"""
        self.actualizar()
        plt.show(block=False)
        plt.pause(0.5)


def simular_con_visualizacion(pasos=100, velocidad=0.3):
    """Ejecuta la simulación con visualización en tiempo real"""
    
    # Configuración del entorno
    entorno = EntornoMultiSuciedad(10, 10, {
        'leve': 8,
        'moderada': 6,
        'severa': 4,
        'toxica': 3
    })
    
    agente = AgenteLimpiadorAvanzado(0, 0)
    visualizador = VisualizadorMatplotlib(entorno, agente)
    
    print("=" * 70)
    print("EJERCICIO 2: AGENTE CON DIFERENTES TIPOS DE SUCIEDAD")
    print("=" * 70)
    print("\nTipos de suciedad:")
    for tipo, info in TipoSuciedad.TIPOS.items():
        print(f"  • {info['nombre']}: Valor={info['valor']}, Tiempo de limpieza={info['tiempo_limpieza']} pasos")
    print("\nIniciando simulación...")
    print("Cierra la ventana de matplotlib para terminar.\n")
    
    # Mostrar estado inicial
    visualizador.actualizar()
    plt.pause(1)
    
    for paso in range(pasos):
        visualizador.paso_actual = paso + 1
        
        # Ciclo del agente
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion, entorno)
        
        if accion == "empezar_limpiar":
            print(f"Paso {paso + 1}: Empezando a limpiar suciedad '{agente.limpiando}' en ({agente.x}, {agente.y})")
        elif accion == "limpiando":
            agente.tiempo_limpieza_restante -= 1
            if agente.tiempo_limpieza_restante == 0:
                # Terminar limpieza
                tipo = entorno.limpiar(agente.x, agente.y)
                if tipo:
                    valor = TipoSuciedad.TIPOS[tipo]['valor']
                    agente.suciedad_limpiada[tipo] += 1
                    agente.puntos_totales += valor
                    print(f"Paso {paso + 1}: ¡Limpieza completada! Tipo: {tipo}, Puntos ganados: +{valor}")
                agente.limpiando = None
        elif accion in ["arriba", "abajo", "izquierda", "derecha"]:
            entorno.mover_agente(agente, accion)
            agente.registrar_visita()
        
        # Actualizar historial de puntos
        visualizador.historial_puntos.append(agente.puntos_totales)
        
        # Actualizar visualización
        visualizador.actualizar()
        plt.pause(velocidad)
        
        # Verificar si la ventana fue cerrada
        if not plt.fignum_exists(visualizador.fig.number):
            print("\nSimulación detenida por el usuario.")
            break
        
        # Condición de salida
        if len(entorno.suciedad) == 0:
            print("\n¡Toda la suciedad ha sido limpiada!")
            break
    
    # Reporte final
    print("\n" + "=" * 70)
    print("REPORTE FINAL")
    print("=" * 70)
    print(f"Pasos totales: {visualizador.paso_actual}")
    print(f"Puntos totales: {agente.puntos_totales}")
    print(f"\nSuciedad limpiada por tipo:")
    for tipo, info in TipoSuciedad.TIPOS.items():
        cantidad = agente.suciedad_limpiada[tipo]
        puntos = cantidad * info['valor']
        print(f"  • {info['nombre']:10} : {cantidad:2} unidades (= {puntos:2} puntos)")
    print(f"\nSuciedad restante: {len(entorno.suciedad)}")
    print(f"Cobertura del mapa: {len(agente.lugares_visitados)}/{entorno.ancho * entorno.alto} celdas")
    print("=" * 70)
    
    # Mantener la ventana abierta
    print("\nCierra la ventana de matplotlib para finalizar.")
    plt.show()


if __name__ == "__main__":
    # Configurar el backend de matplotlib
    plt.ion()  # Modo interactivo
    simular_con_visualizacion(pasos=150, velocidad=0.2)
