#MODULO DE SONIDOS
import pygame
import numpy as np
import sys

# Flag para saber si el sistema de audio esta disponible
sonido_habilitado = False
musica_habilitada = True  # Flag para activar/desactivar musica de fondo
# Canales de sonido (para reproducir multiples sonidos al mismo tiempo)
canal_movimiento = None
canal_rotacion = None
canal_drop = None
canal_linea = None

#inicializacion del sistema de sonido
def inicializar_sonidos():
    """ Inicializa el sistema de sonido de pygame.
    Retorna un bool: True si se inicializo correctamente, False si hubo error """
    global sonido_habilitado, canal_movimiento, canal_rotacion, canal_drop, canal_linea
    
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(8)  # Permitir 8 sonidos simultaneos
        
        # Asignar canales especificos
        canal_movimiento = pygame.mixer.Channel(0)
        canal_rotacion = pygame.mixer.Channel(1)
        canal_drop = pygame.mixer.Channel(2)
        canal_linea = pygame.mixer.Channel(3)
        
        sonido_habilitado = True
        print(" Sistema de sonido inicializado")
        return True
        
    except Exception as e:
        print(f" No se pudo inicializar el sonido: {e}")
        sonido_habilitado = False
        return False

def generar_tono(frecuencia, duracion, volumen=0.3):
    """ Genera un tono simple usando una onda sinusoidal.
        Parametros:
            frecuencia: Frecuencia en Hz (ej: 440 = LA)
            duracion: Duracion en segundos
            volumen: Volumen (0.0 a 1.0)
        Retorna:
            pygame.Sound: Objeto de sonido
    """
    sample_rate = 22050
    n_samples = int(sample_rate * duracion)
    
    # Generar onda sinusoidal
    buf = np.sin(2 * np.pi * frecuencia * np.linspace(0, duracion, n_samples))
    
    # Aplicar fade out para evitar clicks
    fade_len = int(sample_rate * 0.01)  # 10ms de fade
    fade = np.linspace(1, 0, fade_len)
    buf[-fade_len:] *= fade
    
    # Convertir a formato de audio
    buf = (buf * volumen * 32767).astype(np.int16)
    
    # Crear sonido stereo
    buf = np.repeat(buf.reshape(n_samples, 1), 2, axis=1)
    
    return pygame.sndarray.make_sound(buf)

def generar_beep_corto(frecuencia=440):
    #Genera un beep corto para movimientos
    return generar_tono(frecuencia, 0.05, 0.2)

