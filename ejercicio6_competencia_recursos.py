import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge


class AgenteCompetitivo:
    """Agente que compite por recursos limitados"""
    
    def __init__(self, id, x, y, entorno, color, estrategia='equilibrada'):
        self.id = id
        self.x = x
        self.y = y
        self.entorno = entorno
        self.color = color
        self.estrategia = estrategia  # 'agresiva', 'conservadora', 'equilibrada'
        
        # Recursos
        self.energia = 100
        self.comida_recolectada = 0
        self.pasos_dados = 0
        self.vivo = True
        
        # Estrategia
        if estrategia == 'agresiva':
            self.radio_vision = 8
            self.gasto_energia = 2
            self.velocidad = 'rápida'
        elif estrategia == 'conservadora':
            self.radio_vision = 4
            self.gasto_energia = 1
            self.velocidad = 'lenta'
        else:  # equilibrada
            self.radio_vision = 6
            self.gasto_energia = 1.5
            self.velocidad = 'media'
        
        print(f"   🤖 Agente {self.id} creado - Estrategia: {estrategia.upper()}")
        print(f"      Energía: {self.energia} | Visión: {self.radio_vision} | Gasto: {self.gasto_energia}")
    
    def percibir(self):
        """Percibe comida dentro de su radio de visión"""
        return self.entorno.obtener_comida_cercana(self.x, self.y, self.radio_vision)
    
    def decidir_objetivo(self, otros_agentes):
        """Decide hacia qué comida ir, considerando la competencia"""
        comida_visible = self.percibir()
        
        if not comida_visible:
            return None
        
        # Estrategia agresiva: ir a la comida más cercana sin importar otros
        if self.estrategia == 'agresiva':
            objetivo = min(comida_visible, 
                         key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
            print(f"      💪 Agente {self.id} (AGRESIVA): Objetivo {objetivo} - distancia {abs(objetivo[0] - self.x) + abs(objetivo[1] - self.y)}")
            return objetivo
        
        # Estrategia conservadora: evitar comida que esté cerca de otros agentes
        elif self.estrategia == 'conservadora':
            comida_segura = []
            for comida in comida_visible:
                # Verificar si hay otros agentes cerca de esa comida
                otros_cerca = False
                for otro in otros_agentes:
                    if otro.vivo:
                        dist_otro = abs(comida[0] - otro.x) + abs(comida[1] - otro.y)
                        if dist_otro < 3:  # Si otro está muy cerca, evitar
                            otros_cerca = True
                            break
                if not otros_cerca:
                    comida_segura.append(comida)
            
            if comida_segura:
                objetivo = min(comida_segura,
                             key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))
                print(f"      🛡️  Agente {self.id} (CONSERVADORA): Objetivo seguro {objetivo}")
                return objetivo
            else:
                print(f"      🛡️  Agente {self.id} (CONSERVADORA): No hay comida segura, esperando...")
                return None
        
        # Estrategia equilibrada: balance entre distancia y competencia
        else:
            mejor_comida = None
            mejor_puntuacion = -1
            
            for comida in comida_visible:
                dist = abs(comida[0] - self.x) + abs(comida[1] - self.y)
                
                # Contar cuántos agentes están cerca de esta comida
                competidores = 0
                for otro in otros_agentes:
                    if otro.vivo:
                        dist_otro = abs(comida[0] - otro.x) + abs(comida[1] - otro.y)
                        if dist_otro < dist:  # Si otro está más cerca
                            competidores += 1
                
                # Puntuación: menor es mejor (distancia baja, pocos competidores)
                puntuacion = dist + competidores * 3
                
                if mejor_comida is None or puntuacion < mejor_puntuacion:
                    mejor_comida = comida
                    mejor_puntuacion = puntuacion
            
            if mejor_comida:
                print(f"      ⚖️  Agente {self.id} (EQUILIBRADA): Objetivo {mejor_comida} - puntuación {mejor_puntuacion:.1f}")
            return mejor_comida
    
    def actuar(self, objetivo):
        """Ejecuta movimiento hacia el objetivo"""
        if not self.vivo:
            return
        
        # Gastar energía
        self.energia -= self.gasto_energia
        self.pasos_dados += 1
        
        if self.energia <= 0:
            self.vivo = False
            print(f"      💀 Agente {self.id} se quedó SIN ENERGÍA y murió!")
            return
        
        # Recolectar si está sobre comida
        if self.entorno.hay_comida(self.x, self.y):
            if self.entorno.recolectar_comida(self.x, self.y):
                self.comida_recolectada += 1
                self.energia += 30  # Recuperar energía
                print(f"      🍎 Agente {self.id} RECOLECTÓ comida! Energía: {self.energia:.1f} | Total: {self.comida_recolectada}")
                return
        
        # Moverse hacia objetivo
        if objetivo:
            dx = 1 if objetivo[0] > self.x else -1 if objetivo[0] < self.x else 0
            dy = 1 if objetivo[1] > self.y else -1 if objetivo[1] < self.y else 0
            
            nueva_x = self.x
            nueva_y = self.y
            
            if dx != 0:
                nueva_x = max(0, min(self.entorno.ancho - 1, self.x + dx))
            elif dy != 0:
                nueva_y = max(0, min(self.entorno.alto - 1, self.y + dy))
            
            if nueva_x != self.x or nueva_y != self.y:
                print(f"      ➡️  Agente {self.id} se movió a ({nueva_x},{nueva_y}) - Energía: {self.energia:.1f}")
                self.x = nueva_x
                self.y = nueva_y
        else:
            # Movimiento aleatorio si no hay objetivo
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            self.x = max(0, min(self.entorno.ancho - 1, self.x + dx))
            self.y = max(0, min(self.entorno.alto - 1, self.y + dy))


