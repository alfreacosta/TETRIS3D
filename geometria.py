""" MODULO DE GEOMETRIA: En este archivo vamos a configurar y a  definir la geometria del cubo unitario que vamos a 
    usar en el juego. 
    Un cubo unitario es un cubo de 1x1x1 que sera la unidad basica para construir todas las piezas del Tetris."""
from OpenGL import GL
# Vertices del cubo (8 esquinas)
# Siguiendo el estilo del profe KM: usar TUPLAS y no listas
# Cada vertice es un punto (x, y, z) en el espacio 3D
# El cubo va de (0,0,0) a (1,1,1)
CUBO_VERTICES = (
    # Cara frontal (z=0)
    (0, 0, 0),  # 0: Esquina inferior-izquierda-frontal
    (1, 0, 0),  # 1: Esquina inferior-derecha-frontal
    (1, 1, 0),  # 2: Esquina superior-derecha-frontal
    (0, 1, 0),  # 3: Esquina superior-izquierda-frontal    
    # Cara trasera (z=1)
    (0, 0, 1),  # 4: Esquina inferior-izquierda-trasera
    (1, 0, 1),  # 5: Esquina inferior-derecha-trasera
    (1, 1, 1),  # 6: Esquina superior-derecha-trasera
    (0, 1, 1),  # 7: Esquina superior-izquierda-trasera
)
# Caras del cubo (6 caras, cada una con 4 vertices)
# Cada cara es un cuadrilatero (QUAD) definido por 4 indices
# Los indices se refieren a CUBO_VERTICES
# Los vertices estan en orden anti-horario (para que las normales apunten hacia afuera)
CUBO_CARAS = (
    (0, 1, 2, 3),  # Cara frontal (mirando hacia +Z)
    (5, 4, 7, 6),  # Cara trasera (mirando hacia -Z)
    (4, 0, 3, 7),  # Cara izquierda (mirando hacia +X)
    (1, 5, 6, 2),  # Cara derecha (mirando hacia -X)
    (3, 2, 6, 7),  # Cara superior (mirando hacia -Y)
    (4, 5, 1, 0),  # Cara inferior (mirando hacia +Y)
)
# Normales de cada cara (vectores perpendiculares a cada cara)
# Las normales son importantes para la iluminacion
# Cada normal es un vector (x, y, z) de longitud 1
CUBO_NORMALES = (
    (0.0, 0.0, -1.0),  # Normal cara frontal (apunta hacia adelante)
    (0.0, 0.0, 1.0),   # Normal cara trasera (apunta hacia atras)
    (-1.0, 0.0, 0.0),  # Normal cara izquierda (apunta hacia la izquierda)
    (1.0, 0.0, 0.0),   # Normal cara derecha (apunta hacia la derecha)
    (0.0, 1.0, 0.0),   # Normal cara superior (apunta hacia arriba)
    (0.0, -1.0, 0.0),  # Normal cara inferior (apunta hacia abajo)
)