def generar_beep_rotacion():
    #Genera un sonido de rotacion (dos tonos rapidos)
    sample_rate = 22050
    duracion = 0.1
    n_samples = int(sample_rate * duracion)
    
    # Primera mitad: tono bajo
    t1 = np.linspace(0, duracion/2, n_samples//2)
    buf1 = np.sin(2 * np.pi * 300 * t1)
    
    # Segunda mitad: tono alto
    t2 = np.linspace(0, duracion/2, n_samples//2)
    buf2 = np.sin(2 * np.pi * 500 * t2)
    
    # Combinar
    buf = np.concatenate([buf1, buf2])
    
    # Fade out
    fade_len = int(sample_rate * 0.02)
    fade = np.linspace(1, 0, fade_len)
    buf[-fade_len:] *= fade
    
    buf = (buf * 0.15 * 32767).astype(np.int16)
    buf = np.repeat(buf.reshape(len(buf), 1), 2, axis=1)
    
    return pygame.sndarray.make_sound(buf)

def generar_sonido_drop():
    #Genera un sonido descendente para el drop
    sample_rate = 22050
    duracion = 0.2
    n_samples = int(sample_rate * duracion)
    
    # Frecuencia que desciende de 800 Hz a 200 Hz
    t = np.linspace(0, duracion, n_samples)
    frecuencia = np.linspace(800, 200, n_samples)
    fase = 2 * np.pi * np.cumsum(frecuencia) / sample_rate
    
    buf = np.sin(fase)
    
    # Envelope para que suene mas natural
    envelope = np.exp(-3 * t / duracion)
    buf *= envelope
    
    buf = (buf * 0.25 * 32767).astype(np.int16)
    buf = np.repeat(buf.reshape(len(buf), 1), 2, axis=1)
    
    return pygame.sndarray.make_sound(buf)

def generar_sonido_linea():
    #Genera un sonido ascendente para linea completada
    sample_rate = 22050
    duracion = 0.3
    n_samples = int(sample_rate * duracion)
    
    # Frecuencia que asciende de 400 Hz a 800 Hz
    t = np.linspace(0, duracion, n_samples)
    frecuencia = np.linspace(400, 800, n_samples)
    fase = 2 * np.pi * np.cumsum(frecuencia) / sample_rate
    
    buf = np.sin(fase)
    
    # Envelope
    envelope = np.exp(-2 * t / duracion)
    buf *= envelope
    
    buf = (buf * 0.3 * 32767).astype(np.int16)
    buf = np.repeat(buf.reshape(len(buf), 1), 2, axis=1)
    
    return pygame.sndarray.make_sound(buf)

def generar_sonido_fijar():
    #Genera un sonido para cuando la pieza se fija
    return generar_tono(300, 0.08, 0.25)

def generar_sonido_gameover():
    #Genera un sonido triste para game over
    sample_rate = 22050
    duracion = 0.8
    n_samples = int(sample_rate * duracion)
    # Secuencia descendente de notas
    t = np.linspace(0, duracion, n_samples)
    frecuencias = [500, 400, 300, 200]  # Notas descendentes
    buf = np.zeros(n_samples)
    for i, freq in enumerate(frecuencias):
        inicio = int(i * n_samples / len(frecuencias))
        fin = int((i + 1) * n_samples / len(frecuencias))
        t_segmento = t[inicio:fin]
        buf[inicio:fin] = np.sin(2 * np.pi * freq * t_segmento)
    
    envelope = np.exp(-1.5 * t / duracion)
    buf *= envelope
    buf = (buf * 0.2 * 32767).astype(np.int16)
    buf = np.repeat(buf.reshape(len(buf), 1), 2, axis=1)
    
    return pygame.sndarray.make_sound(buf)

# Diccionario para guardar los sonidos generados
_cache_sonidos = {}

def obtener_sonido(tipo):
    """ Obtenemos un sonido del cache o lo genera si no existe.
    Param:
        tipo: Tipo de sonido ('mover', 'rotar', 'drop', 'linea', 'fijar', 'gameover')
    Retorna:
        pygame.Sound o None si el sonido esta deshabilitado """
    if not sonido_habilitado:
        return None
    
    if tipo not in _cache_sonidos:
        # Generar el sonido y guardarlo en cache
        if tipo == 'mover':
            _cache_sonidos[tipo] = generar_beep_corto(440)
        elif tipo == 'rotar':
            _cache_sonidos[tipo] = generar_beep_rotacion()
        elif tipo == 'drop':
            _cache_sonidos[tipo] = generar_sonido_drop()
        elif tipo == 'linea':
            _cache_sonidos[tipo] = generar_sonido_linea()
        elif tipo == 'fijar':
            _cache_sonidos[tipo] = generar_sonido_fijar()
        elif tipo == 'gameover':
            _cache_sonidos[tipo] = generar_sonido_gameover()
    
    return _cache_sonidos.get(tipo)

# Funciones para reproducir los sonidos
def sonido_mover():
    """Reproduce sonido de movimiento."""
    if sonido_habilitado and canal_movimiento:
        sonido = obtener_sonido('mover')
        if sonido and not canal_movimiento.get_busy():
            canal_movimiento.play(sonido)
def sonido_rotar():
    """Reproduce sonido de rotacion."""
    if sonido_habilitado and canal_rotacion:
        sonido = obtener_sonido('rotar')
        if sonido:
            canal_rotacion.play(sonido)
def sonido_drop():
    """Reproduce sonido de drop."""
    if sonido_habilitado and canal_drop:
        sonido = obtener_sonido('drop')
        if sonido:
            canal_drop.play(sonido)
def sonido_linea():
    """Reproduce sonido de linea completada."""
    if sonido_habilitado and canal_linea:
        sonido = obtener_sonido('linea')
        if sonido:
            canal_linea.play(sonido)
def sonido_fijar():
    #Reproduce sonido cuando se fija una pieza
    if sonido_habilitado:
        sonido = obtener_sonido('fijar')
        if sonido:
            pygame.mixer.Sound.play(sonido)
def sonido_gameover():
    #Reproduce sonido de game over
    if sonido_habilitado:
        sonido = obtener_sonido('gameover')
        if sonido:
            pygame.mixer.Sound.play(sonido)
def detener_todos():
    #Detiene todos los sonidos
    if sonido_habilitado:
        pygame.mixer.stop()

def iniciar_musica_fondo():
    #Inicia la musica de fondo desde un archivo MP3 o OGG.
    global musica_habilitada
    if sonido_habilitado and musica_habilitada:
        try:
            # Intentar cargar musica desde archivo
            # Busca en el mismo directorio que el script
            import os
            ruta_musica = os.path.join(os.path.dirname(__file__), 'TetrisNintendo.mp3')
            if not os.path.exists(ruta_musica):
                # Probar con .ogg
                ruta_musica = os.path.join(os.path.dirname(__file__), 'TetrisNintendo.ogg')
            if os.path.exists(ruta_musica):
                pygame.mixer.music.load(ruta_musica)
                pygame.mixer.music.set_volume(0.15)  # Volumen bajo (15%)
                pygame.mixer.music.play(loops=-1)  # Loop infinito
                print(f" Musica de fondo iniciada: {os.path.basename(ruta_musica)}")
            else:
                print(" No se encontro archivo de musica")
                print(" Coloca tu archivo de musica en el directorio del juego")
        except Exception as e:
            print(f" No se pudo iniciar musica: {e}")

def detener_musica_fondo():
    #Detiene la musica de fondo. 
    if sonido_habilitado:
        pygame.mixer.music.stop()

def toggle_musica():
    """Activa/desactiva la musica de fondo."""
    global musica_habilitada
    musica_habilitada = not musica_habilitada
    if musica_habilitada:
        iniciar_musica_fondo()
    else:
        detener_musica_fondo()
    return musica_habilitada


if __name__ == "__main__":    
    if inicializar_sonidos():
        print("\nProbando sonidos...")
        print("1. Sonido de movimiento")
        sonido_mover()
        pygame.time.wait(200)
        print("2. Sonido de rotacion")
        sonido_rotar()
        pygame.time.wait(300)
        print("3. Sonido de drop")
        sonido_drop()
        pygame.time.wait(400)
        print("4. Sonido de linea")
        sonido_linea()
        pygame.time.wait(500)
        print("5. Sonido de fijar")
        sonido_fijar()
        pygame.time.wait(300)
        print("6. Sonido de game over")
        sonido_gameover()
        pygame.time.wait(1000)        
        print("\n Prueba completada")
    else:
        print(" No se pudo inicializar el sonido")
    