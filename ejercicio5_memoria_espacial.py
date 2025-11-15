"""
EJERCICIO 5: Agente que Aprende qué Áreas Tienen Más Comida (Memoria Espacial)
================================================================================
Implementación de un agente con aprendizaje que construye un mapa de calor
de las áreas donde encuentra más comida, optimizando su estrategia de búsqueda.

Características:
- Memoria espacial: Mapa de densidad de comida por región
- Aprendizaje por experiencia: Actualiza creencias según hallazgos
- Exploración vs. Explotación: Balance entre explorar nuevas áreas y explotar áreas conocidas
- Toma de decisiones basada en probabilidades
"""

import random
import math
from collections import defaultdict


class MemoriaEspacial:
    """
    Estructura de datos para almacenar información espacial sobre el entorno.
    
    Divide el entorno en regiones y mantiene estadísticas sobre cada una:
    - Visitas: Cuántas veces visitó la región
    - Comida encontrada: Cantidad de comida hallada en la región
    - Densidad: Comida por visita (indicador de productividad)
    
    Atributos:
        tamano_region: Tamaño de cada región (en celdas)
        regiones: Dict {(rx, ry): {'visitas': int, 'comida': int, 'densidad': float}}
    """
    
    def __init__(self, tamano_region=3):
        self.tamano_region = tamano_region
        self.regiones = defaultdict(lambda: {'visitas': 0, 'comida': 0, 'densidad': 0.0})
    
    def obtener_region(self, x, y):
        """
        Convierte coordenadas del mundo a coordenadas de región.
        
        Args:
            x, y: Coordenadas en el mundo
            
        Returns:
            tuple: (rx, ry) coordenadas de la región
        """
        rx = x // self.tamano_region
        ry = y // self.tamano_region
        return (rx, ry)
    
    def registrar_visita(self, x, y, encontro_comida=False):
        """
        Registra una visita a una posición y actualiza estadísticas.
        
        Args:
            x, y: Coordenadas visitadas
            encontro_comida: Si encontró comida en esa posición
        """
        region = self.obtener_region(x, y)
        self.regiones[region]['visitas'] += 1
        
        if encontro_comida:
            self.regiones[region]['comida'] += 1
        
        # Actualizar densidad (comida por visita)
        visitas = self.regiones[region]['visitas']
        comida = self.regiones[region]['comida']
        self.regiones[region]['densidad'] = comida / visitas if visitas > 0 else 0.0
    
    def obtener_densidad(self, x, y):
        """
        Obtiene la densidad de comida de una región.
        
        Returns:
            float: Densidad de comida (0.0 a 1.0+)
        """
        region = self.obtener_region(x, y)
        return self.regiones[region]['densidad']
    
    def obtener_mejor_region(self):
        """
        Encuentra la región con mayor densidad de comida.
        
        Returns:
            tuple: (rx, ry) de la mejor región, o None si no hay datos
        """
        if not self.regiones:
            return None
        
        mejor_region = max(
            self.regiones.items(),
            key=lambda item: item[1]['densidad']
        )
        
        return mejor_region[0] if mejor_region[1]['densidad'] > 0 else None
    
    def obtener_estadisticas(self):
        """Retorna un resumen de las estadísticas de memoria."""
        if not self.regiones:
            return "Sin datos"
        
        total_visitas = sum(r['visitas'] for r in self.regiones.values())
        total_comida = sum(r['comida'] for r in self.regiones.values())
        regiones_exploradas = len(self.regiones)
        
        return {
            'regiones_exploradas': regiones_exploradas,
            'total_visitas': total_visitas,
            'total_comida': total_comida,
            'densidad_promedio': total_comida / total_visitas if total_visitas > 0 else 0
        }


