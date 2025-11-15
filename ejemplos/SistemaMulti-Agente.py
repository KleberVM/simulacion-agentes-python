import random

class AgenteCooperativo:
    """Agente que puede comunicarse con otros para cooperar"""
    """Escenario: Múltiples agentes que cooperan para recolectar recursos. """
    
    def __init__(self, id, x, y, entorno):
        self.id = id
        self.x = x
        self.y = y
        self.entorno = entorno
        self.comida_recolectada = 0
        self.objetivo = None # Coordenada (x, y) de la comida que persigue
        self.mensajes = [] # Buzón de mensajes recibidos

    def enviar_mensaje(self, destinatarios, tipo, contenido):
        """Comunica información a una lista de otros agentes"""
        for agente in destinatarios:
            agente.recibir_mensaje(self.id, tipo, contenido)

    def recibir_mensaje(self, remitente, tipo, contenido):
        """Recibe un mensaje y lo guarda en el buzón"""
        self.mensajes.append({
            'de': remitente,
            'tipo': tipo,
            'contenido': contenido
        })

    def procesar_mensajes(self):
        """Procesa los mensajes recibidos para extraer información"""
        comida_reportada = []
        for msg in self.mensajes:
            if msg['tipo'] == 'comida_encontrada':
                comida_reportada.append(msg['contenido'])
        
        self.mensajes.clear() # Limpia el buzón después de leer
        return comida_reportada

    def percibir(self):
        """Percibe comida cercana en su radio de visión local"""
        return self.entorno.obtener_comida_cercana(self.x, self.y, radio=3)

    def decidir_y_actuar(self, otros_agentes):
        """Ciclo completo de decisión y acción del agente cooperativo"""
        
        # 1. Procesar comunicaciones
        comida_compartida = self.procesar_mensajes()

        # 2. Percibir entorno local
        comida_local = self.percibir()

        # 3. Compartir descubrimientos con otros
        if comida_local:
            for pos in comida_local:
                # Envía mensaje a todos los 'otros_agentes'
                self.enviar_mensaje(otros_agentes, 'comida_encontrada', pos)

        # 4. Decidir objetivo
        # Combina la comida local y la compartida, eliminando duplicados
        todas_opciones = list(set(comida_local + comida_compartida))

        if todas_opciones and not self.objetivo:
            # Elegir la comida más cercana de todas las opciones conocidas
            self.objetivo = min(todas_opciones,
                                key=lambda p: abs(p[0] - self.x) + abs(p[1] - self.y))

        # 5. Actuar (Moverse)
        if self.objetivo:
            # ¿Ya llegó al objetivo?
            if (self.x, self.y) == self.objetivo:
                if self.entorno.recolectar_comida(self.x, self.y):
                    self.comida_recolectada += 1
                self.objetivo = None # Limpiar objetivo para buscar uno nuevo
            else:
                # Movimiento simple hacia el objetivo (paso a paso)
                dx = 1 if self.objetivo[0] > self.x else -1 if self.objetivo[0] < self.x else 0
                dy = 1 if self.objetivo[1] > self.y else -1 if self.objetivo[1] < self.y else 0

                # Moverse en X o Y (no diagonal)
                if dx != 0:
                    self.x += dx
                elif dy != 0:
                    self.y += dy
        else:
            # Movimiento aleatorio si no hay objetivo
            direccion = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = self.x + direccion[0], self.y + direccion[1]
            if self.entorno.es_valido(nx, ny):
                self.x, self.y = nx, ny


class EntornoMultiAgente:
    """Entorno para múltiples agentes"""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.comida = set()
        
        # Generar comida
        for _ in range(15):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            self.comida.add((x, y))

    def es_valido(self, x, y):
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def obtener_comida_cercana(self, x, y, radio):
        """Retorna comida dentro del radio de visión (distancia Manhattan)"""
        return [pos for pos in self.comida 
                if abs(pos[0] - x) + abs(pos[1] - y) <= radio]

    def recolectar_comida(self, x, y):
        if (x, y) in self.comida:
            self.comida.remove((x, y))
            return True
        return False

    def mostrar(self, agentes):
        """Muestra el grid con los agentes (por ID) y la comida"""
        # Inicializa un grid vacío
        grid = [["⬜️" for _ in range(self.ancho)] for _ in range(self.alto)]
        
        # Coloca la comida
        for (x, y) in self.comida:
            grid[y][x] = "🍎"
            
        # Coloca los agentes (su ID)
        for agente in agentes:
            grid[agente.y][agente.x] = f"{agente.id} " # ID del agente

        # Imprime el grid
        for fila in grid:
            print(" ".join(fila))
        print()


# --- Simulación multi-agente ---
def simular_multi_agente(num_agentes=3, pasos=25):
    entorno = EntornoMultiAgente(10, 10)
    agentes = []

    # Crear los agentes en posiciones aleatorias
    for i in range(num_agentes):
        x, y = random.randint(0, 9), random.randint(0, 9)
        agentes.append(AgenteCooperativo(i + 1, x, y, entorno)) # IDs 1, 2, 3

    print("=== SIMULACIÓN: SISTEMA MULTI-AGENTE COOPERATIVO ===\n")
    print("Estado inicial:")
    entorno.mostrar(agentes)

    for paso in range(pasos):
        # Cada agente decide y actúa en cada paso
        for agente in agentes:
            # Define la lista de "otros" agentes para comunicarse
            otros = [a for a in agentes if a.id != agente.id]
            agente.decidir_y_actuar(otros)

        # Mostrar estado cada 5 pasos
        if (paso + 1) % 5 == 0:
            print(f"\n--- Paso {paso + 1} ---")
            entorno.mostrar(agentes)
            for agente in agentes:
                print(f"Agente {agente.id}: {agente.comida_recolectada} comida")

        # Condición de salida
        if len(entorno.comida) == 0:
            print("\n¡Toda la comida ha sido recolectada!")
            break

    # Reporte final
    print(f"\n--- Resultado final ---")
    total = sum(a.comida_recolectada for a in agentes)
    for agente in agentes:
        print(f"Agente {agente.id}: {agente.comida_recolectada} comida")
    print(f"Total recolectado: {total}")

# --- Ejecutar la simulación ---
simular_multi_agente()