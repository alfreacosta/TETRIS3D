""" MODULO DE ILUMINACION
    Este archivo configura el sistema de iluminacion del juego.
    Usar DOS luces (GL_LIGHT0 y GL_LIGHT1) como vimos en clases de KM
    para crear una iluminacion mucho mas realista y agradable.
    La iluminacion hace que los objetos 3D se vean con volumen y profundidad. """
from OpenGL import GL

def configurar_iluminacion():
    """ Esta funcion debe llamarse UNA SOLA VEZ al inicio del programa,
        despues de crear la ventana OpenGL y antes de empezar a dibujar.
        1. Iluminacion global (GL_LIGHTING)
        2. Dos luces: GL_LIGHT0 (luz principal) y GL_LIGHT1 (luz de relleno)
        3. Materiales con GL_COLOR_MATERIAL (para que glColor3f funcione con luces)
        4. Suavizado de sombreado (GL_SMOOTH) """

    # glEnable(GL_LIGHTING): Activa el sistema de iluminacion de OpenGL
    # Sin esto, las luces no tienen ningun efecto
    GL.glEnable(GL.GL_LIGHTING)
    
    # glEnable(GL_COLOR_MATERIAL): Permite que glColor3f funcione con iluminacion
    # Normalmente con iluminacion hay que definir materiales complejos,
    # pero esto simplifica y permite usar colores directamente
    GL.glEnable(GL.GL_COLOR_MATERIAL)
    
    # glColorMaterial: Especifica que propiedades del material controla glColor3f
    # GL_FRONT_AND_BACK: Afecta caras frontales y traseras
    # GL_AMBIENT_AND_DIFFUSE: glColor3f controla color ambiental y difuso
    GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)
    
    # glShadeModel(GL_SMOOTH): Suaviza los colores entre vertices
    # GL_SMOOTH: Interpola colores suavemente (mejor calidad visual)
    # GL_FLAT: Cada cara tiene un solo color (se ve mas "cuadrado")
    GL.glShadeModel(GL.GL_SMOOTH)
    
    # glEnable(GL_LIGHT0): Activa la primera luz
    # OpenGL tiene 8 luces disponibles: GL_LIGHT0 hasta GL_LIGHT7
    #cuales son esos 7 que diferen?
    GL.glEnable(GL.GL_LIGHT0)
    # Posicion de la luz 0
    # Formato: (x, y, z, w)
    # w=1.0 significa que es una luz POSICIONAL (tiene ubicacion fija)
    # w=0.0 significaria luz DIRECCIONAL (como el sol, viene de infinito)
    luz0_posicion = (10.0, 15.0, 10.0, 1.0)  # Arriba y adelante del tablero
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, luz0_posicion)
    # Componente ambiental (luz que esta en todas partes, sin direccion)
    # RGB con valores de 0.0 a 1.0
    # Balance medio: suficiente para ver todo, pero con sombras visibles
    luz0_ambiental = (0.2, 0.2, 0.2, 1.0)  # Equilibrado
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, luz0_ambiental)
    # Componente difusa (luz que rebota en superficies mates)
    # Esta es la "luz principal" que vemos
    # Blanca e intensa (0.8 = 80% de intensidad)
    luz0_difusa = (0.8, 0.8, 0.8, 1.0)  # Blanco brillante
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, luz0_difusa)
    # Componente especular (brillos en superficies lisas/reflectantes)
    # Baja intensidad para que no sea muy "plastico"
    luz0_especular = (0.5, 0.5, 0.5, 1.0)  # Gris medio
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, luz0_especular)
    

    # Esta segunda luz vamos usar para rellenar las sombras que crea la primera luz
    # Evita que las zonas oscuras sean TOTALMENTE negras
    # glEnable(GL_LIGHT1): Activa la segunda luz
    GL.glEnable(GL.GL_LIGHT1)
    # Posicion opuesta a la luz 0 (ilumina desde atrás-arriba para compensar)
    luz1_posicion = (-8.0, 12.0, -8.0, 1.0)  # Más arriba y atrás
    GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, luz1_posicion)

    # Ambiental moderado para iluminar zonas oscuras
    luz1_ambiental = (0.15, 0.15, 0.15, 1.0)  # Más luz ambiental
    GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, luz1_ambiental)

    # Difusa blanca suave (relleno general, no azul exagerado)
    luz1_difusa = (0.4, 0.4, 0.5, 1.0)  # Blanco-azulado suave
    GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, luz1_difusa)

    # Sin especular en la luz de relleno (no queremos brillos extra)
    luz1_especular = (0.0, 0.0, 0.0, 1.0)  # Negro (desactivado)
    GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, luz1_especular)
    
    #Configurar propiedades especulares del material
    # Especular del material (como "brilla" el material)
    # Valores bajos para que no se vea muy plastico
    material_especular = (0.3, 0.3, 0.3, 1.0)  # Gris oscuro
    GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, material_especular)
    # Shininess (que tan "enfocado" es el brillo)
    # Valores: 0 a 128
    # Bajo (10-30) = brillo difuso, mate
    # Alto (60-128) = brillo concentrado, muy reflectante
    GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 20.0)  # Brillo suave
    
    print("Sistema de iluminacion configurado:")
    print("-LUZ 0: Luz principal blanca (arriba-adelante)")
    print("-LUZ 1: Luz de relleno azulada (atras-abajo)")

def actualizar_luces():
    """ funcion para actualizar las posiciones de las luces. Esta funcion debe llamarse DENTRO del loop de dibujo (display),
    Despues de configurar la camara con gluLookAt porque las posiciones de las luces se transforman con la matriz
    MODELVIEW actual. """
    # Reconfigurar posiciones (las mismas que en configurar_iluminacion)
    luz0_posicion = (10.0, 15.0, 10.0, 1.0)
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, luz0_posicion)
    luz1_posicion = (-8.0, 12.0, -8.0, 1.0)
    GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, luz1_posicion)

# def desactivar_iluminacion():
#     """ funcion para desactivar temporalmente el sistema de iluminacion.
#     Util para dibujar cosas que no queremos que se iluminen:
#     Despues de dibujar, hay que llamar a reactivar_iluminacion() """
#     GL.glDisable(GL.GL_LIGHTING)

# def reactivar_iluminacion():
#     """ Reactiva el sistema de iluminacion despues de desactivarlo.
#         Ejemplo:
#         desactivar_iluminacion()
#         dibujar_ejes()  # Se dibuja sin iluminacion
#         reactivar_iluminacion()
#         dibujar_cubo()  # Se dibuja de vuelta con iluminacion """
#     GL.glEnable(GL.GL_LIGHTING)