class EntornoCompetitivo:
    """Entorno con recursos limitados para competencia"""
    
    def __init__(self, ancho, alto, comida_inicial):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        self.comida_total_inicial = comida_inicial
        
        # Generar comida inicial (limitada)
        for _ in range(comida_inicial):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            self.comida.add((x, y))
        
        print(f"   🌍 Entorno: {ancho}x{alto} con {len(self.comida)} recursos iniciales")
    
    def hay_comida(self, x, y):
        return (x, y) in self.comida
    
    def recolectar_comida(self, x, y):
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False
    
    def obtener_comida_cercana(self, x, y, radio):
        return [pos for pos in self.comida 
                if abs(pos[0] - x) + abs(pos[1] - y) <= radio]


class VisualizadorCompetencia:
    """Visualizador para agentes en competencia"""
    
    def __init__(self, entorno, agentes):
        self.entorno = entorno
        self.agentes = agentes
        self.fig, self.axes = plt.subplots(1, 2, figsize=(16, 7))
        self.ax_grid = self.axes[0]
        self.ax_stats = self.axes[1]
        self.paso_actual = 0
        self.historial_energia = {agente.id: [] for agente in agentes}
        self.historial_comida = {agente.id: [] for agente in agentes}
        
        self.fig.suptitle('Ejercicio 6: Agentes Compitiendo por Recursos Limitados', 
                         fontsize=16, fontweight='bold')
    
    def actualizar(self):
        """Actualiza la visualización"""
        self.ax_grid.clear()
        self.ax_stats.clear()
        
        # --- Panel izquierdo: Grid ---
        self.ax_grid.set_xlim(-0.5, self.entorno.ancho - 0.5)
        self.ax_grid.set_ylim(-0.5, self.entorno.alto - 0.5)
        self.ax_grid.set_aspect('equal')
        self.ax_grid.set_title(f'Campo de Batalla - Paso {self.paso_actual}', 
                              fontsize=14, fontweight='bold')
        self.ax_grid.invert_yaxis()
        
        # Dibujar grid
        for x in range(self.entorno.ancho):
            for y in range(self.entorno.alto):
                rect = Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, 
                               facecolor='#F5F5DC', edgecolor='gray', linewidth=0.5)
                self.ax_grid.add_patch(rect)
        
        # Dibujar comida
        for (x, y) in self.entorno.comida:
            circulo = plt.Circle((x, y), 0.35, color='#FFD700', 
                               edgecolor='#FF8C00', linewidth=2, alpha=0.9)
            self.ax_grid.add_patch(circulo)
        
        # Dibujar agentes
        for agente in self.agentes:
            if agente.vivo:
                # Círculo del agente
                circulo = plt.Circle((agente.x, agente.y), 0.4, 
                                   color=agente.color, alpha=0.9, 
                                   edgecolor='black', linewidth=1.5, zorder=4)
                self.ax_grid.add_patch(circulo)
                
                # Número del agente
                self.ax_grid.text(agente.x, agente.y, str(agente.id), 
                                ha='center', va='center', 
                                fontsize=11, fontweight='bold', color='white', zorder=5)
                
                # Barra de energía sobre el agente
                barra_ancho = 0.8
                barra_alto = 0.15
                energia_porcentaje = agente.energia / 100
                
                # Fondo de la barra (rojo)
                rect_fondo = Rectangle((agente.x - barra_ancho/2, agente.y - 0.7), 
                                      barra_ancho, barra_alto,
                                      facecolor='red', edgecolor='black', linewidth=0.5, zorder=6)
                self.ax_grid.add_patch(rect_fondo)
                
                # Barra de energía (verde)
                if energia_porcentaje > 0:
                    color_energia = 'green' if energia_porcentaje > 0.5 else 'orange' if energia_porcentaje > 0.25 else 'red'
                    rect_energia = Rectangle((agente.x - barra_ancho/2, agente.y - 0.7), 
                                            barra_ancho * energia_porcentaje, barra_alto,
                                            facecolor=color_energia, zorder=7)
                    self.ax_grid.add_patch(rect_energia)
            else:
                # Agente muerto (calavera)
                self.ax_grid.text(agente.x, agente.y, '💀', 
                                ha='center', va='center', fontsize=20, zorder=3)
        
        self.ax_grid.set_xticks(range(self.entorno.ancho))
        self.ax_grid.set_yticks(range(self.entorno.alto))
        self.ax_grid.grid(True, alpha=0.3)
        
        # --- Panel derecho: Estadísticas ---
        self.ax_stats.axis('off')
        
        y_pos = 0.95
        self.ax_stats.text(0.5, y_pos, 'ESTADÍSTICAS DE COMPETENCIA', ha='center', 
                          fontsize=13, fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos = 0.89
        self.ax_stats.text(0.1, y_pos, f'Paso: {self.paso_actual}', 
                          fontsize=11, transform=self.ax_stats.transAxes)
        y_pos -= 0.05
        recursos_restantes = len(self.entorno.comida)
        porcentaje = (recursos_restantes / self.entorno.comida_total_inicial) * 100
        self.ax_stats.text(0.1, y_pos, f'Recursos restantes: {recursos_restantes} ({porcentaje:.1f}%)', 
                          fontsize=11, fontweight='bold', color='red',
                          transform=self.ax_stats.transAxes)
        
        # Ranking de agentes
        y_pos -= 0.1
        self.ax_stats.text(0.5, y_pos, 'RANKING DE AGENTES', ha='center', 
                          fontsize=12, fontweight='bold', transform=self.ax_stats.transAxes)
        
        # Ordenar agentes por comida recolectada
        agentes_ordenados = sorted(self.agentes, key=lambda a: a.comida_recolectada, reverse=True)
        
        y_pos -= 0.06
        for i, agente in enumerate(agentes_ordenados):
            # Emoji de posición
            if i == 0:
                emoji = '🥇'
            elif i == 1:
                emoji = '🥈'
            elif i == 2:
                emoji = '🥉'
            else:
                emoji = f'{i+1}.'
            
            # Color del agente
            circulo = Circle((0.08, y_pos), 0.015, color=agente.color, 
                           transform=self.ax_stats.transAxes)
            self.ax_stats.add_patch(circulo)
            
            # Estado
            estado = '✅' if agente.vivo else '💀'
            
            # Texto
            texto = f"{emoji} Agente {agente.id} ({agente.estrategia[:3].upper()}): {agente.comida_recolectada} comida | E:{agente.energia:.0f} {estado}"
            color_texto = 'black' if agente.vivo else 'gray'
            self.ax_stats.text(0.12, y_pos, texto, 
                             fontsize=9, color=color_texto, transform=self.ax_stats.transAxes,
                             verticalalignment='center')
            y_pos -= 0.05
        
        # Información por estrategia
        y_pos -= 0.05
        self.ax_stats.text(0.5, y_pos, 'POR ESTRATEGIA', ha='center', 
                          fontsize=11, fontweight='bold', transform=self.ax_stats.transAxes)
        
        y_pos -= 0.05
        estrategias = {}
        for agente in self.agentes:
            if agente.estrategia not in estrategias:
                estrategias[agente.estrategia] = {'total': 0, 'vivos': 0, 'comida': 0}
            estrategias[agente.estrategia]['total'] += 1
            if agente.vivo:
                estrategias[agente.estrategia]['vivos'] += 1
            estrategias[agente.estrategia]['comida'] += agente.comida_recolectada
        
        for estrategia, datos in estrategias.items():
            promedio = datos['comida'] / datos['total']
            self.ax_stats.text(0.1, y_pos, 
                             f"{estrategia.capitalize()}: {datos['vivos']}/{datos['total']} vivos | Promedio: {promedio:.1f}", 
                             fontsize=9, transform=self.ax_stats.transAxes)
            y_pos -= 0.04
        
        # Leyenda
        y_pos = 0.18
        self.ax_stats.text(0.5, y_pos, 'LEYENDA', ha='center', fontsize=11, 
                          fontweight='bold', transform=self.ax_stats.transAxes)
        y_pos -= 0.05
        
        elementos = [
            ('#FFD700', 'Recurso (comida)'),
            ('green', 'Barra energía > 50%'),
            ('orange', 'Barra energía 25-50%'),
            ('red', 'Barra energía < 25%'),
        ]
        
        for color, texto in elementos:
            rect = Rectangle((0.08, y_pos - 0.015), 0.03, 0.03, 
                           facecolor=color, edgecolor='black', linewidth=0.5,
                           transform=self.ax_stats.transAxes)
            self.ax_stats.add_patch(rect)
            self.ax_stats.text(0.13, y_pos, f'= {texto}', 
                             fontsize=8, transform=self.ax_stats.transAxes)
            y_pos -= 0.04
        
        y_pos -= 0.02
        self.ax_stats.text(0.1, y_pos, '💀 = Agente eliminado', 
                          fontsize=8, transform=self.ax_stats.transAxes)
        
        plt.tight_layout()


def simular_competencia(num_agentes=6, recursos_iniciales=25, pasos=200, velocidad=0.2):
    """Ejecuta la simulación del ejercicio 6"""
    
    entorno = EntornoCompetitivo(14, 14, recursos_iniciales)
    agentes = []
    
    print("=" * 80)
    print("EJERCICIO 6: COMPETENCIA POR RECURSOS LIMITADOS")
    print("=" * 80)
    print(f"\n⚔️  CONFIGURACIÓN DE LA COMPETENCIA:")
    print(f"   Número de agentes: {num_agentes}")
    print(f"   Recursos iniciales: {recursos_iniciales}")
    print(f"   Área de combate: {entorno.ancho}x{entorno.alto}")
    print("\n🎮 CREANDO AGENTES:")
    
    # Colores y estrategias
    colores = ['#FF1493', '#4169E1', '#32CD32', '#FF8C00', '#9370DB', '#DC143C']
    estrategias = ['agresiva', 'conservadora', 'equilibrada']
    
    # Crear agentes con diferentes estrategias
    for i in range(num_agentes):
        x = random.randint(0, entorno.ancho - 1)
        y = random.randint(0, entorno.alto - 1)
        color = colores[i % len(colores)]
        estrategia = estrategias[i % len(estrategias)]
        agentes.append(AgenteCompetitivo(i + 1, x, y, entorno, color, estrategia))
    
    visualizador = VisualizadorCompetencia(entorno, agentes)
    
    print("\n" + "=" * 80)
    print("🚀 INICIANDO SIMULACIÓN...")
    print("=" * 80)
    
    plt.ion()
    visualizador.actualizar()
    plt.pause(2)
    
    for paso in range(pasos):
        visualizador.paso_actual = paso + 1
        
        print(f"\n{'='*80}")
        print(f"⏱️  PASO {paso + 1}")
        print(f"{'='*80}")
        print(f"   Recursos disponibles: {len(entorno.comida)}")
        print(f"   Agentes vivos: {sum(1 for a in agentes if a.vivo)}/{len(agentes)}")
        
        # Cada agente decide y actúa
        for agente in agentes:
            if agente.vivo:
                print(f"\n   👤 AGENTE {agente.id} ({agente.estrategia.upper()}):")
                otros = [a for a in agentes if a.id != agente.id]
                objetivo = agente.decidir_objetivo(otros)
                agente.actuar(objetivo)
        
        # Actualizar visualización
        visualizador.actualizar()
        plt.pause(velocidad)
        
        # Verificar si la ventana fue cerrada
        if not plt.fignum_exists(visualizador.fig.number):
            print("\n⛔ Simulación detenida por el usuario.")
            break
        
        # Condiciones de salida
        agentes_vivos = [a for a in agentes if a.vivo]
        if len(agentes_vivos) == 0:
            print("\n💀 Todos los agentes han muerto!")
            break
        
        if len(entorno.comida) == 0:
            print("\n🏁 Se acabaron los recursos!")
            break
    
    # Reporte final
    print("\n" + "=" * 80)
    print("🏆 REPORTE FINAL - RESULTADOS DE LA COMPETENCIA")
    print("=" * 80)
    print(f"Duración: {visualizador.paso_actual} pasos")
    print(f"Recursos restantes: {len(entorno.comida)}")
    print(f"Agentes supervivientes: {sum(1 for a in agentes if a.vivo)}/{len(agentes)}")
    
    print(f"\n📊 RANKING FINAL:")
    agentes_ordenados = sorted(agentes, key=lambda a: a.comida_recolectada, reverse=True)
    
    for i, agente in enumerate(agentes_ordenados):
        estado = "VIVO ✅" if agente.vivo else "MUERTO 💀"
        eficiencia = agente.comida_recolectada / max(agente.pasos_dados, 1)
        print(f"{i+1}. Agente {agente.id} ({agente.estrategia.upper():12}) - "
              f"{agente.comida_recolectada:2} comida | "
              f"Energía: {agente.energia:5.1f} | "
              f"Eficiencia: {eficiencia:.3f} | "
              f"{estado}")
    
    # Análisis por estrategia
    print(f"\n🎯 ANÁLISIS POR ESTRATEGIA:")
    estrategias_stats = {}
    for agente in agentes:
        if agente.estrategia not in estrategias_stats:
            estrategias_stats[agente.estrategia] = {
                'total': 0, 'vivos': 0, 'comida': 0, 'energia': 0
            }
        estrategias_stats[agente.estrategia]['total'] += 1
        if agente.vivo:
            estrategias_stats[agente.estrategia]['vivos'] += 1
        estrategias_stats[agente.estrategia]['comida'] += agente.comida_recolectada
        estrategias_stats[agente.estrategia]['energia'] += agente.energia
    
    for estrategia, stats in sorted(estrategias_stats.items()):
        promedio_comida = stats['comida'] / stats['total']
        promedio_energia = stats['energia'] / stats['total']
        tasa_supervivencia = (stats['vivos'] / stats['total']) * 100
        print(f"\n{estrategia.upper()}:")
        print(f"   Supervivencia: {stats['vivos']}/{stats['total']} ({tasa_supervivencia:.0f}%)")
        print(f"   Comida promedio: {promedio_comida:.1f}")
        print(f"   Energía promedio: {promedio_energia:.1f}")
    
    # Ganador
    ganador = agentes_ordenados[0]
    print(f"\n🏆 GANADOR: Agente {ganador.id} ({ganador.estrategia.upper()}) "
          f"con {ganador.comida_recolectada} recursos!")
    
    print("=" * 80)
    print("\nCierra la ventana de matplotlib para finalizar.")
    plt.show()


if __name__ == "__main__":
    simular_competencia(num_agentes=6, recursos_iniciales=30, pasos=250, velocidad=0.15)
