""" MODULO DEL TABLERO 
    Este archivo maneja la logica del tablero del Tetris:
        - Matriz 3D para almacenar cubos fijos
        - Deteccion de colisiones
        - Verificacion de limites
        - Fijar piezas cuando tocan el suelo u otras piezas
        - Detectar lineas completas (para eliminarlas)

    El tablero es una matriz 3D de dimensiones:
        - Ancho (X): 10 cubos
        - Alto (Y): 20 cubos  
        - Profundidad (Z): 10 cubos

    Cada posicion puede estar:
        - None: Vacia
        - (r, g, b): Ocupada por un cubo de ese color """

class Tablero:

    def __init__(self, ancho=10, alto=20, profundidad=10):
        #Crea un nuevo tablero vacio 
        self.ancho = ancho
        self.alto = alto
        self.profundidad = profundidad
        
        # Crear matriz 3D vacia
        # matriz[x][y][z] = None (vacio) o (r, g, b) (color del cubo)
        self.matriz = [
            [
                [None for z in range(profundidad)]
                for y in range(alto)
            ]
            for x in range(ancho)
        ]
        print(f" Tablero creado: {ancho}x{alto}x{profundidad}")
    
    def esta_dentro_limites(self, x, y, z):
        #Verifica si una posicion esta dentro de los limites del tablero,  x, y, z: Coordenadas a verificar
        #devuelve: True si esta dentro, False si esta fuera
        
        return (0 <= x < self.ancho and
                0 <= y < self.alto and
                0 <= z < self.profundidad)
    
    def esta_ocupada(self, x, y, z):
        #Verifica si una posicion del tablero esta ocupada.
        #Parametros: x, y, z: Coordenadas a verificar, devue lve True si esta ocupada, False si esta vacia
        # Si esta fuera de limites, consideramos que esta "ocupada"
        if not self.esta_dentro_limites(x, y, z):
            return True
        
        # Verificar si hay un cubo en esa posicion
        return self.matriz[x][y][z] is not None
    
    def puede_colocar_pieza(self, pieza):
        """ Verifica si una pieza puede colocarse en su posicion actual.
            Una pieza NO puede colocarse si:
            1. Alguno de sus cubos esta fuera del tablero
            2. Alguno de sus cubos colisiona con un cubo ya fijo """
        
        # Obtener todas las posiciones absolutas de la pieza
        posiciones = pieza.obtener_posiciones_absolutas()
        # Verificar cada cubo de la pieza
        for x, y, z in posiciones:
            # Si esta fuera de limites o ocupada, no puede colocarse
            if self.esta_ocupada(x, y, z):
                return False
        # Si todas las posiciones son validas, puede colocarse
        return True
    
    def fijar_pieza(self, pieza): 
        #Fija una pieza en el tablero, cuando ya no puede ir hacia mas hacia abajo.        
        #Esto pasa cuando la pieza toca el suelo o colisiona con otra pieza fija.
        posiciones = pieza.obtener_posiciones_absolutas()
        # Agregar cada cubo de la pieza al tablero
        for x, y, z in posiciones:
            # Solo fijar si esta dentro de limites
            if self.esta_dentro_limites(x, y, z):
                self.matriz[x][y][z] = pieza.color
        
        print(f" Pieza {pieza.nombre} fijada en el tablero")
    
    def obtener_cubos_fijos(self):
        #Retorna una lista con todos los cubos fijos del tablero.
        #Retorna: Lista de tuplas: [(x, y, z, (r,g,b)), ...] Cada tupla contiene posicion y color del cubo
        
        cubos = []
        # Recorrer toda la matriz
        for x in range(self.ancho):
            for y in range(self.alto):
                for z in range(self.profundidad):
                    color = self.matriz[x][y][z]
                    
                    # Si hay un cubo en esta posicion
                    if color is not None:
                        cubos.append((x, y, z, color))    
        return cubos
    
    def contar_cubos_fijos(self):
        #Cuenta el numero de cubos fijos en el tablero.
        return len(self.obtener_cubos_fijos())
    
    def limpiar(self):
        #Limpia todo el tablero (elimina todos los cubos fijos).
        self.matriz = [
            [
                [None for z in range(self.profundidad)]
                for y in range(self.alto)
            ]
            for x in range(self.ancho)
        ]
        print("Tablero limpiado")
    
    def verificar_planos_completos(self):
        """ Verifica que todos los planos horizontales (Y) estan completamente llenos.
            Un plano Y esta completo si TODAS las posiciones (x, z) estan ocupadas.
            En un tablero 10x10, eso significa 100 cubos en ese nivel Y.
            Devuelve una lista con los indices Y de los planos completos
            [0, 1, 5]  # Los planos Y=0, Y=1 y Y=5 estan completos """
        planos_completos = []
        # Revisar cada nivel Y de abajo hacia arriba
        for y in range(self.alto):
            plano_lleno = True
            # Verificar cada posicion (x, z) en este nivel Y
            for x in range(self.ancho):
                for z in range(self.profundidad):
                    # Si hay aunque sea UNA posicion vacia, no esta completo
                    if self.matriz[x][y][z] is None:
                        plano_lleno = False
                        break
                
                if not plano_lleno:
                    break
            
            # Si el plano esta completamente lleno, agregarlo a la lista
            if plano_lleno:
                planos_completos.append(y)
        
        return planos_completos
    
    def eliminar_plano(self, y_plano):
        """
        Elimina Plano el prroceso es:
            1. Eliminar todos los cubos del plano Y=y_plano
            2. Bajar todos los planos superiores (Y > y_plano) una posicion
            3. El plano superior queda vacio
            
        Parametros:
            y_plano: Indice Y del plano a eliminar (0 = piso, 19 = techo) """
        # Bajar todos los planos superiores
        for y in range(y_plano, self.alto - 1):
            for x in range(self.ancho):
                for z in range(self.profundidad):
                    # Copiar el cubo del plano de arriba
                    self.matriz[x][y][z] = self.matriz[x][y + 1][z]
        
        # El plano superior queda vacio
        for x in range(self.ancho):
            for z in range(self.profundidad):
                self.matriz[x][self.alto - 1][z] = None
        
        print(f" Plano Y={y_plano} eliminado")
    
    def eliminar_planos_completos(self):
        #Detecta y elimina TODOS los planos completados.
        #Los planos eliminamos de abajo hacia arriba para evitar problemas con los indices al bajar cubos """
        planos = self.verificar_planos_completos()
        if not planos:
            return 0  # No hay planos completos
        # (los indices no cambian mientras eliminamos)
        for y_plano in sorted(planos):
            self.eliminar_plano(y_plano)
        num_planos = len(planos)
        print(f" {num_planos} plano(s) eliminado(s)")
        return num_planos
        
    def __str__(self):
        cubos = self.contar_cubos_fijos()
        return f"Tablero: {self.ancho}x{self.alto}x{self.profundidad} con {cubos} cubos fijos"


