from controller import Supervisor, DistanceSensor, Motor, LED, Gyro, Accelerometer, Camera
import math

# Inicialización del objeto Supervisor
robot = Supervisor()

# Configuración del paso de tiempo
TIMESTEP = int(robot.getBasicTimeStep())
MAX_SPEED = 6.28  # Velocidad máxima de los motores [cite: 109]

# --- 1. INICIALIZACIÓN DE SENSORES [cite: 102] ---
ps_names = ['ps0', 'ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7']
prox_sensors = []
for name in ps_names:
    sensor = robot.getDevice(name)
    sensor.enable(TIMESTEP)
    prox_sensors.append(sensor)

gyro = robot.getDevice('gyro')
gyro.enable(TIMESTEP)

accelerometer = robot.getDevice('accelerometer')
accelerometer.enable(TIMESTEP)

# Inicializar y configurar Cámara (Requerimiento del proyecto) [cite: 107]
camera = robot.getDevice('camera')
camera.enable(TIMESTEP)

# --- 2. INICIALIZACIÓN DE ACTUADORES [cite: 108] ---
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

led_names = ['led0', 'led1', 'led2', 'led3', 'led4', 'led5', 'led6', 'led7']
leds = [robot.getDevice(name) for name in led_names]

# --- VARIABLES DE CONTROL ---
estado = 'RESOLVIENDO'
bucle_led = 0
robot_nodo = robot.getSelf()
mensaje_meta_impreso = False

# --- ADICIÓN: VARIABLES PARA MÉTRICAS DE DESEMPEÑO ---
tiempo_inicio = robot.getTime()
colisiones = 0
distancia_total = 0
posicion_anterior = robot_nodo.getPosition() if robot_nodo else [0, 0, 0]

def apagar_leds():
    for led in leds:
        led.set(0)

print("Iniciando resolución del laberinto (Algoritmo: Seguir Pared Derecha)...")

