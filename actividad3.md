# Programación Basada en Agentes con Python
**Actividad 3 de Taller de Simulación de Sistemas**
*Elaborado por: Lic. Henrry Frank Villarroel Tapia*

## 📜 Introducción
La programación basada en agentes es un paradigma de desarrollo de software donde el sistema se construye como una colección de entidades autónomas llamadas **agentes**. Este enfoque observa cómo funcionan los sistemas naturales: hormigas que buscan comida, bandadas de pájaros volando, las sociedades humanas y demás colectivos.

### ¿Por qué es importante?
La programación basada en agentes es fundamental porque permite implementar **Simulaciones** acerca de modelado de epidemias, tráfico urbano, economías y otros.

### Aspectos Centrales
En lugar de programar un sistema centralizado que controla todo, se crean múltiples agentes independientes que:
* Perciben su entorno local
* Toman decisiones propias
* Actúan de forma autónoma
* Interactúan con otros agentes

De estas interacciones simples emergen comportamientos complejos (emergencia).

---

## 🧠 Conceptos Fundamentales

### 1. ¿Qué es un Agente?
Un agente es una entidad computacional que opera por:

* **AUTONOMÍA:** Opera sin intervención directa constante.
    * *Ejemplo: Un robot aspiradora que decide por sí mismo dónde limpiar.*
* **PERCEPCIÓN:** Recibe información de su entorno mediante sensores.
    * *Ejemplo: Una cámara de auto autónomo detecta peatones y señales.*
* **ACCIÓN:** Modifica su entorno mediante actuadores.
    * *Ejemplo: Un personaje de videojuego que se mueve y dispara.*
* **OBJETIVOS:** Tiene metas que intenta alcanzar.
    * *Ejemplo: Un agente de trading que busca maximizar ganancias.*
* **RACIONALIDAD:** Elige acciones que lo acercan a sus objetivos.
    * *Ejemplo: Un GPS que selecciona la ruta más corta.*

### 2. Arquitectura de un Agente
El flujo básico de un agente es:
`ENTORNO → [SENSORES] → AGENTE → [ACTUADORES] → ENTORNO`
El agente internamente utiliza:
`[MEMORIA/ESTADO] → [LÓGICA DECISIÓN]`

**Componentes:**
* **Percepción (Sensores):** Qué información recibe el agente (puede ser completa o parcial).
* **Estado Interno:** La memoria del agente y sus creencias sobre el mundo.
* **Función de Decisión:** El "cerebro" del agente. Mapea percepciones a acciones.
* **Acción (Actuadores):** Qué puede hacer el agente para modificar el entorno.

### 3. Tipos de Agentes
1.  **Agente Reactivo Simple:** Responde directamente a percepciones, sin memoria (Ej: `SI [ve comida] ENTONCES [comer]`).
2.  **Agente Basado en Modelo:** Mantiene un modelo interno (memoria) del mundo.
3.  **Agente Basado en Objetivos:** Planifica secuencias de acciones para alcanzar metas (Ej: Calcular una ruta óptima).
4.  **Agente Basado en Utilidad:** Elige acciones que maximizan una función de "felicidad" o utilidad (Ej: Elegir la acción que da +10 puntos sobre la que da +7).
5.  **Agente con Aprendizaje:** Mejora su comportamiento con la experiencia (Ej: Observa resultados/recompensas y ajusta su estrategia).

### 4. Entorno del Agente
Define las reglas del mundo donde opera el agente. Sus propiedades pueden ser:

* **Observable** (Ajedrez) vs **Parcialmente Observable** (Poker)
* **Determinístico** (Crucigrama) vs **Estocástico** (Dados)
* **Episódico** (Clasificación de imágenes) vs **Secuencial** (Ajedrez)
* **Estático** (Sudoku) vs **Dinámico** (Conducir)
* **Discreto** (Tablero) vs **Continuo** (Espacio 3D)
* **Individual** (Solitario) vs **Multi-agente** (Fútbol)

### 5. Sistemas Multi-Agente (MAS)
Cuando múltiples agentes interactúan, pueden tener relaciones de:
* **Cooperación:** Agentes trabajan juntos hacia un objetivo común.
* **Competencia:** Agentes compiten por recursos limitados.
* **Coexistencia:** Agentes persiguen objetivos independientes.
* **Comunicación:** Agentes intercambian información (protocolos de mensajes, negociación).

---

## 🐍 Implementación en Python

### Instalación de Bibliotecas
```bash
# Para simulaciones básicas (no requiere instalación adicional)
# Usaremos: random, math, collections

# Para visualización avanzada (opcional)
pip install matplotlib numpy

# Para agentes más avanzados (opcional)
pip install mesa # Framework de simulación basada en agente
```

## Frameworks y Librerias Recomendadas

1. **Mesa:** Framework de simulación ABM (Agent Based Modeling).

```python
# pip install mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
# Simulaciones científicas y modelado social
```
2. **Pade** Plataforma de agentes distribuidos
```python
# pip install pade
# Simulaciones multi-agentes distribuidos
```
3. **spade** Sistema de agentes con XMPP
```python
# pip install spade
# Agentes comunicándose por internet
```
4. **Gym/Gymnasium** Entornos de aprendizaje por refuerzo
```python
# pip install gym gymnasium
# gentes con IA que aprenden 
```
---
## Conclucion

La programacion basada en agentes permite:

1. **Modelar sistemas complejos:** de forma modular y comprensible
2. **Crear comportamientos emergentes** sorprendentes a partir de reglas simples
3. **Simular y entender** sistemas naturales y sociales
4. **Desarrollar IA distribuida** y escalable
5. **Resolver problemas** que requieren coordinación y autonomía

### Principios Clave

1. **Un agente = Autonomía + Percepción + Decisión + Acción**
Estos cuatro elementos son fundamentales en cualquier agente
2. **La complejidad emerge de interacciones simples**
No necesitas programar el comportamiento complejo directamente
3. **No hay control central - cada agente decide por sí mismo**
La descentralización es clave para la escalabilidad
4. **El entorno define las reglas del juego**
Diseñar bien el entorno es tan importante como diseñar los agentes
5. **Incrementar complejidad gradualmente** Comenzar con agentes reactivos antes de agregar aprendizaje o comunicación
---

## Ejercicios propuestos para la actividad 3

La presentación de esta actividad se programa para fecha 17 de noviembre de los corrientes de acuerdo a lo especificado en programación de tareas de classroom, por supuesto considerando los formatos y modos ya establecidos.
Los puntos a considerar como tarea son: 

1. Modificar el agente limpiador para que recuerde lugares ya
visitados
2. Agregar diferentes tipos de suciedad con distintos valores
3. Implementar un agente que evite obstáculos fijos en el entorno
4. Implementar comunicación entre agentes recolectores para
evitar ir al mismo objetivo
5. Crear un agente que aprenda qué áreas tienen más comida
(memoria espacial)
6. Desarrollar un sistema donde agentes compitan por recursos
limitados