if __name__ == "__main__":
    # Pruebas basicas del modulo tablero.py
    # Crear tablero
    print("Creando tablero:")
    tablero = Tablero(10, 20, 10)
    print(f"  {tablero}")
    
    # Probar limites
    print("Probando deteccion de limites:")
    print(f" (5, 10, 5) esta dentro: {tablero.esta_dentro_limites(5, 10, 5)}")
    print(f" (-1, 10, 5) esta dentro: {tablero.esta_dentro_limites(-1, 10, 5)}")
    print(f" (5, 25, 5) esta dentro: {tablero.esta_dentro_limites(5, 25, 5)}")
    print(f" (15, 10, 5) esta dentro: {tablero.esta_dentro_limites(15, 10, 5)}")
    print("")
    
    # Probar ocupacion
    print("Probando deteccion de ocupacion:")
    print(f" (5, 10, 5) esta ocupada: {tablero.esta_ocupada(5, 10, 5)}")
    
    # Agregar un cubo manualmente
    tablero.matriz[5][10][5] = (1.0, 0.0, 0.0)  # Cubo rojo
    print(f"  Agregamos cubo rojo en (5, 10, 5)")
    print(f"  (5, 10, 5) esta ocupada: {tablero.esta_ocupada(5, 10, 5)}")
    print("")
    
    # Probar con una pieza, importar piezas.py
    try:
        import piezas
        
        print("Probando colisiones con piezas:")
        print("")
        
        # Crear pieza en posicion valida (arriba, centro)
        pieza1 = piezas.Pieza('I', (4, 18, 4))
        print(f"  {pieza1}")
        print(f"  Se puede colocar: {tablero.puede_colocar_pieza(pieza1)}")
        print("")
        
        # Crear pieza que colisiona con el cubo rojo
        pieza2 = piezas.Pieza('O', (5, 10, 5))
        print(f"  {pieza2}")
        print(f"  Se uede colocar? : {tablero.puede_colocar_pieza(pieza2)}")
        print(f"  No puede colocarse porque colisiona con cubo fijo en (5,10,5)")
        print("")
        
        # Fijar la pieza1 en el tablero
        print("Fijando pieza en el tablero:")
        tablero.fijar_pieza(pieza1)
        print(f"  {tablero}")
        print("")
        
        # Mostrar cubos fijos
        print("Cubos fijos en el tablero:")
        cubos = tablero.obtener_cubos_fijos()
        for i, (x, y, z, color) in enumerate(cubos, 1):
            print(f"  {i}. Posicion ({x}, {y}, {z}) - Color RGB{color}")
        
    except ImportError:
        print("No se pudo importar modulo 'piezas'")
    print("Modulo de tablero funcionando correctamente")