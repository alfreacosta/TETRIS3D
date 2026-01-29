""" Este archivo define las 5 piezas del Tetris 3D y la clase Pieza.
    Las 5 piezas son:
    1. I (Palillo): 4 cubos en linea
    2. O (Cuadrado): 2x2 cubos
    3. L (Ele): Forma de L con 4 cubos
    4. T (Te): Forma de T con 4 cubos
    5. Z (Zeta): Forma de Z con 4 cubos
    Cada pieza tiene:
    - Geometria (posiciones relativas de sus cubos)
    - Color
    - Posicion actual en el tablero
    - Metodos para moveerse y rotarse """
import random
# Siguiendo lo visto en clase el profe recomendo siempre mejor usar TUPLAS, no listas
# Cada geometria es una tupla de tuplas (x,y,z) relativas
# (0,0,0) es el "pivote" de la pieza
# PIEZA I (Palillo) - 4 cubos en linea horizontal
GEOMETRIA_I = (
    (0, 0, 0),   # Cubo 1 (pivote)
    (1, 0, 0),   # Cubo 2 (a la derecha)
    (2, 0, 0),   # Cubo 3 a la derecha
    (3, 0, 0),   # Cubo 4 a la derecha, 4ta posicion
)
GEOMETRIA_O = (
    (0, 0, 0),   # Esquina inferior a la izquierda
    (1, 0, 0),   # Esquina inferior a la derecha
    (0, 1, 0),   # Esquina superior a la izquierda
    (1, 1, 0),   # Esquina superior a la derecha
)
GEOMETRIA_L = (
    (0, 0, 0),   # Base izquierda
    (0, 1, 0),   # Medio
    (0, 2, 0),   # Arriba
    (1, 0, 0),   # Base derecha (forma la L)
)
GEOMETRIA_T = (
    (0, 0, 0),   # Izquierda
    (1, 0, 0),   # Centro (pivote)
    (2, 0, 0),   # Derecha
    (1, 1, 0),   # Arriba del centro
)
GEOMETRIA_Z = (
    (0, 1, 0),   # Arriba-izquierda
    (1, 1, 0),   # Arriba-derecha
    (1, 0, 0),   # Abajo-centro
    (2, 0, 0),   # Abajo-derecha
)
COLOR_I = (0.0, 1.0, 1.0)   # Cyan (celeste brillante)
COLOR_O = (1.0, 1.0, 0.0)   # Amarillo
COLOR_L = (1.0, 0.5, 0.0)   # Naranja
COLOR_T = (0.5, 0.0, 1.0)   # Purpura/Morado
COLOR_Z = (1.0, 0.0, 0.0)   # Rojo

# DICCIONARIO DE LOS TIPOS DE PIEZAS QUE VAMOS A USAR EN EL JUEGO  
TIPOS_PIEZAS = {
    'I': {'geometria': GEOMETRIA_I, 'color': COLOR_I, 'nombre': 'Palillo'},
    'O': {'geometria': GEOMETRIA_O, 'color': COLOR_O, 'nombre': 'Cuadrado'},
    'L': {'geometria': GEOMETRIA_L, 'color': COLOR_L, 'nombre': 'Ele'},
    'T': {'geometria': GEOMETRIA_T, 'color': COLOR_T, 'nombre': 'Te'},
    'Z': {'geometria': GEOMETRIA_Z, 'color': COLOR_Z, 'nombre': 'Zeta'}, }

