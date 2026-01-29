# Tetris 3D - Proyecto final Info3
# Aca esta todo el juego, OpenGL, camara, inputs y demas
# Alfredo Acosta - Dic 2025
from OpenGL import GL      # OpenGL principal
from OpenGL import GLU     # Utilidades OpenGL (camara, etc.)
from OpenGL import GLUT    # Toolkit para ventanas

#Modulos personalizados para tener bien ordenado todo
import geometria           # Funciones para dibujar cubos, ejes, grilla
import iluminacion         # Sistema de luzes
import piezas              # Definicion de las 5 piezas de Tetris
import tablero             # Tablero 3D y deteccion de coliciones
import sonidos             # Sistema de efectos de sonido


import sys
# Tamano de la ventana en pixeles
ancho_pantalla = 1200
alto_pantalla = 1000
# Variables de la camara
camara_distancia = 100.0  
camara_angulo_h = 46.0   # horizontal
camara_angulo_v = 30.0   # vertical
# se calculan despues en actualizar_posicion_camara
ojox = 20.0
ojoy = 15.0
ojoz = 35.0

# Hacia donde mira (centro del tablero)
centro_x = 5.0   
centro_y = 10.0  
centro_z = 5.0

# Vector arriba
arriba_x = 0.0
arriba_y = 1.0   
arriba_z = 0.0
# Config de niveles de dificultad
NIVELES_DIFICULTAD = {
    'PRINCIPIANTE': {
        'ancho': 6,
        'alto': 12,
        'profundidad': 6,
        'piezas_permitidas': ['O', 'I', 'L'],  # Solo 3 piezas
        'nombre': 'Principiante',
        'velocidad': 1000   #Despacito  1 segundo
    },
    'MEDIO': {
        'ancho': 8,
        'alto': 16,
        'profundidad': 8,
        'piezas_permitidas': ['O', 'I', 'L', 'T'],  # 4 piezas
        'nombre': 'Medio',
        'velocidad': 600  #  0.6 segundos
    },
    'DIFICIL': {
        'ancho': 10,
        'alto': 20,
        'profundidad': 10,
        'piezas_permitidas': ['O', 'I', 'L', 'T', 'Z'],  # Todas las 5 piezas
        'nombre': 'Dificil',
        'velocidad': 300  # Mucho mas Rapido la caida de la pieza (0.3 segundos)
    }
}

# Estos parametros se va actualizar de acuerdo a lo que se elija en el juego
ANCHO_TABLERO = 10      # Ancho (eje X): 10 cubos
ALTO_TABLERO = 20       # Alto (eje Y): 20 cubos
PROFUNDIDAD_TABLERO = 10  # Profundidad (eje Z): 10 cubos
# Los estados que puede tener la aplicacion
ESTADO_MENU = 0
ESTADO_JUGANDO = 1
ESTADO_PAUSADO = 2
ESTADO_GAME_OVER = 3

# Estado actual del juego
estado_juego = ESTADO_MENU  # Comienza con el menu siempre
# Nivel de dificultad seleccionado
dificultad_seleccionada = 'MEDIO'  # Por defecto elegimos medio al empezar 
piezas_permitidas = ['O', 'I', 'L', 'T']  # Por defecto nivel medio
# Estado del juego (legacy - mantener compatibilidad)
juego_pausado = False   # no esta pausado
game_over = False       # no se perdio el video juego
# Tablero del juego
tablero_juego = None    # Se inicializa en inicializar()
# Pieza actual que esta cayendo
pieza_actual = None     # Se inicializa en inicializar()
# Pieza siguiente (preview)
pieza_siguiente = None  # Se inicializa en inicializar()

# Velocidad de caida (en milisegundos)
VELOCIDAD_CAIDA = 600  # Valor por defecto (nivel medio)
velocidad_actual = VELOCIDAD_CAIDA  # Velocidad dinamica (aumenta con nivel)
velocidad_base_nivel = VELOCIDAD_CAIDA  # Velocidad base del nivel seleccionado

# Sistema de puntaje
puntaje = 0             # Puntos totales
nivel = 1               # Nivel actual (1, 2, 3, ...)
lineas_totales = 0      # Lineas completadas en total
piezas_colocadas = 0    # Contador de piezas fijadas

# Modo automatico (IA)
modo_automatico = False # Si esta activado la IA juega sola
timer_ia_activo = False

def renderizar_texto_2d(x, y, texto, fuente=None):
    # Dibuja texto en 2D sobre la pantala
    if fuente is None:
        fuente = GLUT.GLUT_BITMAP_HELVETICA_18
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    GL.glOrtho(0, ancho_pantalla, alto_pantalla, 0, -1, 1)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    GL.glRasterPos2f(x, y)
    for char in texto:
        GLUT.glutBitmapCharacter(fuente, ord(char))
    
    # Restaurar
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)
    
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)


def renderizar_hud():
    """
    Renderiza el HUD con informacion del juego y muestra:
        - Puntaje actual
        - Nivel actual
        - Lineas completadas
        - Piezas colocadas """
    # Desactivar iluminacion para el HUD
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    # Color blanco brillante para el texto
    GL.glColor3f(1.0, 1.0, 1.0)
    
    # Posicion del HUD (esquina superior izquierda)
    x_base = 10
    y_base = 10
    
    # Titulo
    renderizar_texto_2d(x_base, y_base, "TETRIS 3D", GLUT.GLUT_BITMAP_HELVETICA_18)
    
    # Estadisticas (usar fuente mas pequena)
    renderizar_texto_2d(x_base, y_base + 30, f"PUNTAJE: {puntaje}", GLUT.GLUT_BITMAP_HELVETICA_12)
    renderizar_texto_2d(x_base, y_base + 50, f"NIVEL: {nivel}", GLUT.GLUT_BITMAP_HELVETICA_12)
    renderizar_texto_2d(x_base, y_base + 70, f"LINEAS: {lineas_totales}", GLUT.GLUT_BITMAP_HELVETICA_12)
    renderizar_texto_2d(x_base, y_base + 90, f"PIEZAS: {piezas_colocadas}", GLUT.GLUT_BITMAP_HELVETICA_12)
    
    # Modo automatico
    if modo_automatico:
        GL.glColor3f(0.0, 1.0, 0.0)  # Verde
        renderizar_texto_2d(x_base, y_base + 110, "IA: ON", GLUT.GLUT_BITMAP_HELVETICA_12)
        GL.glColor3f(1.0, 1.0, 1.0)
    
    # Preview label
    renderizar_texto_2d(x_base, y_base + 140, "SIGUIENTE:", GLUT.GLUT_BITMAP_HELVETICA_12)
    
    # Mensaje de pausa (centrado)
    if juego_pausado:
        GL.glColor3f(1.0, 1.0, 0.0)  # Amarillo
        renderizar_texto_2d(500, 400, "PAUSA", GLUT.GLUT_BITMAP_TIMES_ROMAN_24)
    
    # Mensaje de Game Over (centrado)
    if game_over:
        GL.glColor3f(1.0, 0.0, 0.0)  # Rojo
        renderizar_texto_2d(450, 400, "GAME OVER!", GLUT.GLUT_BITMAP_TIMES_ROMAN_24)
        GL.glColor3f(1.0, 1.0, 1.0)
        renderizar_texto_2d(450, 440, "Presiona R", GLUT.GLUT_BITMAP_HELVETICA_18)
    
    # Reactivar estados
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

# Definicion de botones del menu (x, y, ancho, alto en pixeles)
# Sistema de coordenadas:   X va de izquierda (0) a derecha (1200)
#                           Y va de ARRIBA (0) a ABAJO (1000)  <- coordenadas GLUT normales
# Centrados horizontalmente: x = (1200 - 600) / 2 = 300
BOTONES_NIVELES = {
    'PRINCIPIANTE': {'x': 300, 'y': 100, 'ancho': 500, 'alto': 70},
    'MEDIO':        {'x': 300, 'y': 180, 'ancho': 500, 'alto': 70},
    'DIFICIL':      {'x': 300, 'y': 260, 'ancho': 500, 'alto': 70}
}

# Botones de accion
BOTON_EMPEZAR = {'x': 400, 'y': 400, 'ancho': 180, 'alto': 70}
BOTON_SALIR = {'x': 620, 'y': 400, 'ancho': 180, 'alto': 70}

# Variables de estado del menu
boton_hover = None  # Cual boton esta siendo hover por el mouse
nivel_seleccionado = None  # Nivel seleccionado (PRINCIPIANTE, MEDIO, DIFICIL)