class AgenteConAprendizaje:
    """
    Agente que aprende sobre la distribución de comida en el entorno.
    
    Estrategia:
    - Explora el entorno y construye un mapa mental
    - Aprende qué regiones son más productivas
    - Balancea exploración (buscar nuevas áreas) con explotación (ir a áreas conocidas)
    
    Atributos:
        x, y: Posición actual
        entorno: Referencia al entorno
        memoria: Objeto MemoriaEspacial
        comida_recolectada: Contador de comida recolectada
        epsilon: Probabilidad de exploración (vs. explotación)
        pasos_totales: Contador de pasos dados
    """
    
    def __init__(self, x, y, entorno, tamano_region=3):
        self.x = x
        self.y = y
        self.entorno = entorno
        self.memoria = MemoriaEspacial(tamano_region)
        self.comida_recolectada = 0
        self.epsilon = 0.3  # 30% exploración, 70% explotación
        self.pasos_totales = 0
        self.objetivo_actual = None
    
    def percibir(self):
        """
        Percibe si hay comida en la posición actual.
        
        Returns:
            bool: True si hay comida
        """
        return self.entorno.hay_comida(self.x, self.y)
    
    def decidir_estrategia(self):
        """
        Decide entre exploración y explotación usando epsilon-greedy.
        
        Returns:
            str: 'explorar' o 'explotar'
        """
        if random.random() < self.epsilon:
            return 'explorar'
        else:
            return 'explotar'
    
    def seleccionar_objetivo_explotacion(self):
        """
        Selecciona un objetivo en la región con mayor densidad de comida.
        
        Returns:
            tuple: (x, y) objetivo en región productiva
        """
        mejor_region = self.memoria.obtener_mejor_region()
        
        if mejor_region is None:
            # Si no hay datos, explorar
            return self.seleccionar_objetivo_exploracion()
        
        # Convertir región a coordenadas del mundo
        rx, ry = mejor_region
        tamano = self.memoria.tamano_region
        
        # Seleccionar punto aleatorio dentro de esa región
        x = rx * tamano + random.randint(0, tamano - 1)
        y = ry * tamano + random.randint(0, tamano - 1)
        
        # Ajustar a límites del entorno
        x = max(0, min(x, self.entorno.ancho - 1))
        y = max(0, min(y, self.entorno.alto - 1))
        
        return (x, y)
    
    def seleccionar_objetivo_exploracion(self):
        """
        Selecciona un objetivo aleatorio para exploración.
        
        Returns:
            tuple: (x, y) objetivo aleatorio
        """
        x = random.randint(0, self.entorno.ancho - 1)
        y = random.randint(0, self.entorno.alto - 1)
        return (x, y)
    
    def decidir_y_actuar(self):
        """
        Ciclo completo de decisión y acción del agente.
        """
        # 1. Percibir entorno actual
        hay_comida = self.percibir()
        
        # 2. Registrar visita en memoria
        self.memoria.registrar_visita(self.x, self.y, hay_comida)
        
        # 3. Recolectar comida si hay
        if hay_comida:
            if self.entorno.recolectar_comida(self.x, self.y):
                self.comida_recolectada += 1
                self.objetivo_actual = None  # Buscar nuevo objetivo
        
        # 4. Decidir nuevo objetivo si no tiene uno
        if self.objetivo_actual is None or (self.x, self.y) == self.objetivo_actual:
            estrategia = self.decidir_estrategia()
            
            if estrategia == 'explotar':
                self.objetivo_actual = self.seleccionar_objetivo_explotacion()
            else:
                self.objetivo_actual = self.seleccionar_objetivo_exploracion()
        
        # 5. Moverse hacia el objetivo
        self.mover_hacia_objetivo()
        self.pasos_totales += 1
        
        # 6. Reducir epsilon con el tiempo (menos exploración, más explotación)
        # Decae exponencialmente: epsilon = epsilon_inicial * 0.995^pasos
        self.epsilon = max(0.1, self.epsilon * 0.995)
    
    def mover_hacia_objetivo(self):
        """Mueve el agente un paso hacia su objetivo actual."""
        if self.objetivo_actual is None:
            return
        
        dx = 0
        dy = 0
        
        if self.objetivo_actual[0] > self.x:
            dx = 1
        elif self.objetivo_actual[0] < self.x:
            dx = -1
        
        if self.objetivo_actual[1] > self.y:
            dy = 1
        elif self.objetivo_actual[1] < self.y:
            dy = -1
        
        # Priorizar movimiento en X o Y aleatoriamente
        if dx != 0 and dy != 0:
            if random.random() < 0.5:
                self.x += dx
            else:
                self.y += dy
        elif dx != 0:
            self.x += dx
        elif dy != 0:
            self.y += dy
        
        # Asegurar que esté dentro de límites
        self.x = max(0, min(self.x, self.entorno.ancho - 1))
        self.y = max(0, min(self.y, self.entorno.alto - 1))


class EntornoConDistribucionComida:
    """
    Entorno donde la comida se distribuye en clusters (áreas concentradas).
    
    Esto simula un entorno realista donde los recursos no están uniformemente
    distribuidos, sino que se concentran en ciertas áreas.
    
    Atributos:
        ancho, alto: Dimensiones del grid
        comida: Set de tuplas (x, y) con posiciones de comida
        comida_inicial: Cantidad inicial de comida (para estadísticas)
    """

    def __init__(self, ancho, alto, num_clusters=4, comida_por_cluster=8):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        
        # Generar clusters de comida
        for _ in range(num_clusters):
            # Centro del cluster
            cx = random.randint(2, ancho - 3)
            cy = random.randint(2, alto - 3)
            
            # Generar comida alrededor del centro
            for _ in range(comida_por_cluster):
                # Distribución normal alrededor del centro
                offset_x = int(random.gauss(0, 2))
                offset_y = int(random.gauss(0, 2))
                
                x = max(0, min(cx + offset_x, ancho - 1))
                y = max(0, min(cy + offset_y, alto - 1))
                
                self.comida.add((x, y))
        
        self.comida_inicial = len(self.comida)

    def hay_comida(self, x, y):
        """Verifica si hay comida en la posición."""
        return (x, y) in self.comida

    def recolectar_comida(self, x, y):
        """
        Recolecta comida si existe.
        
        Returns:
            bool: True si había comida y fue recolectada
        """
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False

    def mostrar(self, agente):
        """
        Visualización del entorno con mapa de calor de memoria.
        """
        for y in range(self.alto):
            fila = ""
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    fila += "🤖 "
                elif (x, y) in self.comida:
                    fila += "🍎 "
                else:
                    # Mostrar densidad aprendida con intensidad de color
                    densidad = agente.memoria.obtener_densidad(x, y)
                    if densidad > 0.5:
                        fila += "🟥 "  # Alta densidad
                    elif densidad > 0.3:
                        fila += "🟧 "  # Media-alta densidad
                    elif densidad > 0.1:
                        fila += "🟨 "  # Media densidad
                    elif densidad > 0:
                        fila += "⬜️ "  # Baja densidad
                    else:
                        fila += "⬛️ "  # No visitado
            print(fila)
        print()


