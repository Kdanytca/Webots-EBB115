# Navegación Autónoma de un Robot E-Puck en un Laberinto Simulado con Webots

## Descripción

Este proyecto implementa un sistema de navegación autónoma para el robot E-Puck utilizando el simulador Webots y el lenguaje Python. El objetivo principal es que el robot sea capaz de recorrer un laberinto de forma autónoma, evitando obstáculos, tomando decisiones de movimiento basadas en información sensorial y alcanzando una meta definida dentro del entorno.

La solución utiliza una estrategia de navegación basada en el algoritmo clásico **Right Wall Follower (Seguir Pared Derecha)**, permitiendo al robot desplazarse por el laberinto sin requerir un mapa previo del entorno.

---

## Objetivos

* Implementar un sistema de navegación autónoma para el robot E-Puck.
* Utilizar sensores y actuadores integrados en Webots.
* Detectar y evitar obstáculos durante el recorrido.
* Mantener una trayectoria estable mediante control diferencial de motores.
* Identificar la meta utilizando visión por computadora.
* Registrar métricas de desempeño para evaluar el comportamiento del sistema.

---

## Tecnologías Utilizadas

* Python
* Webots
* Robot E-Puck

---

## Sensores Implementados

### Sensores de Proximidad Infrarrojos (IR)

Utilizados para detectar paredes y obstáculos cercanos. El sistema emplea los ocho sensores disponibles (`ps0` a `ps7`) para determinar la presencia de obstáculos frontales y laterales.

### Giroscopio

Inicializado para obtener información relacionada con la orientación angular del robot durante la navegación.

### Acelerómetro

Utilizado para monitorear el comportamiento dinámico del robot y disponer de información relacionada con estabilidad e impactos.

### Cámara

Empleada para detectar visualmente la zona objetivo mediante reconocimiento del color amarillo presente en la meta.

---

## Actuadores Implementados

### Motores Diferenciales

Permiten controlar de forma independiente la velocidad de cada rueda para realizar movimientos de avance, corrección de trayectoria y giros.

### LEDs

Los ocho LEDs del robot son utilizados para representar visualmente el estado actual del sistema:

* Navegación normal.
* Giro hacia la izquierda.
* Giro hacia la derecha.
* Meta alcanzada.

---

## Algoritmo de Navegación

El sistema implementa el algoritmo **Seguir Pared Derecha**, ampliamente utilizado para la resolución de laberintos simplemente conexos.

### Lógica General

1. Si existe una pared enfrente, el robot gira a la izquierda.
2. Si existe una pared a la derecha, continúa avanzando manteniendo una distancia segura.
3. Si no existe una pared a la derecha, gira hacia la derecha para explorar un nuevo pasillo.

Esta estrategia permite recorrer el laberinto de manera continua hasta localizar la zona objetivo.

---

## Máquina de Estados

El comportamiento del robot se organiza mediante una máquina de estados compuesta por dos estados principales:

### RESOLVIENDO

Estado principal de navegación.

Funciones:

* Lectura continua de sensores.
* Seguimiento de pared derecha.
* Evasión de obstáculos.
* Activación secuencial de LEDs.

### META

Estado final del recorrido.

Funciones:

* Detención inmediata de motores.
* Activación de secuencia especial de LEDs.
* Impresión de métricas finales de desempeño.

---

## Detección de la Meta

La meta se identifica mediante dos mecanismos complementarios:

### Detección Visual

La cámara analiza la imagen capturada y busca regiones con predominancia del color amarillo.

### Verificación por Posición

Se realiza una validación adicional utilizando las coordenadas del robot dentro del entorno para asegurar una detección correcta de la zona objetivo.

---

## Métricas Registradas

Durante la ejecución se recopilan métricas que permiten evaluar el desempeño del algoritmo:

* Tiempo total de recorrido.
* Distancia recorrida.
* Número de colisiones detectadas.
* Nivel de iluminación promedio.

Estas métricas son mostradas automáticamente cuando el robot alcanza la meta.

---

## Estructura del Proyecto

```text
controllers/
└── epuck_controller.py

worlds/
└── tarea2_epuck.wbt

README.md
```

---

## Ejecución

1. Abrir el proyecto en Webots.
2. Cargar el mundo del laberinto.
3. Asociar el controlador Python al robot E-Puck.
4. Ejecutar la simulación.
5. Observar el recorrido autónomo y las métricas generadas al finalizar.

---

## Resultados

El sistema logra:

* Navegar de forma autónoma dentro del laberinto.
* Evitar colisiones mediante sensores infrarrojos.
* Mantener una trayectoria estable utilizando seguimiento de pared.
* Detectar correctamente la meta mediante visión basada en color.
* Generar métricas de desempeño para análisis posterior.

---

## Autor

Kevin Daniel Vásquez Alegría
Universidad de El Salvador
Facultad de Ingeniería y Arquitectura
Escuela de Ingeniería de Sistemas Informáticos
Asignatura: Sistemas Embebidos I