# --- BUCLE PRINCIPAL DE SIMULACIÓN ---
while robot.step(TIMESTEP) != -1:
    bucle_led += 1
    
    # 1. LEER DATOS DE LOS SENSORES
    ps_values = [sensor.getValue() for sensor in prox_sensors]
    gyro_values = gyro.getValues()
    acc_values = accelerometer.getValues()
    
    # Los sensores de proximidad también funcionan como sensores de luz
    # Usamos el valor promedio de los 8 sensores como indicador de luminosidad
    light_value = sum(ps_values) / len(ps_values)
    
    # Obtener imagen de la cámara para procesamiento de color [cite: 107]
    camera_image = camera.getImage()
    width = camera.getWidth()
    height = camera.getHeight()

    # --- CÁLCULO DE DISTANCIA RECORRIDA ---
    if robot_nodo:
        posicion_actual = robot_nodo.getPosition()
        dx = posicion_actual[0] - posicion_anterior[0]
        dz = posicion_actual[2] - posicion_anterior[2]
        distancia_recorrida = math.sqrt(dx*dx + dz*dz)
        distancia_total += distancia_recorrida
        posicion_anterior = posicion_actual

    color_meta_detectado = False
    if camera_image:
        pixeles_amarillos = 0
        # Muestrear una cuadrícula central de la imagen de la cámara para optimizar velocidad
        for x in range(0, width, 2):
            for y in range(0, height, 2):
                red = camera.imageGetRed(camera_image, width, x, y)
                green = camera.imageGetGreen(camera_image, width, x, y)
                blue = camera.imageGetBlue(camera_image, width, x, y)
                
                # El amarillo de la meta tiene alto Rojo y Verde, y bajo Azul (1.0, 0.84, 0.0) 
                if red > 200 and green > 160 and blue < 50:
                    pixeles_amarillos += 1
        
        # Si más del 15% de la zona central visible es amarilla y estamos muy cerca de una pared
        if pixeles_amarillos > ((width * height) / 4) * 0.15 and (ps_values[0] > 80 or ps_values[7] > 80):
            color_meta_detectado = True

    # Verificación de respaldo por coordenadas absolutas corregidas (Eje Z global en Webots)
    coordenada_meta_alcanzada = False
    if robot_nodo:
        posicion_actual = robot_nodo.getPosition()
        # CORREGIDO: eliminar el espacio adicional antes de 'if'
        if abs(posicion_actual[0] - 0.0) < 0.25 and posicion_actual[1] <= -1.10:
            coordenada_meta_alcanzada = True

    # Combinación de criterios para asegurar una parada perfecta en la zona dorada 
    if color_meta_detectado or coordenada_meta_alcanzada:
        estado = 'META'

    # 3. MÁQUINA DE ESTADOS
    if estado == 'META':
        # Detener motores inmediatamente [cite: 109]
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        
        # Juego de luces dinámico y festivo en los LEDs (Meta alcanzada) [cite: 48, 110]
        for i, led in enumerate(leds):
            led.set(1 if (bucle_led // 4) % 2 == 0 else 0)
        
        # --- MÉTRICAS DE DESEMPEÑO AL FINALIZAR ---
        if not mensaje_meta_impreso:
            tiempo_final = robot.getTime() - tiempo_inicio
            print("ya llego a la meta")
            print("=== MÉTRICAS DE DESEMPEÑO ===")
            print(f"Tiempo total: {tiempo_final:.2f} segundos")
            print(f"Colisiones detectadas: {colisiones}")
            print(f"Distancia recorrida: {distancia_total:.2f} metros")
            print(f"Nivel de luz promedio: {light_value:.2f}")
            mensaje_meta_impreso = True
        
        continue

    # --- DETECCIÓN DE COLISIONES ---
    if ps_values[0] > 95.0 or ps_values[7] > 95.0:
        colisiones += 1

    # 4. ALGORITMO DE SEGUIMIENTO DE PARED DERECHA (WALL FOLLOWING) [cite: 120]
    UMBRAL_FRONTAL = 95.0   # Detección de obstáculos frontales (ps0 y ps7) [cite: 104]
    UMBRAL_PARED = 80.0     # Detección de pared lateral derecha (ps1 o ps2) [cite: 104]
    
    hay_pared_enfrente = ps_values[0] > UMBRAL_FRONTAL or ps_values[7] > UMBRAL_FRONTAL
    hay_pared_derecha = ps_values[1] > UMBRAL_PARED or ps_values[2] > UMBRAL_PARED

    # Velocidades base rápidas para resolver el laberinto en menor tiempo
    vel_izquierda = MAX_SPEED * 0.9        # [cite: 109]
    vel_derecha = MAX_SPEED * 0.9          # [cite: 109]

    if hay_pared_enfrente:
        # Esquina o bloqueo: Giro rápido sobre su propio eje hacia la izquierda
        vel_izquierda = -MAX_SPEED * 0.5   # [cite: 109]
        vel_derecha = MAX_SPEED * 0.6      # [cite: 109]
        
        # LEDs izquierdos encendidos como direccionales [cite: 48, 110]
        apagar_leds()
        leds[5].set(1)
        leds[6].set(1)
        
    elif hay_pared_derecha:
        # Seguimiento e interpolación de distancia con la pared derecha [cite: 120]
        if ps_values[1] > 120 or ps_values[2] > 120:
            # Demasiado cerca: corregir suavemente hacia la izquierda
            vel_izquierda = MAX_SPEED * 0.5  # [cite: 109]
            vel_derecha = MAX_SPEED * 0.95   # [cite: 109]
        elif ps_values[1] < 85:
            # Alejándose: corregir inclinándose hacia la derecha
            vel_izquierda = MAX_SPEED * 0.95 # [cite: 109]
            vel_derecha = MAX_SPEED * 0.5    # [cite: 109]
            
        # Animación secuencial normal en los LEDs durante la navegación activa [cite: 48]
        apagar_leds()
        leds[bucle_led % 8].set(1)
    else:
        # Apertura a la derecha detectada (Pasillo libre disponible)
        # Girar de forma inmediata a la derecha para avanzar por la nueva ruta [cite: 47]
        vel_izquierda = MAX_SPEED * 0.8    # [cite: 109]
        vel_derecha = MAX_SPEED * 0.2      # [cite: 109]
        
        # LEDs derechos activos [cite: 110]
        apagar_leds()
        leds[1].set(1)
        leds[2].set(1)

    left_motor.setVelocity(vel_izquierda)
    right_motor.setVelocity(vel_derecha)