# ============================================================================
# SIMULACIÓN
# ============================================================================

def simular_agente_con_aprendizaje(pasos=80):
    """
    Ejecuta la simulación del agente con memoria espacial.
    
    Args:
        pasos: Número máximo de pasos de simulación
    """
    # Crear entorno con comida en clusters
    entorno = EntornoConDistribucionComida(15, 12, num_clusters=5, comida_por_cluster=10)
    
    # Crear agente
    agente = AgenteConAprendizaje(7, 6, entorno, tamano_region=3)
    
    print("=" * 80)
    print("EJERCICIO 5: AGENTE CON MEMORIA ESPACIAL Y APRENDIZAJE")
    print("=" * 80)
    print("\nConcepto: El agente aprende qué áreas tienen más comida")
    print("Estrategia: Epsilon-greedy (exploración vs. explotación)")
    print("Memoria: Mapa de densidad de comida por región\n")
    print("Leyenda del mapa de calor:")
    print("  🟥 = Alta densidad de comida aprendida")
    print("  🟧 = Media-alta densidad")
    print("  🟨 = Media densidad")
    print("  ⬜️ = Baja densidad")
    print("  ⬛️ = Área no explorada\n")
    print("Estado inicial:")
    entorno.mostrar(agente)
    print(f"Comida total: {len(entorno.comida)}")
    print(f"Epsilon inicial: {agente.epsilon:.2f}\n")

    for paso in range(pasos):
        # El agente ejecuta su ciclo
        agente.decidir_y_actuar()
        
        # Mostrar estado cada 15 pasos
        if (paso + 1) % 15 == 0:
            print(f"\n{'='*80}")
            print(f"PASO {paso + 1}")
            print('='*80)
            entorno.mostrar(agente)
            
            stats = agente.memoria.obtener_estadisticas()
            print(f"Posición: ({agente.x}, {agente.y})")
            print(f"Comida recolectada: {agente.comida_recolectada}/{entorno.comida_inicial}")
            print(f"Comida restante: {len(entorno.comida)}")
            print(f"Epsilon actual: {agente.epsilon:.3f} (exploración)")
            print(f"\nMemoria espacial:")
            print(f"  - Regiones exploradas: {stats['regiones_exploradas']}")
            print(f"  - Total visitas: {stats['total_visitas']}")
            print(f"  - Densidad promedio: {stats['densidad_promedio']:.3f}")
            
            mejor_region = agente.memoria.obtener_mejor_region()
            if mejor_region:
                densidad = agente.memoria.regiones[mejor_region]['densidad']
                print(f"  - Mejor región: {mejor_region} (densidad: {densidad:.3f})")
        
        # Condición de salida
        if len(entorno.comida) == 0:
            print(f"\n{'='*80}")
            print("¡ÉXITO! Toda la comida ha sido recolectada")
            print('='*80)
            break
    
    # Reporte final
    print(f"\n{'='*80}")
    print("REPORTE FINAL")
    print('='*80)
    entorno.mostrar(agente)
    
    stats = agente.memoria.obtener_estadisticas()
    
    print(f"\n📊 Estadísticas de recolección:")
    print(f"  ✅ Comida recolectada: {agente.comida_recolectada}/{entorno.comida_inicial}")
    print(f"  ❌ Comida restante: {len(entorno.comida)}")
    print(f"  👣 Pasos totales: {agente.pasos_totales}")
    print(f"  ⚡ Eficiencia: {agente.comida_recolectada / agente.pasos_totales:.3f} comida/paso")
    
    print(f"\n🧠 Estadísticas de aprendizaje:")
    print(f"  📍 Regiones exploradas: {stats['regiones_exploradas']}")
    print(f"  🔍 Total de visitas: {stats['total_visitas']}")
    print(f"  📈 Densidad promedio aprendida: {stats['densidad_promedio']:.3f}")
    print(f"  🎯 Epsilon final: {agente.epsilon:.3f}")
    
    # Análisis de aprendizaje
    print(f"\n💡 Análisis:")
    if agente.comida_recolectada / entorno.comida_inicial > 0.8:
        print("  - Excelente desempeño en recolección")
    elif agente.comida_recolectada / entorno.comida_inicial > 0.6:
        print("  - Buen desempeño en recolección")
    else:
        print("  - Desempeño mejorable")
    
    if stats['densidad_promedio'] > 0.15:
        print("  - Aprendizaje efectivo: identificó áreas productivas")
    else:
        print("  - Aprendizaje en progreso: necesita más exploración")


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    simular_agente_con_aprendizaje()