def dibujar_cubo(x, y, z, color):
    """ Esta funcion Dibuja un cubo unitario de 1x1x1 en la posicion (x, y, z)
        los parametros son :
        x, y, z: Posicion del cubo en el espacio 3D (esquina inferior-izquierda-frontal)
        color: Tupla RGB con valores de 0.0 a 1.0, ejemplo: (1.0, 0.0, 0.0) para rojo
        Ejemplo de uso:
        dibujar_cubo(5, 10, 3, (0.0, 1.0, 1.0))  # Dibuja un cubo cyan en posicion (5,10,3)
    
        Esta funcion usa glPushMatrix/glPopMatrix para no afectar otras transformaciones """
    
    # glPushMatrix: sirve para guardar el estado actual de la matriz de la transformacion
    # Esto es como hacer un "checkpoint" para poder volver despues
    GL.glPushMatrix()

    # glTranslatef: Mueve el origen a la posicion (x, y, z)
    # # Todo lo que dibujemos ahora estara en esa posicion
    GL.glTranslatef(x, y, z)
    
    # Establecer el color del cubo
    GL.glColor3fv(color)

    # glBegin(GL_QUADS): Dibuja los cuadrilateros
    # Un cuadrilatero es una figura de 4 lados (las caras del cubo)
    GL.glBegin(GL.GL_QUADS)
    
    # Dibujamos cada cara del cubo
    for i, cara in enumerate(CUBO_CARAS):
        # glNormal3fv: Define la normal de la cara, esto es importante para la iluminacion
        # La normal es un vector perpendicular a la superficie
        GL.glNormal3fv(CUBO_NORMALES[i])

        # Dibujamos los 4 vertices de esta cara
        for indice_vertice in cara:
            # Obtenemos las coordenadas del vertice
            vertice = CUBO_VERTICES[indice_vertice]
            # glVertex3fv: Define un vertice (punto) en 3D
            GL.glVertex3fv(vertice)
    
    #Terminamos de dibujar
    GL.glEnd()
    
    # Opcional: Dibujar bordes del cubo en negro para que se vea mejor
    # Esto hace que cada cubo tenga un contorno negro
    GL.glColor3f(0.0, 0.0, 0.0)  # Color negro
    GL.glLineWidth(1)  # Grosor de la linea
    
    # glBegin(GL_LINE_LOOP): Dibuja lineas conectadas en un loop cerrado
    for cara in CUBO_CARAS:
        GL.glBegin(GL.GL_LINE_LOOP)
        for indice_vertice in cara:
            vertice = CUBO_VERTICES[indice_vertice]
            GL.glVertex3fv(vertice)
        GL.glEnd()
    
    # glPopMatrix: Restaura el estado de transformaciones anterior
    # Volvemos al "checkpoint" que guardamos al inicio
    GL.glPopMatrix()

def dibujar_ejes(longitud=10):
    """ Dibuja los ejes de  coordenados X, Y, Z
        -X: Rojo (hacia la derecha) - etiqueta "X"
        -Y: Verde (hacia arriba) - etiqueta "Y"
        -Z: Azul (hacia adelante/atras) - etiqueta "Z"
        Parametros: longitud: Longitud de cada eje (por defecto 10 unidades)
        Esto tambien hacemos para utilizar lo que KM explocp en sus ejemplos en clases """
    
    # Desactivar iluminacio
    GL.glDisable(GL.GL_LIGHTING)
    
    #  dibujamos las lineas
    GL.glBegin(GL.GL_LINES)
    
    # Eje X - Rojo (horizontal, de izquierda a derecha)
    GL.glColor3f(1.0, 0.0, 0.0)  # Color rojo
    GL.glVertex3f(0.0, 0.0, 0.0)  # Punto inicial (origen)
    GL.glVertex3f(longitud, 0.0, 0.0)  # Punto final (en direccion X)
    
    # Eje Y - Verde (vertical, de abajo hacia arriba) - MÁS LARGO
    GL.glColor3f(0.0, 1.0, 0.0)  # Color verde
    GL.glVertex3f(0.0, 0.0, 0.0)  # Punto inicial (origen)
    GL.glVertex3f(0.0, longitud * 1.8, 0.0)  # Punto final (80% más largo)
    
    # Eje Z - Azul (profundidad, hacia adelante)
    GL.glColor3f(0.0, 0.0, 1.0)  # Color azul
    GL.glVertex3f(0.0, 0.0, 0.0)  # Punto inicial (origen)
    GL.glVertex3f(0.0, 0.0, longitud)  # Punto final (en direccion Z)
    
    # Terminamos de dibujar lineas
    GL.glEnd()
    
    # Dibujar etiquetas en los extremos de cada eje
    from OpenGL import GLUT
    
    # Etiqueta X (rojo)
    GL.glColor3f(1.0, 0.0, 0.0)
    GL.glRasterPos3f(longitud + 0.5, 0.0, 0.0)
    GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord('X'))
    
    # Etiqueta Y (verde)
    GL.glColor3f(0.0, 1.0, 0.0)
    GL.glRasterPos3f(0.0, longitud * 1.8 + 0.5, 0.0)
    GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord('Y'))
    
    # Etiqueta Z (azul)
    GL.glColor3f(0.0, 0.0, 1.0)
    GL.glRasterPos3f(0.0, 0.0, longitud + 0.5)
    GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord('Z'))
    
    # Reactivar iluminacion para el resto de objetos
    GL.glEnable(GL.GL_LIGHTING)