class Pieza:
    """ Representa una pieza del Tetris que puede moveerse y rotarse.
        Atributos:
            tipo: Letra identificadora ('I', 'O', 'L', 'T', 'Z')
            geometria: Tupla de posiciones relativas (x, y, z)
            color: Tupla RGB del color de la pieza
            x,y,z: Posicion actual del pivote en el tablero
            nombre: Nombre descriptivo de la pieza """
    
    def __init__(self, tipo, posicion_inicial=(4, 17, 4)):
        # Validar que el tipo sea valido
        if tipo not in TIPOS_PIEZAS:
            raise ValueError(f"Tipo de pieza invalido: {tipo}. Debe ser I, O, L, T o Z")
        # Guardar la informacion de la pieza
        self.tipo = tipo
        self.geometria = TIPOS_PIEZAS[tipo]['geometria']
        self.color = TIPOS_PIEZAS[tipo]['color']
        self.nombre = TIPOS_PIEZAS[tipo]['nombre']
        # Posicion actual del pivote de la pieza
        self.x, self.y, self.z = posicion_inicial
        #PIEZA INICIAL EN FACIL     (2,9,2)
        #PIEZA INICIAL EN MEDIO     (3,13,3)
        #PIEZA INICIAL EN DIFICIL   (4,17,4)
        print(f"Piezaa '{self.nombre}' ({tipo}) creada en posicion ({self.x}, {self.y}, {self.z})")

    def obtener_posiciones_absolutas(self):
        """ Calcula las posiciones absolutas de todos los cubos de la pieza.
            Suma la posicion del pivote (x, y, z) a cada posicion relativa de la geometria.
            Retorna: Lista de tuplas (x, y, z) con las posiciones absolutas
            Ejemplo: Si la pieza esta en (5, 10, 3) y su geometria es: [(0,0,0), (1,0,0), (2,0,0), (3,0,0)]
                Retorna: [(5,10,3), (6,10,3), (7,10,3), (8,10,3)]
        """
        posiciones = []
        i=0
        for dx, dy, dz in self.geometria:
            # Sumar posicion relativa a posicion del pivote
            pos_x = self.x + dx
            pos_y = self.y + dy
            pos_z = self.z + dz
            posiciones.append((pos_x, pos_y, pos_z))
            i += 1
        return posiciones
    
    
    def mover(self, dx, dy, dz):
        """ Mueve la pieza sumando un desplazamiento a su posicion.
            Parametros:
                dx: Desplazamiento en X (positivo = derecha, negativo = izquierda)
                dy: Desplazamiento en Y (positivo = arriba, negativo = abajo)
                dz: Desplazamiento en Z (positivo = adelante, negativo = atras)
            Ejemplo:
                pieza.moveer(1, 0, 0)   # Moveer 1 cubo a la derecha
                pieza.moveer(0, -1, 0)  # Moveer 1 cubo hacia abajo (gravedad)
                pieza.moveer(0, 0, -1)  # Moveer 1 cubo hacia atras"""
        
        #Esta funcion NO verifica colisiones, solo cambia la posicion. La verificacion de colisiones hacemos en en tablero.py
        self.x += dx
        self.y += dy
        self.z += dz
    
    
    def clonar_posicion(self):
        """ Retorna una copia de la posicion actual se usa para probar un movimiento sin modificar la pieza real.
        Retorna una Tupla (x, y, z) con la posicion actual """
        return (self.x, self.y, self.z)
    
    
    def restaurar_posicion(self, posicion):
        """ Restaura la pieza a una posicion guardada se usa para deshacer un movimiento invalido.
            Parametros:
            posicion: Tupla (x, y, z) con la posicion a restaurar """
        self.x, self.y, self.z = posicion
    
    
    def rotar_y(self, angulo=90):
        """ Rota la pieza alrededor del eje Y (vertical).
            Rotacion en Y (vista desde arriba):
            - 90°: Gira hacia la derecha
            - -90°: Gira hacia la izquierda
            - 180°: Media vuelta
            Parametros: angulo: Angulos a rotar (90, -90, 180)
            Formulas de rotacion en Y:
                x' = z * sin(θ) + x * cos(θ)
                y' = y (no cambia)
                z' = z * cos(θ) - x * sin(θ)
            Para 90°:  (x,y,z) -> (z, y, -x)
            Para -90°: (x,y,z) -> (-z, y, x)
            Para 180°: (x,y,z) -> (-x, y, -z)
            """
        nueva_geometria = []
        for x, y, z in self.geometria:
            if angulo == 90:
                # Rotar 90° horario (vista desde arriba)
                nuevo_x = z
                nuevo_y = y
                nuevo_z = -x
            elif angulo == -90:
                # Rotar 90° antihorario
                nuevo_x = -z
                nuevo_y = y
                nuevo_z = x
            elif angulo == 180:
                # Rotar 180°
                nuevo_x = -x
                nuevo_y = y
                nuevo_z = -z
            else:
                # Angulo no soportado, no rotar
                nuevo_x, nuevo_y, nuevo_z = x, y, z
            
            nueva_geometria.append((nuevo_x, nuevo_y, nuevo_z))
        
        # Actualizar geometria (convertir lista a tupla)
        self.geometria = tuple(nueva_geometria)
    
    
    def rotar_x(self, angulo=90):
        """ Rota la pieza alrededor del eje X (horizontal).
            Rotacion en X (vista desde el lado):
            - 90°: Gira hacia adelante
            - -90°: Gira hacia atras
            Formulas de rotacion en X:
                x' = x (no cambia)
                y' = y * cos(θ) - z * sin(θ)
                z' = y * sin(θ) + z * cos(θ)
            Para 90°:  (x,y,z) -> (x, -z, y)
            Para -90°: (x,y,z) -> (x, z, -y) """
        nueva_geometria = []
        
        for x, y, z in self.geometria:
            if angulo == 90:
                nuevo_x = x
                nuevo_y = -z
                nuevo_z = y
            elif angulo == -90:
                nuevo_x = x
                nuevo_y = z
                nuevo_z = -y
            elif angulo == 180:
                nuevo_x = x
                nuevo_y = -y
                nuevo_z = -z
            else:
                nuevo_x, nuevo_y, nuevo_z = x, y, z
            
            nueva_geometria.append((nuevo_x, nuevo_y, nuevo_z))
        
        self.geometria = tuple(nueva_geometria)
    
    
    def rotar_z(self, angulo=90):
        """ Rota la pieza alrededor del eje Z (profundidad).    
            Rotacion en Z (vista frontal):
            - 90°: Gira hacia la derecha
            - -90°: Gira hacia la izquierda
            Formulas de rotacion en Z:
                x' = x * cos(θ) - y * sin(θ)
                y' = x * sin(θ) + y * cos(θ)
                z' = z (no cambia)
            Para 90°:  (x,y,z) -> (y, -x, z)
            Para -90°: (x,y,z) -> (-y, x, z) """
        nueva_geometria = []
        
        for x, y, z in self.geometria:
            if angulo == 90:
                nuevo_x = y
                nuevo_y = -x
                nuevo_z = z
            elif angulo == -90:
                nuevo_x = -y
                nuevo_y = x
                nuevo_z = z
            elif angulo == 180:
                nuevo_x = -x
                nuevo_y = -y
                nuevo_z = z
            else:
                nuevo_x, nuevo_y, nuevo_z = x, y, z
            
            nueva_geometria.append((nuevo_x, nuevo_y, nuevo_z))
        
        self.geometria = tuple(nueva_geometria)
    
    
    def clonar_geometria(self):
        #Retorna una copia de la geometria actual para probar una rotacion sin modificar la pieza real
        return tuple(self.geometria)
    
    def restaurar_geometria(self, geometria):
        #Restaura la pieza a una geometria guardada para deshacer una rotacion invalida
        self.geometria = geometria
    
    def __str__(self):
        #Ejemplo: print(pieza)  Muestra: Pieza Palillo (I) en (5, 10, 3)
        return f"Pieza {self.nombre} ({self.tipo}) en ({self.x}, {self.y}, {self.z})"

def crear_pieza_aleatoria_filtrada(piezas_permitidas=None, posicion_inicial=(4, 17, 4)):
    #Crea una pieza aleatoria de entre las piezas permitidas segun la dificultad que se esta jugando
    # Si no se especifican piezas permitidasse usa todas
    if piezas_permitidas is None:
        piezas_permitidas = list(TIPOS_PIEZAS.keys())
    # Elegir un tipo aleatorio de entre las permitidas
    tipo = random.choice(piezas_permitidas)
    # Crear y retornar la pieza
    return Pieza(tipo, posicion_inicial)