def renderizar_rectangulo_2d(x, y, ancho, alto, color):
    """ Renderiza un rectangulo 2D con el color especificado.
        x, y: Esquina SUPERIOR IZQUIERDA en pixeles (coordenadas GLUT)
        ancho, alto: Dimensiones del rectangulo
        color: Tupla RGB (r, g, b) """
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    # Proyeccion ortográfica: Y va de 0 (arriba) a alto_pantalla (abajo)
    GL.glOrtho(0, ancho_pantalla, alto_pantalla, 0, -1, 1)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    
    GL.glColor3f(*color)
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex2f(x, y)
    GL.glVertex2f(x + ancho, y)
    GL.glVertex2f(x + ancho, y + alto)
    GL.glVertex2f(x, y + alto)
    GL.glEnd()
    
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_boton(x, y, ancho, alto, texto, es_hover=False):
    """ Renderiza el boton del menu.
        es_hover: Si el mouse esta encima de algun boton """
    # Color del boton
    if es_hover:
        color_fondo = (0.3, 0.5, 0.8)  # Azul claro cuando hover
        color_borde = (0.5, 0.7, 1.0)  # Azul mas claro
    else:
        color_fondo = (0.2, 0.3, 0.5)  # Azul oscuro
        color_borde = (0.3, 0.4, 0.6)  # Azul medio
    
    # Dibujar fondo del boton
    renderizar_rectangulo_2d(x, y, ancho, alto, color_fondo)
    
    # Dibujar borde del boton (4 lineas)
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    GL.glOrtho(0, ancho_pantalla, 0, alto_pantalla, -1, 1)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    
    GL.glColor3f(*color_borde)
    GL.glLineWidth(3.0)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2f(x, y)
    GL.glVertex2f(x + ancho, y)
    GL.glVertex2f(x + ancho, y + alto)
    GL.glVertex2f(x, y + alto)
    GL.glEnd()
    GL.glLineWidth(1.0)
    
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    # Dibujar texto centrado
    GL.glColor3f(1.0, 1.0, 1.0)  # Blanco
    texto_x = x + ancho // 2 - len(texto) * 6  # Centrar aproximadamente
    texto_y = y + alto // 2 - 10
    renderizar_texto_2d(texto_x, texto_y, texto, GLUT.GLUT_BITMAP_HELVETICA_18)
    
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_menu():
    global nivel_seleccionado
    # Fondo oscuro
    GL.glClearColor(0.1, 0.1, 0.15, 1.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    # Obtener dimensiones de la ventana
    ancho_ventana = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
    centro_x = ancho_ventana // 2
    
    # Recalcular posiciones de botones centrados
    ancho_boton_nivel = 500
    x_boton_nivel = (ancho_ventana - ancho_boton_nivel) // 2
    
    ancho_boton_accion = 180
    espacio_entre_botones = 20
    ancho_total_botones = ancho_boton_accion * 2 + espacio_entre_botones
    x_boton_empezar = (ancho_ventana - ancho_total_botones) // 2
    x_boton_salir = x_boton_empezar + ancho_boton_accion + espacio_entre_botones
    
    # titulo centrado
    GL.glColor3f(0.3, 0.9, 1.0)
    titulo = "TETRIS 3D"
    fuente_titulo = GLUT.GLUT_BITMAP_TIMES_ROMAN_24
    #glutBitmapWidth calcula el ancho en pixeles de cada caracter, usamos para centrar todos los textos
    ancho_titulo = sum(GLUT.glutBitmapWidth(fuente_titulo, ord(c)) for c in titulo)
    titulo_x = centro_x - ancho_titulo // 2
    renderizar_texto_2d(titulo_x, 30, titulo, fuente_titulo)
    
    # subtitulo
    GL.glColor3f(0.7, 0.7, 0.8)
    subtitulo = "Selecciona nivel de dificultad"
    fuente_sub = GLUT.GLUT_BITMAP_HELVETICA_18
    ancho_sub = sum(GLUT.glutBitmapWidth(fuente_sub, ord(c)) for c in subtitulo)
    subtitulo_x = centro_x - ancho_sub // 2
    renderizar_texto_2d(subtitulo_x, 60, subtitulo, fuente_sub)
    # BOTONES DE NIVELES
    for i, (nombre, config) in enumerate(BOTONES_NIVELES.items()):
        x = x_boton_nivel  # Usar posicion centrada
        y = config['y']
        ancho = ancho_boton_nivel  # Usar ancho calculado
        alto = config['alto']
        
        es_hover = (boton_hover == nombre)
        es_seleccionado = (nivel_seleccionado == nombre)
        nivel_config = NIVELES_DIFICULTAD[nombre]
        
        # Dibujar el rectangulo del boton
        if es_seleccionado:
            color = (0.2, 0.7, 0.3)  # Verde
        elif es_hover:
            color = (0.25, 0.45, 0.75)  # Azul claro
        else:
            color = (0.15, 0.25, 0.45)  # Azul oscuro
        
        renderizar_rectangulo_2d(x, y, ancho, alto, color)
        
        # Borde del boton
        GL.glColor3f(0.5, 0.6, 0.7)
        GL.glLineWidth(2.0)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(x, y)
        GL.glVertex2f(x + ancho, y)
        GL.glVertex2f(x + ancho, y + alto)
        GL.glVertex2f(x, y + alto)
        GL.glEnd()
        GL.glLineWidth(1.0)
        
        # Texto del nivel
        GL.glColor3f(1.0, 1.0, 1.0)
        texto_y = y + 25
        texto_nivel = f"[{i+1}] {nivel_config['nombre']}"
        fuente_nivel = GLUT.GLUT_BITMAP_HELVETICA_18
        ancho_texto_nivel = sum(GLUT.glutBitmapWidth(fuente_nivel, ord(c)) for c in texto_nivel)
        renderizar_texto_2d(x + (ancho - ancho_texto_nivel) // 2, texto_y, texto_nivel, fuente_nivel)
        
        # Informacion del tablero
        GL.glColor3f(0.7, 0.8, 0.9)
        dim_texto = f"{nivel_config['ancho']}x{nivel_config['alto']}x{nivel_config['profundidad']}"
        texto_info = f"Tablero: {dim_texto} - {len(nivel_config['piezas_permitidas'])} tipos de piezas"
        fuente_info = GLUT.GLUT_BITMAP_HELVETICA_12
        ancho_texto_info = sum(GLUT.glutBitmapWidth(fuente_info, ord(c)) for c in texto_info)
        renderizar_texto_2d(x + (ancho - ancho_texto_info) // 2, texto_y + 22, texto_info, fuente_info)
        
        # Checkmark si seleccionado
        if es_seleccionado:
            GL.glColor3f(1.0, 1.0, 1.0)
            renderizar_texto_2d(x + ancho - 30, texto_y, "", GLUT.GLUT_BITMAP_TIMES_ROMAN_24)
    
    # BOTON EMPEZAR
    x = x_boton_empezar  # Usar posicion centrada
    y = BOTON_EMPEZAR['y']
    ancho = ancho_boton_accion  # Usar ancho calculado
    alto = BOTON_EMPEZAR['alto']
    
    es_hover_empezar = (boton_hover == 'EMPEZAR')
    puede_empezar = (nivel_seleccionado is not None)
    
    if not puede_empezar:
        color = (0.2, 0.2, 0.25)
    elif es_hover_empezar:
        color = (0.3, 0.8, 0.3)
    else:
        color = (0.2, 0.6, 0.2)
    
    renderizar_rectangulo_2d(x, y, ancho, alto, color)
    
    # Borde
    GL.glColor3f(0.4, 0.7, 0.4) if puede_empezar else GL.glColor3f(0.3, 0.3, 0.3)
    GL.glLineWidth(2.0)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2f(x, y)
    GL.glVertex2f(x + ancho, y)
    GL.glVertex2f(x + ancho, y + alto)
    GL.glVertex2f(x, y + alto)
    GL.glEnd()
    GL.glLineWidth(1.0)
    
    # Texto
    GL.glColor3f(1.0, 1.0, 1.0) if puede_empezar else GL.glColor3f(0.5, 0.5, 0.5)
    texto_empezar = "EMPEZAR"
    fuente_empezar = GLUT.GLUT_BITMAP_HELVETICA_18
    ancho_texto_empezar = sum(GLUT.glutBitmapWidth(fuente_empezar, ord(c)) for c in texto_empezar)
    renderizar_texto_2d(x + (ancho - ancho_texto_empezar) // 2, y + 28, texto_empezar, fuente_empezar)
    
    # BOTON SALIR
    x = x_boton_salir  # Usar posicion centrada
    y = BOTON_SALIR['y']
    ancho = ancho_boton_accion  # Usar ancho calculado
    alto = BOTON_SALIR['alto']
    
    es_hover_salir = (boton_hover == 'SALIR')
    
    color = (0.9, 0.2, 0.2) if es_hover_salir else (0.6, 0.15, 0.15)
    renderizar_rectangulo_2d(x, y, ancho, alto, color)
    
    # Borde
    GL.glColor3f(0.9, 0.4, 0.4)
    GL.glLineWidth(2.0)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex2f(x, y)
    GL.glVertex2f(x + ancho, y)
    GL.glVertex2f(x + ancho, y + alto)
    GL.glVertex2f(x, y + alto)
    GL.glEnd()
    GL.glLineWidth(1.0)
    
    # Texto
    GL.glColor3f(1.0, 1.0, 1.0)
    texto_salir = "SALIR"
    fuente_salir = GLUT.GLUT_BITMAP_HELVETICA_18
    ancho_texto_salir = sum(GLUT.glutBitmapWidth(fuente_salir, ord(c)) for c in texto_salir)
    renderizar_texto_2d(x + (ancho - ancho_texto_salir) // 2, y + 28, texto_salir, fuente_salir)
    
    # Mensaje inferior
    if nivel_seleccionado:
        GL.glColor3f(0.3, 1.0, 0.4)
        texto = f"Nivel: {NIVELES_DIFICULTAD[nivel_seleccionado]['nombre']}"
        fuente = GLUT.GLUT_BITMAP_HELVETICA_18
        ancho_texto = sum(GLUT.glutBitmapWidth(fuente, ord(c)) for c in texto)
        texto_x = centro_x - ancho_texto // 2
        renderizar_texto_2d(texto_x, 520, texto, fuente)
    else:
        GL.glColor3f(0.6, 0.6, 0.7)
        texto = "Selecciona un nivel para continuar"
        fuente = GLUT.GLUT_BITMAP_HELVETICA_12
        ancho_texto = sum(GLUT.glutBitmapWidth(fuente, ord(c)) for c in texto)
        texto_x = centro_x - ancho_texto // 2
        renderizar_texto_2d(texto_x, 520, texto, fuente)
    
    # Instrucciones
    GL.glColor3f(0.5, 0.5, 0.6)
    instruccion = "Usa mouse o teclado: 1, 2, 3 para seleccionar + 'e' para Empezar"
    fuente = GLUT.GLUT_BITMAP_HELVETICA_12
    ancho_instruccion = sum(GLUT.glutBitmapWidth(fuente, ord(c)) for c in instruccion)
    instruccion_x = centro_x - ancho_instruccion // 2
    renderizar_texto_2d(instruccion_x, 560, instruccion, fuente)
    
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_game_over():
    #Renderiza la pantalla de Game Over cundo se pierde el juego
    global puntaje, nivel, lineas_totales, piezas_colocadas, tablero_juego
    
    ancho_pantalla = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
    alto_pantalla = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
    
    # Fondo semi-transparente
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    GL.glOrtho(0, ancho_pantalla, 0, alto_pantalla, -1, 1)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    
    # Fondo oscuro semi-transparente
    GL.glColor4f(0.0, 0.0, 0.0, 0.7)
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex2f(0, 0)
    GL.glVertex2f(ancho_pantalla, 0)
    GL.glVertex2f(ancho_pantalla, alto_pantalla)
    GL.glVertex2f(0, alto_pantalla)
    GL.glEnd()
    
    # Titulo GAME OVER
    GL.glColor3f(1.0, 0.2, 0.2)
    titulo_x = ancho_pantalla // 2 - 60
    titulo_y = alto_pantalla - 100
    renderizar_texto_2d(titulo_x, titulo_y, "GAME OVER", GLUT.GLUT_BITMAP_TIMES_ROMAN_24)
    
    # Estadisticas
    GL.glColor3f(1.0, 1.0, 1.0)
    inicio_y = alto_pantalla - 180
    espacio = 30
    inicio_x = ancho_pantalla // 2 - 100
    
    renderizar_texto_2d(inicio_x, inicio_y, f"Puntaje final: {puntaje}", GLUT.GLUT_BITMAP_HELVETICA_18)
    renderizar_texto_2d(inicio_x, inicio_y - espacio, f"Nivel alcanzado: {nivel}", GLUT.GLUT_BITMAP_HELVETICA_18)
    renderizar_texto_2d(inicio_x, inicio_y - espacio*2, f"Lineas completadas: {lineas_totales}", GLUT.GLUT_BITMAP_HELVETICA_18)
    renderizar_texto_2d(inicio_x, inicio_y - espacio*3, f"Piezas colocadas: {piezas_colocadas}", GLUT.GLUT_BITMAP_HELVETICA_18)
    
    if tablero_juego is not None:
        cubos = tablero_juego.contar_cubos_fijos()
        renderizar_texto_2d(inicio_x, inicio_y - espacio*4, f"Cubos en tablero: {cubos}", GLUT.GLUT_BITMAP_HELVETICA_18)
    
    # Instrucciones
    GL.glColor3f(0.7, 0.7, 0.7)
    renderizar_texto_2d(ancho_pantalla // 2 - 120, 100, "Presiona R para reiniciar", GLUT.GLUT_BITMAP_HELVETICA_18)
    renderizar_texto_2d(ancho_pantalla // 2 - 100, 70, "Presiona ESC para salir", GLUT.GLUT_BITMAP_HELVETICA_18)
    
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    GL.glDisable(GL.GL_BLEND)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_controles_miniguia():
    #Renderiza una mini guia de controles en la esquina inferior izquierda. 
    # Desactivar iluminacion y depth test
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    # Color gris claro para que no moleste
    GL.glColor3f(0.7, 0.7, 0.8)
    # Posicion base (parte inferior izquierda)
    x_base = 10
    y_base = alto_pantalla - 300  # Desde abajo
    # Fuente grande
    fuente = GLUT.GLUT_BITMAP_HELVETICA_12
    #ms grande para el titulo
    fuente_titulo = GLUT.GLUT_BITMAP_HELVETICA_18 #mas grande
    # Titulo de la seccion
    GL.glColor3f(0.9, 0.9, 1.0)  # Un poco mas brillante
    renderizar_texto_2d(x_base, y_base, "CONTROLES: ", fuente_titulo)
    # Controles basicos (color AMARILLO)
    GL.glColor3f(0.9, 0.9, 0.0)
    renderizar_texto_2d(x_base, y_base + 20, "FLECHAS: MOVER PIEZA", fuente)
    renderizar_texto_2d(x_base, y_base + 40, "Q/W/E: ROTA EJE X", fuente)
    renderizar_texto_2d(x_base, y_base + 60, "A/S/D: ROTA EJE Y", fuente)
    renderizar_texto_2d(x_base, y_base + 80, "Z/X/C: ROTA EJE Z", fuente)
    renderizar_texto_2d(x_base, y_base + 100, "ESPACIO: DROP", fuente)
    renderizar_texto_2d(x_base, y_base + 120, "P: PAUSA  R: RESET", fuente)
    # Nota sobre controles relativos
    #GL.glColor3f(0.5, 0.5, 0.6)
    #colocar los botones que usa para la camaras 2,4,6,8,5,+,-
    GL.glColor3f(0.9, 0.9, 1.0)  # Un poco mas brillante
    renderizar_texto_2d(x_base, y_base + 160, "CAMARAS: NumPad", fuente_titulo)
    GL.glColor3f(0.9, 0.9, 0.0)  # Amarillo
    renderizar_texto_2d(x_base, y_base + 180, "ROTAR: 2,4,6,8", fuente)
    renderizar_texto_2d(x_base, y_base + 200, "CENTRAR: 5", fuente)
    renderizar_texto_2d(x_base, y_base + 220, "ACERCAR/ALEJAR: +,-", fuente)
    # Reactivar estados
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_preview_siguiente():
    """ Renderiza la preview de la siguiente pieza en 2D (overlay fijo en pantalla).
        No rota con la cámara, siempre visible en la esquina superior izquierda. """
    if pieza_siguiente is None:
        return
    
    # Desactivar iluminacion y depth test para dibujar en 2D
    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    
    # Configurar proyeccion ortográfica 2D
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    GL.glOrtho(0, ancho_pantalla, alto_pantalla, 0, -1, 1)
    
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    
    # Posicion de la preview en pixeles (debajo de "SIGUIENTE:")
    preview_x_pantalla = 50  # A la izquierda
    preview_y_pantalla = 180  # Debajo del texto "SIGUIENTE:"
    tamano_cubo = 25  # Tamaño de cada cubo en pixeles
    
    # Dibujar cada cubo de la pieza siguiente
    for dx, dy, dz in pieza_siguiente.geometria:
        # Calcular posicion en pantalla (solo usamos dx y dy, ignoramos dz)
        x = preview_x_pantalla + dx * tamano_cubo
        y = preview_y_pantalla + dy * tamano_cubo
        
        # Dibujar cubo relleno
        GL.glColor3f(*pieza_siguiente.color)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(x, y)
        GL.glVertex2f(x + tamano_cubo, y)
        GL.glVertex2f(x + tamano_cubo, y + tamano_cubo)
        GL.glVertex2f(x, y + tamano_cubo)
        GL.glEnd()
        
        # Dibujar borde del cubo
        GL.glColor3f(0.2, 0.2, 0.2)
        GL.glLineWidth(1.5)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(x, y)
        GL.glVertex2f(x + tamano_cubo, y)
        GL.glVertex2f(x + tamano_cubo, y + tamano_cubo)
        GL.glVertex2f(x, y + tamano_cubo)
        GL.glEnd()
        GL.glLineWidth(1.0)
    
    # Restaurar matrices
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    # Reactivar estados
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

def renderizar_pieza_fantasma():
    """ Renderiza una silueta semi-transparente de donde caera la pieza actual. """
    if pieza_actual is None or game_over or juego_pausado:
        return
    # Hacer una copia temporal de la pieza
    import copy
    pieza_temp = copy.deepcopy(pieza_actual)
    
    # Bajar la pieza temporal hasta que colisione
    while tablero_juego.puede_colocar_pieza(pieza_temp):
        pieza_temp.mover(0, -1, 0)
    
    # Retroceder un paso (ultima posicion valida)
    pieza_temp.mover(0, 1, 0)
    # Dibujar la pieza fantasma semi-transparente
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    for dx, dy, dz in pieza_temp.geometria:
        x = pieza_temp.x + dx
        y = pieza_temp.y + dy
        z = pieza_temp.z + dz
        # Usar el color de la pieza pero con alpha bajo (semi-transparente)
        color_fantasma = (pieza_temp.color[0], pieza_temp.color[1], pieza_temp.color[2], 0.3)
        # Dibujar cubo semi-transparente sin bordes
        GL.glColor4f(*color_fantasma)
        GL.glPushMatrix() #guarda la matriz actual
        GL.glTranslatef(x, y, z)#aplicamos las transformacion
        # Dibujar solo las caras, sin bordes
        GL.glBegin(GL.GL_QUADS)
        for cara in geometria.CUBO_CARAS:
            for vertice_idx in cara:
                GL.glVertex3fv(geometria.CUBO_VERTICES[vertice_idx])
        GL.glEnd()
        GL.glPopMatrix()#restaura la matriz anterior

    GL.glDisable(GL.GL_BLEND)

def actualizar_posicion_camara():
    """ Esta funcion calcula y actualiza la posicion de la camara (ojox, ojoy, ojoz) basandose en
        los angulos horizontal y vertical, y la distancia al centro.
        Usa coordenadas esfericas para facilitar la rotacion orbital.   
        Formulas:
            x = centro_x + distancia * cos(angulo_v) * sin(angulo_h)
            y = centro_y + distancia * sin(angulo_v)
            z = centro_z + distancia * cos(angulo_v) * cos(angulo_h) """
    global ojox, ojoy, ojoz
    import math
    # Convertir angulos de grados a radianes
    ang_h_rad = math.radians(camara_angulo_h)
    ang_v_rad = math.radians(camara_angulo_v)
    # Calcula la posicion en coordenadas esfericas
    ojox = centro_x + camara_distancia * math.cos(ang_v_rad) * math.sin(ang_h_rad)
    ojoy = centro_y + camara_distancia * math.sin(ang_v_rad)
    ojoz = centro_z + camara_distancia * math.cos(ang_v_rad) * math.cos(ang_h_rad)
    print(f"Camara posicion actual: ({ojox:.2f}, {ojoy:.2f}, {ojoz:.2f})")

def calcular_movimiento_relativo_camara(tecla):
    """ Calcula el movimiento (dx, dz) segun la tecla presionada y el angulo de la camara.
        Los controles se adaptan a la orientacion de la camara:
        - Flecha arriba: mueve adelante desde la perspectiva de la camara
        - Flecha abajo: mueve atras desde la perspectiva de la camara
        - Flecha derecha: mueve a la derecha desde la perspectiva de la camara
        - Flecha izquierda: mueve a la izquierda desde la perspectiva de la camara
        Param:
            tecla: Codigo de tecla especial de GLUT (GLUT.GLUT_KEY_UP, GLUT.GLUT_KEY_DOWN, etc.)
        Retorna:
            Tupla (dx, dz) con el desplazamiento a aplicar """
    import math
    # Convertir angulo horizontal de la camara a radianes
    ang_h_rad = math.radians(camara_angulo_h)
    
    dx = 0
    dz = 0
    
    # Calcular vectores direccionales segun la orientacion de la camara
    # Vector adelante (hacia donde mira la camara, proyectado en el plano XZ)
    adelante_x = -math.sin(ang_h_rad)
    adelante_z = -math.cos(ang_h_rad)
    
    # Vector "derecha" (perpendicular a adelante)
    derecha_x = math.cos(ang_h_rad)
    derecha_z = -math.sin(ang_h_rad)
    
    # Mapear teclas a movimientos
    if tecla == GLUT.GLUT_KEY_UP:
        # Flecha arriba: mover adelante (hacia donde mira la camara)
        # Elegir el eje con mayor componente para evitar diagonales
        if abs(adelante_x) > abs(adelante_z):
            dx = 1 if adelante_x > 0 else -1
            dz = 0
        else:
            dx = 0
            dz = 1 if adelante_z > 0 else -1
    
    elif tecla == GLUT.GLUT_KEY_DOWN:
        # Flecha abajo: mover atras (opuesto a donde mira la camara)
        if abs(adelante_x) > abs(adelante_z):
            dx = -1 if adelante_x > 0 else 1
            dz = 0
        else:
            dx = 0
            dz = -1 if adelante_z > 0 else 1
    
    elif tecla == GLUT.GLUT_KEY_RIGHT:
        # Flecha derecha: mover a la derecha de la camara
        # Elegir el eje con mayor componente
        if abs(derecha_x) > abs(derecha_z):
            dx = 1 if derecha_x > 0 else -1
            dz = 0
        else:
            dx = 0
            dz = 1 if derecha_z > 0 else -1
    
    elif tecla == GLUT.GLUT_KEY_LEFT:
        # Flecha izquierda: mover a la izquierda de la camara
        if abs(derecha_x) > abs(derecha_z):
            dx = -1 if derecha_x > 0 else 1
            dz = 0
        else:
            dx = 0
            dz = -1 if derecha_z > 0 else 1
    
    return (dx, dz)

def volver_menu_callback(valor):
    #Callback para volver al menu principal después de game over.
    global estado_juego, game_over, juego_pausado, puntaje, nivel, lineas_totales, piezas_colocadas
    global pieza_actual, pieza_siguiente, tablero_juego
    
    print("Regresando al menu principal...")
    estado_juego = ESTADO_MENU
    game_over = False
    juego_pausado = False
    
    # Limpiaar el tablero
    if tablero_juego is not None:
        tablero_juego.limpiar()
    
    # Resetear estadisticas
    puntaje = 0
    nivel = 1
    lineas_totales = 0
    piezas_colocadas = 0
    pieza_actual = None
    pieza_siguiente = None
    
    GLUT.glutPostRedisplay()


# funcion que dibuja todo en la pantalla
def display():
    # Funcion que dibuja todo, se llama automaticamente muchas veces por segundo
    
    global estado_juego
    
    if estado_juego == ESTADO_MENU:
        renderizar_menu()
        GLUT.glutSwapBuffers()
        return 
    
    # Limpiar pantalla
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity()
    
    # Configurar camara
    actualizar_posicion_camara()
    GLU.gluLookAt(
        ojox, ojoy, ojoz,           
        centro_x, centro_y, centro_z,  
        arriba_x, arriba_y, arriba_z
    )
    
    # Actualizamos las posiciones de las luces se Debe hacer siempre DESPUES de gluLookAt
    iluminacion.actualizar_luces()
    geometria.dibujar_ejes(longitud=12)
    
    # Dibujamos los limites del tablero del juego 
    geometria.dibujar_grilla(ANCHO_TABLERO, ALTO_TABLERO, PROFUNDIDAD_TABLERO)
    
    # Dibujar todos los cubos que ya estan fijados en el tablero
    if tablero_juego is not None:
        cubos_fijos = tablero_juego.obtener_cubos_fijos()
        for x, y, z, color in cubos_fijos:
            geometria.dibujar_cubo(x, y, z, color)
    
    # Primero dibujamos la pieza fantasma
    if pieza_actual is not None and not game_over:
        renderizar_pieza_fantasma()
    
    # Luego dibujamos la pieza que esta cayendo actualmente
    if pieza_actual is not None and not game_over:
        posiciones = pieza_actual.obtener_posiciones_absolutas()
        for x, y, z in posiciones:
            geometria.dibujar_cubo(x, y, z, pieza_actual.color)
    
    # Renderizamos HUD con estadisticas
    renderizar_hud()
    
    # Renderizamos preview de siguiente pieza
    renderizar_preview_siguiente()
    
    # Renderizamos mini guia de controles
    renderizar_controles_miniguia()
    
    # Si es Game Over, mostrar pantalla de estadisticas
    if game_over:
        renderizar_game_over()
    
    # glutSwapBuffers: Muestra en pantalla lo que acabamos de dibujar
    # OpenGL usa "doble buffer": dibujamos en uno invisible y lo mostramos
    # cuando esta listo (evita parpadeos)
    GLUT.glutSwapBuffers()

def buttons(key, x, y):
    """ Maneja todos los eventos del teclado. Esta funcion se llama automaticamente 
        cuando el usuario presiona una tecla.
        Parametros:
            key: La tecla presionada (como bytes, ej: b'a', b'\x1b')
            x, y: Posicion del mouse cuando se presiono la tecla (no la usamos) """
    
    global juego_pausado, game_over, pieza_actual, tablero_juego, pieza_siguiente
    global puntaje, nivel, lineas_totales, piezas_colocadas, velocidad_actual
    global camara_distancia, camara_angulo_h, camara_angulo_v
    global estado_juego, nivel_seleccionado
    
    if estado_juego == ESTADO_MENU:
        if isinstance(key, bytes):
            tecla = key.decode('utf-8')
            if ord(tecla) == 27:  # ESC
                print("\n" + "=" * 70)
                print("SALIENDO DEL JUEGO...")
                print("=" * 70)
                GLUT.glutLeaveMainLoop()
            elif tecla == '1':
                nivel_seleccionado = 'PRINCIPIANTE'
                print(f"Nivel seleccionado: {NIVELES_DIFICULTAD['PRINCIPIANTE']['nombre']}")
                GLUT.glutPostRedisplay()
            elif tecla == '2':
                nivel_seleccionado = 'MEDIO'
                print(f"Nivel seleccionado: {NIVELES_DIFICULTAD['MEDIO']['nombre']}")
                GLUT.glutPostRedisplay()
            elif tecla == '3':
                nivel_seleccionado = 'DIFICIL'
                print(f"Nivel seleccionado: {NIVELES_DIFICULTAD['DIFICIL']['nombre']}")
                GLUT.glutPostRedisplay()
            elif tecla.lower() == 'e':  # Enter/Empezar
                if nivel_seleccionado:
                    iniciar_juego_con_dificultad(nivel_seleccionado)
                else:
                    print("Primero selecciona un nivel (1, 2 o 3)")
        return
    
    # No hacer nada si el juego esta pausado o en game over
    if juego_pausado or game_over:
        # Excepto ESC, P, R y CONTROLES DE CAMARA que siempre funcionan
        if isinstance(key, bytes):
            tecla = key.decode('utf-8')
            if ord(tecla) == 27:  # ESC
                print("\n" + "=" * 70)
                print("VOLVIENDO AL MENu PRINCIPAL...")
                print("=" * 70)
                # Volver al menu en lugar de salir
                estado_juego = ESTADO_MENU
                game_over = False
                juego_pausado = False
                GLUT.glutPostRedisplay()
                return
            elif tecla == 'p' or tecla == 'P':
                juego_pausado = not juego_pausado
                estado = "PAUSADO" if juego_pausado else "REANUDADO"
                print(f"Juego {estado}")
                GLUT.glutPostRedisplay()
            elif tecla == 'r' or tecla == 'R':
                print("\n" + "=" * 70)
                print("REINICIANDO JUEGO...")
                print("=" * 70)
                # Resetear tablero
                tablero_juego.limpiar()
                # Resetear puntaje y estadisticas
                puntaje = 0
                nivel = 1
                lineas_totales = 0
                piezas_colocadas = 0
                velocidad_actual = VELOCIDAD_CAIDA
                
                # Crear nueva pieza y siguiente (con piezas permitidas del nivel)
                pieza_actual = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas)
                pieza_siguiente = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas)
                game_over = False
                juego_pausado = False  # Tambien despausar si estaba pausado
                
                print(" Juego reiniciado")
                print("=" * 70 + "\n")
                GLUT.glutPostRedisplay()

            # CONTROLES DE CAMARA (funcionan en pausa y Game Over)
            elif tecla == '4':
                camara_angulo_h -= 15
                if camara_angulo_h < 0:
                    camara_angulo_h += 360
                print(f" Camara rotada izquierda (angulo: {camara_angulo_h:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '6':
                camara_angulo_h += 15
                if camara_angulo_h >= 360:
                    camara_angulo_h -= 360
                print(f" Camara rotada derecha (angulo: {camara_angulo_h:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '8':
                camara_angulo_v += 10
                if camara_angulo_v > 85:
                    camara_angulo_v = 85
                print(f" Camara inclinada arriba (angulo: {camara_angulo_v:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '2':
                camara_angulo_v -= 10
                if camara_angulo_v < -10:
                    camara_angulo_v = -10
                print(f" Camara inclinada abajo (angulo: {camara_angulo_v:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '+':
                camara_distancia -= 3
                if camara_distancia < 15:
                    camara_distancia = 15
                print(f" Camara acercada (distancia: {camara_distancia:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '-':
                camara_distancia += 3
                if camara_distancia > 80:
                    camara_distancia = 80
                print(f" Camara alejada (distancia: {camara_distancia:.0f})")
                GLUT.glutPostRedisplay()
            elif tecla == '5':
                camara_distancia = 40.0
                camara_angulo_h = 45.0
                camara_angulo_v = 30.0
                print(" Camara reseteada a posicion inicial")
                GLUT.glutPostRedisplay()
        return
    
    # Convertir la tecla de bytes a string para facilitar comparacion
    # Ejemplo: b'a' -> 'a'
    tecla = key.decode('utf-8') if isinstance(key, bytes) else key
    
    # Teecla: ESC para salir del juego
    if ord(tecla) == 27:  # 27 es el codigo ASCII de ESC
        print("\n" + "=" * 70)
        print("SALIENDO DEL JUEGO...")
        print("=" * 70)
        GLUT.glutLeaveMainLoop()  # Terminar el programa
    
    # Teecla: P (pausar/despausar)
    elif tecla == 'p' or tecla == 'P':
        juego_pausado = not juego_pausado  # Invertir estado
        estado = "PAUSADO" if juego_pausado else "REANUDADO"
        print(f"Juego {estado}")
    
    # Teecla: M modo IA (automatico) on/off
    elif tecla == 'm' or tecla == 'M':
        global modo_automatico, timer_ia_activo
        modo_automatico = not modo_automatico
        estado = "ACTIVADO" if modo_automatico else "DESACTIVADO"
        print(f"Modo Automatico (IA) {estado}")
        
        # Si se activa, iniciar el timer de IA
        if modo_automatico and not timer_ia_activo:
            GLUT.glutTimerFunc(800, timer_ia, 0)
    
    # Teecla: R  para reiniciar
    elif tecla == 'r' or tecla == 'R':
        print("\n" + "=" * 70)
        print("REINICIANDO JUEGO...")
        print("=" * 70)
        
        # Resetear tablero
        tablero_juego.limpiar()
        
        # Resetear puntaje y estadisticas
        puntaje = 0
        nivel = 1
        lineas_totales = 0
        piezas_colocadas = 0
        velocidad_actual = VELOCIDAD_CAIDA
    
    # Tecla: O para activar/desactivar musica
    elif tecla == 'o' or tecla == 'O':
        estado = sonidos.toggle_musica()
        print(f" Musica: {'ON' if estado else 'OFF'}")
        
        # Crear nueva pieza y siguiente (con piezas permitidas)
        pieza_actual = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas)
        pieza_siguiente = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas)
        game_over = False
        
        print(" Juego reiniciado")
        print("=" * 70 + "\n")
    
    # Teclas para las camaras 2,4,5,6,8,+,-
    # Teecla 2: Rotar camara ABAJO (angulo vertical -)
    elif tecla == '2':
        camara_angulo_v -= 10
        # Limitar para no ir bajo el suelo
        if camara_angulo_v < -10:
            camara_angulo_v = -10
        print(f" Camara inclinada abajo (angulo: {camara_angulo_v:.0f}°)")
    # Teecla 4: Rotar camara a la IZQUIERDA (angulo horizontal -)
    elif tecla == '4':
        camara_angulo_h -= 15  # Rotar 15 grados
        if camara_angulo_h < 0:
            camara_angulo_h += 360
        print(f" Camara rotada izquierda (angulo: {camara_angulo_h:.0f}°)")
    # Teecla 6: Rotar camara a la DERECHA (angulo horizontal +)
    elif tecla == '6':
        camara_angulo_h += 15  # Rotar 15 grados
        if camara_angulo_h >= 360:
            camara_angulo_h -= 360
        print(f" Camara rotada derecha (angulo: {camara_angulo_h:.0f}°)")
    # Teecla 8: Rotar camara ARRIBA (angulo vertical +)
    elif tecla == '8':
        camara_angulo_v += 10
        # Limitar para no dar la vuelta completa
        if camara_angulo_v > 85:
            camara_angulo_v = 85
        print(f" Camara inclinada arriba (angulo: {camara_angulo_v:.0f}°)")
    # Teecla + : ACERCAR LA camara
    elif tecla == '+':
        camara_distancia -= 3
        if camara_distancia < 15:  # Minimo
            camara_distancia = 15
        print(f" Camara acercada (distancia: {camara_distancia:.0f})")
    # Teecla - : ALEJAR LA camara 
    elif tecla == '-':
        camara_distancia += 3
        if camara_distancia > 80:  # Maximo
            camara_distancia = 80
        print(f" Camara alejada (distancia: {camara_distancia:.0f})")
    # Teecla 5: RESETEAR camara a la posicion inicial que empieza el juego 
    elif tecla == '5':
        camara_distancia = 40.0
        camara_angulo_h = 46.0  # Resetear a 46° en vez de 45° para evitar diagonal
        camara_angulo_v = 30.0
        print(" Camara reseteada a posicion inicial")
    
    # Rotaciones de piezas
    # Q/A/Z = -90, W/S/X = 180, E/D/C = +90
    # Fila Q-W-E = Eje X
    # Fila A-S-D = Eje Y  
    # Fila Z-X-C = Eje Z
    
    # Eje X
    elif tecla == 'q' or tecla == 'Q':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_x(90)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("No se pudo rotar")
            else:
                sonidos.sonido_rotar()
                print("Rotado +90° (eje X)")
    # Teecla W: Rotar 180° en eje X
    elif tecla == 'w' or tecla == 'W':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_x(180)
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado 180° (eje X)")
    # Teecla E: Rotar -90° en eje X
    elif tecla == 'e' or tecla == 'E':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_x(-90)
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado -90° (eje X)")
    
    # EJE Y (VERTICAL)
    # Teecla A: Rotar +90° en eje Y
    elif tecla == 'a' or tecla == 'A':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_y(90)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado +90° (eje Y)")
    # Tecla S: Rotar 180° en eje Y
    elif tecla == 's' or tecla == 'S':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_y(180)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado 180° (eje Y)")
    # Teecla D: Rotar -90° en eje Y
    elif tecla == 'd' or tecla == 'D':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_y(-90)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado -90° (eje Y)")
    
    # --- EJE Z (PROFUNDIDAD) ---
    # Teecla Z: Rotar +90° en eje Z
    elif tecla == 'z' or tecla == 'Z':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_z(90)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado +90° (eje Z)")
    # Teecla X: Rotar 180° en eje Z
    elif tecla == 'x' or tecla == 'X':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_z(180)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado 180° (eje Z)")
    # Teecla C: Rotar -90° en eje Z
    elif tecla == 'c' or tecla == 'C':
        if pieza_actual is not None:
            geo_anterior = pieza_actual.clonar_geometria()
            pieza_actual.rotar_z(-90)
            
            if not tablero_juego.puede_colocar_pieza(pieza_actual):
                pieza_actual.restaurar_geometria(geo_anterior)
                print("Rotacion bloqueada (colision)")
            else:
                sonidos.sonido_rotar()
                print("Rotado -90° (eje Z)")
    
    # Teecla: ESPACIO drop rapido
    elif tecla == ' ':
        if pieza_actual is not None:
            # Sonido de drop
            sonidos.sonido_drop()
            # Bajar la pieza hasta que choque contra el piso donde tiene que caer la pieza
            while True:
                # Guardar posicion actual por si acaso
                pos_anterior = pieza_actual.clonar_posicion()
                # Intentar bajar
                pieza_actual.mover(0, -1, 0)
                # Si colisiona, volver atras y fijar
                if not tablero_juego.puede_colocar_pieza(pieza_actual):
                    pieza_actual.restaurar_posicion(pos_anterior)
                    tablero_juego.fijar_pieza(pieza_actual)
                    sonidos.sonido_fijar()
                    # Incrementar contador
                    piezas_colocadas += 1
                    # Verificar y eliminar planos completos
                    lineas_eliminadas = tablero_juego.eliminar_planos_completos()
                    if lineas_eliminadas > 0:
                        sonidos.sonido_linea()
                        calcular_puntaje(lineas_eliminadas)
                    # Crear nueva pieza (usar la siguiente y generar nueva siguiente con piezas permitidas)
                    pieza_actual = pieza_siguiente
                    # Reposicionar la pieza actual a la posicion inicial del tablero
                    pos_inicial = (ANCHO_TABLERO // 2 - 1, ALTO_TABLERO - 3, PROFUNDIDAD_TABLERO // 2 - 1)
                    pieza_actual.x, pieza_actual.y, pieza_actual.z = pos_inicial
                    pieza_siguiente = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas, pos_inicial)
                    
                    # Verificar Game Over: si la nueva pieza colisiona O se sale por arriba
                    posiciones_nuevas = pieza_actual.obtener_posiciones_absolutas()
                    hay_colision_real = False
                    se_sale_arriba = False
                    
                    for x, y, z in posiciones_nuevas:
                        # Verificar si se sale por arriba del tablero
                        if y >= ALTO_TABLERO:
                            se_sale_arriba = True
                            break
                        # Verificar colision con bloques ocupados
                        if tablero_juego.esta_dentro_limites(x, y, z):
                            if tablero_juego.esta_ocupada(x, y, z):
                                hay_colision_real = True
                                break
                    
                    if hay_colision_real or se_sale_arriba:
                        game_over = True
                        sonidos.sonido_gameover()
                        print("\n GAME OVER !!!\n")
                        # Volver al menu
                        GLUT.glutTimerFunc(0, volver_menu_callback, 0)
                    break
            
            print(" -- DROP -- ")
    # Forzar redibujo de la escena
    GLUT.glutPostRedisplay()

def teclas_especiales(key, x, y):
    """ Manejamos aca las teclas especiales como flechas  F1-F12,etc. Las flechas se usan para mover la pieza actual.
    Los movimientos hicimos que sean relativos a la orientacion de donde estee la camara para que siempre tenga sentido el movimiento
    Parametros: key: Codigo de la tecla especial (GLUT.GLUT_KEY_LEFT, etc.) x, y: Posicion del mouse (no la usamos) """
    
    global pieza_actual, tablero_juego, game_over, juego_pausado
    # No hacemos nada si el juego esta pausado o terminado
    if juego_pausado or game_over or pieza_actual is None:
        return
    # Guardar posicion actual por si el movimiento es invalido
    pos_anterior = pieza_actual.clonar_posicion()

    # Calcula y Obtiene el desplazamiento reñativo (dx, dz) segun la tecla y el angulo de camara
    dx, dz = calcular_movimiento_relativo_camara(key)
    
    # Aplicar el movimiento
    if dx != 0 or dz != 0:
        pieza_actual.mover(dx, 0, dz)
    
    # Si el movimiento causo una colision, deshacerlo
    if not tablero_juego.puede_colocar_pieza(pieza_actual):
        pieza_actual.restaurar_posicion(pos_anterior)
        # print("Movimiento bloqueado (colision)")
    else:
        # Movimiento exitoso: reproducir sonido
        if dx != 0 or dz != 0:
            sonidos.sonido_mover()
    
    # Redibujar la escena
    GLUT.glutPostRedisplay()

def calcular_puntaje(lineas_eliminadas):
    """
    Calcula y actualiza el puntaje segun las lineas eliminadas.
    Sistema de puntaje:
    - 1 linea  = 100 puntos × nivel
    - 2 lineas = 300 puntos × nivel (bonus)
    - 3 lineas = 500 puntos × nivel (super bonus)
    - 4+ lineas = 800 puntos × nivel (TETRIS)
    Tambien actualiza el nivel cada 10 lineas y aumenta la velocidad.
    Parametros:
        lineas_eliminadas: Numero de lineas eliminadas de una vez
    """
    global puntaje, nivel, lineas_totales, velocidad_actual, velocidad_base_nivel
    
    if lineas_eliminadas == 0:
        return
    
    # Calcular puntos segun numero de lineas
    if lineas_eliminadas == 1:
        puntos = 100 * nivel
    elif lineas_eliminadas == 2:
        puntos = 300 * nivel
    elif lineas_eliminadas == 3:
        puntos = 500 * nivel
    else:  # 4 o mas
        puntos = 800 * nivel
    
    # Actualizar puntaje y lineas
    puntaje += puntos
    lineas_totales += lineas_eliminadas
    
    # Calcular nuevo nivel (cada 10 lineas sube de nivel)
    nivel_anterior = nivel
    nivel = (lineas_totales // 10) + 1
    
    # Si subio de nivel, aumentar velocidad (reducir tiempo)
    if nivel > nivel_anterior:
        # Usar la velocidad base del nivel como referencia
        velocidad_actual = max(100, velocidad_base_nivel - (nivel - 1) * 50)
        print(f"\n NIVEL: {nivel} Velocidad aumentada (ahora: {velocidad_actual}ms)")

    # Mostrar informacion
    print(f"{puntos} puntos | Puntaje: {puntaje} | Nivel: {nivel} | Lineas: {lineas_totales}")

def timer_gravedad(valor):
    # Timer que hace caer la pieza automaticamnte
    global pieza_actual, tablero_juego, game_over, juego_pausado, pieza_siguiente
    global puntaje, nivel, lineas_totales, piezas_colocadas, velocidad_actual
    global estado_juego
    
    if estado_juego != ESTADO_JUGANDO:
        return
    
    if not juego_pausado and not game_over and pieza_actual is not None and tablero_juego is not None:
        
        # Guardar posicion actual
        pos_anterior = pieza_actual.clonar_posicion()
        
        # Intentar bajar la pieza
        pieza_actual.mover(0, -1, 0)
        
        # Si colisiona al bajar, fijar la pieza y crear una nueva
        if not tablero_juego.puede_colocar_pieza(pieza_actual):
            # Restaurar a la posicion anterior (antes de la colision)
            pieza_actual.restaurar_posicion(pos_anterior)
            
            # Fijar la pieza en el tablero
            tablero_juego.fijar_pieza(pieza_actual)
            sonidos.sonido_fijar()
            
            # Incrementar contador de piezas
            global piezas_colocadas
            piezas_colocadas += 1
            
            # Verificar y eliminar planos completos
            lineas_eliminadas = tablero_juego.eliminar_planos_completos()
            
            # Calcular puntaje si se eliminaron lineas
            if lineas_eliminadas > 0:
                sonidos.sonido_linea()
                calcular_puntaje(lineas_eliminadas)
            
            # Crear nueva pieza (usar la siguiente y generar nueva siguiente con piezas permitidas)
            pieza_actual = pieza_siguiente
            # Reposicionar la pieza actual a la posicion inicial del tablero
            pos_inicial = (ANCHO_TABLERO // 2 - 1, ALTO_TABLERO - 3, PROFUNDIDAD_TABLERO // 2 - 1)
            pieza_actual.x, pieza_actual.y, pieza_actual.z = pos_inicial
            pieza_siguiente = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas, pos_inicial)
            
            # Verificar si la nueva pieza puede colocarse (Game Over)
            # Solo es Game Over si colisiona con cubos YA FIJADOS
            # (no por estar fuera de limites arriba)
            posiciones_nuevas = pieza_actual.obtener_posiciones_absolutas()
            hay_colision_real = False
            
            for x, y, z in posiciones_nuevas:
                # Si esta dentro de limites Y ocupada = colision real
                if tablero_juego.esta_dentro_limites(x, y, z):
                    if tablero_juego.esta_ocupada(x, y, z):
                        hay_colision_real = True
                        break
            
            if hay_colision_real:
                game_over = True
                sonidos.sonido_gameover()
                print("\n GAME OVER !!!\n")
                print(f"Puntaje: {puntaje} | Nivel: {nivel} | Lineas: {lineas_totales}\n")
        
        # Redibujar la escena
        GLUT.glutPostRedisplay()
    
    # Programar el proximo timer (esto hace que se llame recursivamente)
    # Usar velocidad_actual que aumenta con el nivel
    GLUT.glutTimerFunc(velocidad_actual, timer_gravedad, 0)

def mouse_click(boton, estado, x, y):
    """ Maneja todos los eventos de clic del mouse. """
    global estado_juego, nivel_seleccionado
    if estado_juego != ESTADO_MENU:
        return
    # Solo procesar cuando se suelta el boton izquierdo
    #GLUT_DOWN es presionado
    #GLUT_UP es soltado
    if boton != GLUT.GLUT_LEFT_BUTTON or estado != GLUT.GLUT_UP:
        return
    # NO INVERTIR LAS COORDENADAS
    print(f"\n[DEBUG] Click en: ({x}, {y})")
    # Verificar clic en botones de nivel
    for nombre, config in BOTONES_NIVELES.items():
        if (config['x'] <= x <= config['x'] + config['ancho'] and
            config['y'] <= y <= config['y'] + config['alto']):
            nivel_seleccionado = nombre
            print(f" Nivel seleccionado: {NIVELES_DIFICULTAD[nombre]['nombre']}")
            GLUT.glutPostRedisplay()
            return
    
    # Verificar clic en boton EMPEZAR
    if nivel_seleccionado is not None:
        config = BOTON_EMPEZAR
        if (config['x'] <= x <= config['x'] + config['ancho'] and
            config['y'] <= y <= config['y'] + config['alto']):
            
            print(f" Iniciando juego con nivel: {NIVELES_DIFICULTAD[nivel_seleccionado]['nombre']}")
            iniciar_juego_con_dificultad(nivel_seleccionado)
            return
    
    # Verificar clic en boton SALIR
    config = BOTON_SALIR
    if (config['x'] <= x <= config['x'] + config['ancho'] and
        config['y'] <= y <= config['y'] + config['alto']):
        print(" Saliendo del juego...")
        #le dice a GLUT que termine la ejecucion y que cierre la aplicacion
        GLUT.glutLeaveMainLoop()
        return

def mouse_motion(x, y):
    """
    Maneja el movimiento del mouse (para efecto hover en botones).
    """
    global boton_hover
    
    # Solo en el menu
    if estado_juego != ESTADO_MENU:
        return
    
    # GLUT ya usa coordenadas correctas: Y desde arriba (0) hacia abajo
    # NO INVERTIR LAS COORDENADAS
    
    # print de coordenadas para debug
    print(f"\rMouse: ({x:4d}, {y:4d})", end='', flush=True)
    
    # Verificar sobre que boton esta el mouse
    boton_anterior = boton_hover
    boton_hover = None
    
    # Verificar botones de nivel
    for nombre, config in BOTONES_NIVELES.items():
        if (config['x'] <= x <= config['x'] + config['ancho'] and
            config['y'] <= y <= config['y'] + config['alto']):
            boton_hover = nombre
            if boton_hover != boton_anterior:
                GLUT.glutPostRedisplay()
            return
    
    # Verificar boton EMPEZAR
    config = BOTON_EMPEZAR
    if (config['x'] <= x <= config['x'] + config['ancho'] and
        config['y'] <= y <= config['y'] + config['alto']):
        boton_hover = 'EMPEZAR'
        if boton_hover != boton_anterior:
            GLUT.glutPostRedisplay()
        return
    
    # Verificar boton SALIR
    config = BOTON_SALIR
    if (config['x'] <= x <= config['x'] + config['ancho'] and
        config['y'] <= y <= config['y'] + config['alto']):
        boton_hover = 'SALIR'
        if boton_hover != boton_anterior:
            GLUT.glutPostRedisplay()
        return
    
    # Si cambio el estado, redibujar
    if boton_hover != boton_anterior:
        GLUT.glutPostRedisplay()

def iniciar_juego_con_dificultad(dificultad):
    """ Inicia el juego con la dificultad seleccionada.
        dificultad puede ser : 'PRINCIPIANTE', 'MEDIO', o 'DIFICIL' """
    global estado_juego, dificultad_seleccionada, piezas_permitidas
    global ANCHO_TABLERO, ALTO_TABLERO, PROFUNDIDAD_TABLERO
    global velocidad_actual, velocidad_base_nivel, tablero_juego, pieza_actual, pieza_siguiente
    global puntaje, nivel, lineas_totales, piezas_colocadas
    global game_over, juego_pausado
    global centro_x, centro_y, centro_z, camara_distancia
    
    # Guardar configuracion seleccionada
    dificultad_seleccionada = dificultad
    config = NIVELES_DIFICULTAD[dificultad]
    
    # Actualizar dimensiones del tablero
    ANCHO_TABLERO = config['ancho']
    ALTO_TABLERO = config['alto']
    PROFUNDIDAD_TABLERO = config['profundidad']
    
    # Actualizar piezas permitidas
    piezas_permitidas = config['piezas_permitidas']
    
    # Actualizar velocidad
    velocidad_actual = config['velocidad']
    velocidad_base_nivel = config['velocidad']  # Guardar velocidad base
    
    # Actualizar centro de camara (centro del tablero)
    centro_x = ANCHO_TABLERO / 2.0
    centro_y = ALTO_TABLERO / 2.0
    centro_z = PROFUNDIDAD_TABLERO / 2.0
    
    # Ajustar distancia de camara segun tamano del tablero
    tamano_max = max(ANCHO_TABLERO, ALTO_TABLERO, PROFUNDIDAD_TABLERO)
    camara_distancia = tamano_max * 2.0
    
    print(f"\nConfiguracion del nivel:")
    print(f"Tablero: {ANCHO_TABLERO}x{ALTO_TABLERO}x{PROFUNDIDAD_TABLERO}")
    print(f"Piezas: {len(piezas_permitidas)} tipos ({', '.join(piezas_permitidas)})")
    print(f"Velocidad: {velocidad_actual}ms")
    
    # Crear nuevo tablero
    tablero_juego = tablero.Tablero(ANCHO_TABLERO, ALTO_TABLERO, PROFUNDIDAD_TABLERO)
    
    # Crear primera pieza
    pos_inicial = (ANCHO_TABLERO // 2 - 1, ALTO_TABLERO - 3, PROFUNDIDAD_TABLERO // 2 - 1)
    pieza_actual = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas, pos_inicial)
    pieza_siguiente = piezas.crear_pieza_aleatoria_filtrada(piezas_permitidas, pos_inicial)
    
    # Resetear estadisticas
    puntaje = 0
    nivel = 1
    lineas_totales = 0
    piezas_colocadas = 0
    game_over = False
    juego_pausado = False
    
    # Cambiar al estado de juego
    estado_juego = ESTADO_JUGANDO
    
    # Iniciar timer de gravedad
    GLUT.glutTimerFunc(velocidad_actual, timer_gravedad, 0)
    
    print(f"\nJuego iniciado--> Nivel: {config['nombre']}\n")






def inicializar():
    """ Configura OpenGL y todas las opciones de renderizado.
        Esta funcion se llama UNA SOLA VEZ al inicio, despues de crear la ventana.
    esta es la configuracion inicial de OpenGL:
    - Color de fondo
    - Test de profundidad (para que objetos lejanos no tapen a los cercanos)
    - Sistema de iluminacion
    - Modo de proyeccion (perspectiva) """
    # glClearColor: Define el color de fondo de la ventana, el color del fondo
    # Parametros: (R, G, B, A) con valores de 0.0 a 1.0
    # Usamos un color degradado estilo espacio/galaxia
    GL.glClearColor(0.05, 0.05, 0.15, 1.0)  # Azul espacial profundo
    # glEnable(GL_DEPTH_TEST): Activa el "test de profundidad"
    # Esto hace que los objetos mas cercanos tapen a los mas lejanos
    # Sin esto, veriamos cosas raras (objetos lejanos encima de cercanos)
    GL.glEnable(GL.GL_DEPTH_TEST)
    # glDepthFunc: Como funciona el test de profundidad
    # GL_LESS: Un pixel se dibuja solo si esta MAS CERCA que el que habia antes, 
    # GL_LESS es la mas usada, ya que simula la vision humana
    GL.glDepthFunc(GL.GL_LESS)
    #Configuramos las dos luces que vamos a usar (LIGHT0 y LIGHT1)
    iluminacion.configurar_iluminacion()
    # Configuramos la proyeccion de la camara define COMO vemos el mundo 3D en la pantalla 2D
    # glMatrixMode(GL_PROJECTION): Cambiamos a la matriz de proyeccion, entonces todo lo que se hace ahora
    # afecta a la proyeccion y no a los objetos. antes de definir nuestra camara tenemos que cambiar a esta matriz projeccion
    GL.glMatrixMode(GL.GL_PROJECTION)
    # glLoadIdentity: Reseteamos la matriz (empezamos desde cero), Resetea la matriz actual y la deja como matriz identidad.
    #no hay rotacion, traslacion ni escalado, le digo borra cualquier configuracion previa y empezamos de cero
    GL.glLoadIdentity()
    # gluPerspective: Configuramos una proyeccion en PERSPECTIVA
    # (Los objetos lejanos se ven mas pequenos, como en la vida real)
    # Parametros:
    #   - fovy: Campo de vision vertical (en grados) - 45° es estandar
    #   - aspect: Relacion de aspecto (ancho/alto de la ventana)
    #   - zNear: Distancia minima que ve la camara (0.1 unidades)
    #   - zFar: Distancia maxima que ve la camara (100 unidades)
    aspecto = ancho_pantalla / alto_pantalla
    GLU.gluPerspective(
        45.0,      # Campo de vision de 45 grados
        aspecto,   # Relacion de aspecto de la ventana
        0.1,       # Plano cercano (near plane)
        100.0      # Plano lejano (far plane)
    )
    # glMatrixMode(GL_MODELVIEW): Volvemos a la matriz de modelo-vista
    # Esta es la matriz que usamos para dibujar objetos
    GL.glMatrixMode(GL.GL_MODELVIEW)
    # Calculamos la posicion inicial de la camara
    print(f" Camara posicionada Inicial en: ({ojox:.1f}, {ojoy:.1f}, {ojoz:.1f})")
    actualizar_posicion_camara()
    print(" OpenGL configurado")
    print(" Sistema de iluminacion activado")
    print(" Proyeccion en perspectiva configurada")
    print(f" Camara posicionada en ({ojox:.1f}, {ojoy:.1f}, {ojoz:.1f})")
    global tablero_juego, pieza_actual, pieza_siguiente    
    # El tablero y las piezas se crean cuando el usuario selecciona un nivel
    # Por ahora solo dejamos los valores en None
    tablero_juego = None
    pieza_actual = None
    pieza_siguiente = None
    #inicializamos el sistema de los sonidos    
    sonidos.inicializar_sonidos()
    sonidos.iniciar_musica_fondo()  # Iniciar musica de fondo
    print(" Sistema inicializado")
    print("=" * 70)
    print("ESPERANDO SELECCIoN DE NIVEL...")
    print("  Haz clic en un nivel o presiona:")
    print("    1 - Principiante (6x12x6, 3 piezas)")
    print("    2 - Medio (8x16x8, 4 piezas)")
    print("    3 - Dificil (10x20x10, 5 piezas)")
    print("=" * 70 + "\n")
    # NO iniciar el timer de gravedad aqui, se iniciará al seleccionar nivel
    GLUT.glutTimerFunc(VELOCIDAD_CAIDA, timer_gravedad, 0)

def main():
    """  Aca se inicializa el GLUT, luego se crea la ventana y  se registran las funciones
        callback (display, buttons) y se inicia el loop principal."""

    # glutInit: Inicializamos GLUT esto debe ser lo primero
    # sys.argv pasa los argumentos de linea de comandos
    GLUT.glutInit(sys.argv)
    # glutInitDisplayMode: Configura el modo de display
    # GLUT_DOUBLE: Usa doble buffer (evita parpadeos)
    # GLUT_RGB: Modo de color RGB (rojo, verde, azul)
    # GLUT_DEPTH: Activa el buffer de profundidad (para 3D)
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB | GLUT.GLUT_DEPTH)
    # glutInitWindowSize: Tamano inicial de la ventana en pixeles
    GLUT.glutInitWindowSize(ancho_pantalla, alto_pantalla)
    # glutInitWindowPosition: Posicion inicial de la ventana en la pantalla
    # (100, 100) = 100 pixeles desde la izquierda y 100 desde arriba
    GLUT.glutInitWindowPosition(100, 100)
    # glutCreateWindow: Crea la ventana con el titulo especificado
    GLUT.glutCreateWindow("TETRIS 3D EN OpenGL")
    # Llamamos a la funcion de inicializacion
    inicializar()
    # Callbacks son funciones que GLUT llama automaticamente cuando pasa algo
    # glutDisplayFunc: Funcion que dibuja la escena en la pantalla
    GLUT.glutDisplayFunc(display)    
    # glutKeyboardFunc: Funcion que maneja el teclado normal
    GLUT.glutKeyboardFunc(buttons)
    # glutSpecialFunc: Funcion que maneja teclas especiales (flechas)
    GLUT.glutSpecialFunc(teclas_especiales)
    # glutMouseFunc: Funcion que maneja click del mouse
    GLUT.glutMouseFunc(mouse_click)
    
    # glutPassiveMotionFunc: Funcion que maneja movimiento del mouse (sin boton presionado)
    GLUT.glutPassiveMotionFunc(mouse_motion)
    #imprimir la hora 
    import time
    print("INICIANDO LOOP PRINCIPAL DE GLUT a las %s" % time.strftime("%H:%M:%S"))
    print("=" * 70 + "\n")
    # glutMainLoop: Inicia el loop principal de eventos
    # Esta funcion NUNCA termina (hasta que cerramos la ventana)
    # Aqui GLUT se encarga de:
    #   - Detectar eventos (teclado, mouse, etc.)
    #   - Llamar a display() para redibujar
    #   - Mantener la ventana respondiendo
    
    GLUT.glutMainLoop()
if __name__ == "__main__":
    main()



#funciones de la ia, para que juegue automatico
def evaluar_posicion_ia(tablero_temp, pieza_temp):
    import copy
    # Simular la colocacion de la pieza
    tablero_copia = copy.deepcopy(tablero_temp)
    pieza_copia = copy.deepcopy(pieza_temp)
    # Bajar la pieza hasta el fondo
    while tablero_copia.puede_colocar_pieza(pieza_copia):
        pieza_copia.mover(0, -1, 0)
    pieza_copia.mover(0, 1, 0)
    # Fijar la pieza en el tablero temporal
    posiciones = pieza_copia.obtener_posiciones_absolutas()
    score = 0
    # CRITERIO 1: Premiamos posiciones BAJAS (lo más importante)
    altura_promedio = sum(y for x, y, z in posiciones) / len(posiciones)
    score -= altura_promedio * 10  #Penalizamos altura queremos que las piezas esten lo mas  abajo
    
    # CRITERIO 2: Verificar y PREMIAR MUCHO las lineas completas
    tablero_copia.fijar_pieza(pieza_copia)
    lineas = tablero_copia.eliminar_planos_completos()
    
    if lineas == 1:
        score += 500  # MUY bueno
    elif lineas == 2:
        score += 1500  # Excelente
    elif lineas == 3:
        score += 3000  # Increible
    elif lineas >= 4:
        score += 5000  # PERFECTO
    
    # CRITERIO 3: PENALIZAR FUERTEMENTE los huecos (espacios vacios con bloques encima)
    huecos_totales = 0
    for x in range(ANCHO_TABLERO):
        for z in range(PROFUNDIDAD_TABLERO):
            encontrado_bloque = False
            for y in range(ALTO_TABLERO - 1, -1, -1):
                if tablero_copia.esta_ocupada(x, y, z):
                    encontrado_bloque = True
                elif encontrado_bloque:
                    # Hay un hueco debajo de un bloque
                    huecos_totales += 1
    
    score -= huecos_totales * 50  # PENALIZACIoN FUERTE por huecos
    # CRITERIO 4: Premiar superficie PLANA (poca variacion de altura)
    alturas_columnas = {}
    for x in range(ANCHO_TABLERO):
        for z in range(PROFUNDIDAD_TABLERO):
            alturas_columnas[(x, z)] = 0
            for y in range(ALTO_TABLERO - 1, -1, -1):
                if tablero_copia.esta_ocupada(x, y, z):
                    alturas_columnas[(x, z)] = y + 1
                    break
    
    if len(alturas_columnas) > 0:
        valores = list(alturas_columnas.values())
        variacion = max(valores) - min(valores)
        score -= variacion * 8  # Penalizar superficies irregulares
    
    # CRITERIO 5: Premiar colocar piezas en los BORDES y esquinas
    for x, y, z in posiciones:
        # Premiar si está en el borde
        if x == 0 or x == ANCHO_TABLERO - 1 or z == 0 or z == PROFUNDIDAD_TABLERO - 1:
            score += 5

        # Premiar si está en contacto con otras piezas (más estable)
        contactos = 0
        for dx, dy, dz in [(-1,0,0), (1,0,0), (0,-1,0), (0,0,-1), (0,0,1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            if tablero_copia.esta_dentro_limites(nx, ny, nz):
                if tablero_copia.esta_ocupada(nx, ny, nz):
                    contactos += 1
        score += contactos * 3
    
    return score

def encontrar_mejor_movimiento_ia():
    #Encuentra la mejor posicion para la pieza actual
    if pieza_actual is None or tablero_juego is None:
        return None
    import copy
    mejor_score = -999999
    mejor_x = pieza_actual.x
    mejor_z = pieza_actual.z
    mejor_rotaciones = []
    
    # Probar diferentes rotaciones
    rotaciones_probar = [
        [],  # Sin rotacion
        [('y', 90)],  # 90 grados en Y
        [('y', 180)],  # 180 grados en Y
        [('y', -90)],  
        [('x', 90)],  
        [('z', 90)],  
    ]
    for rotaciones in rotaciones_probar:
        # Crear copia de la pieza
        pieza_temp = copy.deepcopy(pieza_actual)
        
        # Aplicar rotaciones
        for eje, angulo in rotaciones:
            if eje == 'y':
                pieza_temp.rotar_y(angulo)
            elif eje == 'x':
                pieza_temp.rotar_x(angulo)
            elif eje == 'z':
                pieza_temp.rotar_z(angulo)
        
        # Probar diferentes posiciones X y Z
        for test_x in range(ANCHO_TABLERO):
            for test_z in range(PROFUNDIDAD_TABLERO):
                # Mover pieza a la posicion de prueba
                pieza_test = copy.deepcopy(pieza_temp)
                pieza_test.x = test_x
                pieza_test.z = test_z
                pieza_test.y = ALTO_TABLERO - 3  # Posicion inicial alta (adapta a altura del tablero)
                
                # Verificar si la posicion es valida
                if not tablero_juego.puede_colocar_pieza(pieza_test):
                    continue
                
                # Evaluar esta posicion
                score = evaluar_posicion_ia(tablero_juego, pieza_test)
                
                if score > mejor_score:
                    mejor_score = score
                    mejor_x = test_x
                    mejor_z = test_z
                    mejor_rotaciones = rotaciones[:]
    
    return (mejor_x, mejor_z, mejor_rotaciones)

def ejecutar_movimiento_ia():
    #Ejecuta un movimiento inteligente de la IA.
    global pieza_actual
    
    if pieza_actual is None or game_over or juego_pausado:
        return
    
    # Encontrar el mejor movimiento
    resultado = encontrar_mejor_movimiento_ia()
    
    if resultado is None:
        return
    
    mejor_x, mejor_z, rotaciones = resultado
    
    # Aplicar rotaciones
    for eje, angulo in rotaciones:
        if eje == 'y':
            pieza_actual.rotar_y(angulo)
        elif eje == 'x':
            pieza_actual.rotar_x(angulo)
        elif eje == 'z':
            pieza_actual.rotar_z(angulo)
    
    # Mover a la posicion objetivo
    pieza_actual.x = mejor_x
    pieza_actual.z = mejor_z
    
    # Hacer drop inmediato
    while tablero_juego.puede_colocar_pieza(pieza_actual):
        pieza_actual.mover(0, -1, 0)
    pieza_actual.mover(0, 1, 0)
    
    # Reproducir sonido
    sonidos.sonido_drop()
    
    GLUT.glutPostRedisplay()

def timer_ia(valor):
    #Timer para que la IA ejecute movimientos automaticamente
    global timer_ia_activo
    if modo_automatico and not game_over and not juego_pausado:
        ejecutar_movimiento_ia()
        timer_ia_activo = True
        GLUT.glutTimerFunc(800, timer_ia, 0)  # Ejecutar cada 800ms
    else:
        timer_ia_activo = False