def dibujar_grilla(ancho, alto, profundidad, espaciado=2):
    """ Dibuja una grilla 3D que representa el tablero del Tetris
        La grilla muestra las lineas que delimitan cada posicion del tablero.
        Es como dibujar una caja de alambre donde caeran las piezas.

        Param:
            ancho: Numero de cubos de ancho (tipicamente 10)
            alto: Numero de cubos de alto (tipicamente 20)
            profundidad: Numero de cubos de profundidad (tipicamente 10)
            espaciado: Cada cuantos cubos dibujar una linea (default=2 para menos densidad) """
    
    # Desactivar iluminacion
    GL.glDisable(GL.GL_LIGHTING)
    # Color gris mas claro y transparente (menos intrusivo)
    GL.glColor3f(0.25, 0.25, 0.3)  # Gris azulado tenue
    
    if False:
        #Desactivamos las lineas de la grilla para que no molesten visualmente 
        # glBegin(GL_LINES): Dibujamos lineas
        GL.glBegin(GL.GL_LINES)
        
        # Lineas horizontales (paralelas al eje X)
        for y in range(0, alto + 1, espaciado):
            for z in range(0, profundidad + 1, espaciado):
                # Linea desde (0, y, z) hasta (ancho, y, z)
                GL.glVertex3f(0, y, z)
                GL.glVertex3f(ancho, y, z)
        
        # Lineas verticales (paralelas al eje Y)
        for x in range(0, ancho + 1, espaciado):
            for z in range(0, profundidad + 1, espaciado):
                # Linea desde (x, 0, z) hasta (x, alto, z)
                GL.glVertex3f(x, 0, z)
                GL.glVertex3f(x, alto, z)
        
        # Lineas de profundidad (paralelas al eje Z)
        for x in range(0, ancho + 1, espaciado):
            for y in range(0, alto + 1, espaciado):
                # Linea desde (x, y, 0) hasta (x, y, profundidad)
                GL.glVertex3f(x, y, 0)
                GL.glVertex3f(x, y, profundidad)

        GL.glEnd()
    
    # Ahora dibujamos los BORDES del tablero en un color MAS VISIBLE
    GL.glColor3f(0.8, 0.8, 1.0)  # Azul claro brillante para los bordes
    GL.glLineWidth(3.5)  # Lineas MAS gruesas para mejor visibilidad
    
    # Dibujar el marco exterior (caja completa)
    GL.glBegin(GL.GL_LINE_LOOP)
    # Base (Y=0)
    GL.glVertex3f(0, 0, 0)
    GL.glVertex3f(ancho, 0, 0)
    GL.glVertex3f(ancho, 0, profundidad)
    GL.glVertex3f(0, 0, profundidad)
    GL.glEnd()
    
    GL.glBegin(GL.GL_LINE_LOOP)
    # Tope (Y=alto)
    GL.glVertex3f(0, alto, 0)
    GL.glVertex3f(ancho, alto, 0)
    GL.glVertex3f(ancho, alto, profundidad)
    GL.glVertex3f(0, alto, profundidad)
    GL.glEnd()
    
    # Lineas verticales conectando base y tope
    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(0, 0, 0)
    GL.glVertex3f(0, alto, 0)
    
    GL.glVertex3f(ancho, 0, 0)
    GL.glVertex3f(ancho, alto, 0)
    
    GL.glVertex3f(ancho, 0, profundidad)
    GL.glVertex3f(ancho, alto, profundidad)
    
    GL.glVertex3f(0, 0, profundidad)
    GL.glVertex3f(0, alto, profundidad)
    GL.glEnd()
    GL.glLineWidth(1.0)  # Restauramos el grosor normal    
    # Reactivar iluminacion
    GL.glEnable(GL.GL_LIGHTING)

