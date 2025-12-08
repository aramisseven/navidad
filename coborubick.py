import copy
import random
import sys

# --- 1. Definiciones de Colores y Estructura ---

# La representación de color en el terminal para una mejor visualización
COLORES_ANSI = {
    'W': '\033[47m  \033[0m',  # Blanco
    'Y': '\033[43m  \033[0m',  # Amarillo
    'R': '\033[41m  \033[0m',  # Rojo
    'O': '\033[48;5;208m  \033[0m', # Naranja (cercano)
    'G': '\033[42m  \033[0m',  # Verde
    'B': '\033[44m  \033[0m',  # Azul
    'X': '  ',                 # Espacio vacío (para el diseño)
}

# La estructura inicial del cubo resuelto (6 caras de 3x3)
ESTADO_RESUELTO = {
    'U': [['W'] * 3 for _ in range(3)], # Arriba (Up)
    'D': [['Y'] * 3 for _ in range(3)], # Abajo (Down)
    'F': [['R'] * 3 for _ in range(3)], # Frente (Front)
    'B': [['O'] * 3 for _ in range(3)], # Detrás (Back)
    'L': [['G'] * 3 for _ in range(3)], # Izquierda (Left)
    'R': [['B'] * 3 for _ in range(3)], # Derecha (Right)
}

# --- 2. Patrón MEMENTO (EstadoGuardado) ---

class EstadoGuardado:
    """
    Clase Memento. Guarda el estado interno del cubo (la configuración de colores).
    """
    def __init__(self, estado):
        # Usamos deepcopy para asegurarnos de guardar una COPIA completa y no una referencia.
        self._estado = copy.deepcopy(estado)

    def obtener_estado(self):
        """Devuelve el estado guardado."""
        return self._estado

# --- 3. Clase Caretaker (Historial) ---

class Historial:
    """
    Clase Caretaker. Gestiona el historial de estados guardados (la pila de "undo").
    """
    def __init__(self):
        self._pila_mementos = []

    def guardar_estado(self, memento):
        """Añade un nuevo estado a la pila."""
        self._pila_mementos.append(memento)

    def deshacer(self):
        """
        Retorna el estado anterior y lo elimina de la pila.
        Si la pila está vacía (solo queda el estado inicial), no hace nada.
        """
        if len(self._pila_mementos) > 1:
            # Elimina el estado actual
            self._pila_mementos.pop()
            # Retorna el estado anterior (que ahora es el tope de la pila)
            return self._pila_mementos[-1]
        
        # Si solo queda el estado inicial, devuelve ese mismo estado
        return self._pila_mementos[0] if self._pila_mementos else None

# --- 4. Clase Originator (CuboRubik) ---

class CuboRubik:
    """
    Clase Originator. Contiene el estado actual del cubo y define las operaciones (movimientos).
    """
    def __init__(self):
        # Inicializa el cubo en estado resuelto
        self.estado = copy.deepcopy(ESTADO_RESUELTO)
        self.historial = Historial()
        # Guarda el estado inicial como primer memento
        self.historial.guardar_estado(self.crear_memento())

    def crear_memento(self):
        """Crea un objeto Memento con el estado actual."""
        return EstadoGuardado(self.estado)

    def restaurar_memento(self, memento):
        """Restaura el estado interno a partir del Memento."""
        if memento:
            self.estado = copy.deepcopy(memento.obtener_estado())
            # La restauración ya se maneja en el método deshacer del Historial
            return True
        return False

    def rotar_cara(self, cara):
        """Gira una cara 90 grados en el sentido de las agujas del reloj."""
        
        # Transposición de la matriz
        matriz = self.estado[cara]
        matriz = [list(fila) for fila in zip(*matriz)]
        
        # Inversión de las filas para giro CW
        matriz = [fila[::-1] for fila in matriz]
        self.estado[cara] = matriz

    def _ejecutar_movimiento_derecha(self, prima=False):
        """Simula una rotación de la cara Derecha (R o R')."""
        
        # R (Clockwise - CW) o R' (Counter-Clockwise - CCW)
        veces = 1 if not prima else 3 # 3 giros CW = 1 giro CCW

        for _ in range(veces):
            # 1. Rotar la cara Derecha (R)
            self.rotar_cara('R')
            
            # 2. Rotar las 4 aristas adyacentes: U -> F -> D -> B -> U
            temp_col = [self.estado['U'][i][2] for i in range(3)] # Columna derecha de U
            
            # F (columna 2) -> U (columna 2)
            for i in range(3):
                self.estado['U'][i][2] = self.estado['F'][i][2]
                
            # D (columna 2) -> F (columna 2)
            for i in range(3):
                self.estado['F'][i][2] = self.estado['D'][i][2]
                
            # B (columna 0, invertida) -> D (columna 2)
            for i in range(3):
                self.estado['D'][i][2] = self.estado['B'][2 - i][0]
                
            # U (temp) -> B (columna 0, invertida)
            for i in range(3):
                self.estado['B'][2 - i][0] = temp_col[i]
            
            # Nota: Esto es complejo y propenso a errores, pero suficiente para la demostración.

    def mover(self, comando):
        """Ejecuta un movimiento y guarda el estado."""
        
        movimiento_valido = False
        
        if comando == 'R':
            self._ejecutar_movimiento_derecha(prima=False)
            movimiento_valido = True
        elif comando == "R'":
            self._ejecutar_movimiento_derecha(prima=True)
            movimiento_valido = True
        elif comando == 'S': # Comando de Barajar (Shuffle)
            self.barajar()
            movimiento_valido = True
            print("Cubo barajado.")

        if movimiento_valido:
            # Creamos y guardamos un nuevo punto de restauración
            self.historial.guardar_estado(self.crear_memento())
            return True
        return False

    def barajar(self, movimientos=10):
        """Baraja el cubo aplicando movimientos aleatorios."""
        movimientos_disponibles = ['R', "R'"]
        
        for _ in range(movimientos):
            mov = random.choice(movimientos_disponibles)
            self.mover(mov)
        
        # Tras barajar, el historial ya está actualizado por self.mover()

    def deshacer(self):
        """Restaura el cubo al estado anterior usando el Historial."""
        memento_anterior = self.historial.deshacer()
        if memento_anterior:
            self.restaurar_memento(memento_anterior)
            print("Movimiento deshecho. Volviendo al estado anterior.")
            return True
        else:
            print("No hay más movimientos que deshacer (estás en el estado inicial).")
            return False

    def esta_resuelto(self):
        """Comprueba si el cubo está en el estado resuelto."""
        for cara in self.estado:
            # Comprueba si todos los colores en la cara son el mismo
            primer_color = self.estado[cara][0][0]
            for fila in self.estado[cara]:
                for color in fila:
                    if color != primer_color:
                        return False
        return True

    def mostrar_cubo(self):
        """Dibuja el cubo en la consola utilizando una vista 2D (la cruz)."""
        
        # Función auxiliar para pintar una fila de un bloque 3x3
        def pintar_fila(cara, fila):
            return ''.join(COLORES_ANSI[c] for c in self.estado[cara][fila])

        print("\n" + "="*40)
        print("         VISTA DEL CUBO (U/L/F/R/B/D)         ")
        print("="*40)

        # 1. Cara Superior (U)
        print("           Cara U")
        for i in range(3):
            print(f"       {COLORES_ANSI['X']*3} {pintar_fila('U', i)} {COLORES_ANSI['X']*3}")

        # 2. Caras Laterales (L, F, R, B - Fila central)
        print("\n   Cara L   Cara F   Cara R   Cara B")
        for i in range(3):
            fila_L = pintar_fila('L', i)
            fila_F = pintar_fila('F', i)
            fila_R = pintar_fila('R', i)
            fila_B = pintar_fila('B', i)
            print(f"   {fila_L} {fila_F} {fila_R} {fila_B}")

        # 3. Cara Inferior (D)
        print("\n           Cara D")
        for i in range(3):
            print(f"       {COLORES_ANSI['X']*3} {pintar_fila('D', i)} {COLORES_ANSI['X']*3}")
        
        print("\n" + "="*40)


# --- 5. Lógica del Juego en Consola ---

def juego_rubik():
    """Bucle principal del juego en consola."""
    
    cubo = CuboRubik()

    print("--- 🎲 Bienvenido al Cubo de Rubik Console Edition 🎲 ---")
    print("El concepto de 'punto de restauración' se usa para Deshacer (U).")
    
    cubo.mostrar_cubo()
    
    # Barajar automáticamente para empezar a jugar
    cubo.barajar(movimientos=15)
    cubo.mostrar_cubo()
    
    while True:
        if cubo.esta_resuelto():
            print("\n¡FELICIDADES! ¡Cubo Resuelto! 🥳")
            break
        
        print("\nMovimientos disponibles:")
        print(" R: Girar cara Derecha (Clockwise)")
        print(" R': Girar cara Derecha Inverso (Counter-Clockwise)")
        print(" S: Barajar (Shuffle)")
        print(" U: Deshacer (Undo) - Vuelve al estado anterior. (El Memento en acción)")
        print(" Q: Salir")
        
        entrada = input("Tu movimiento (R, R', S, U, Q): ").upper().strip()

        if entrada == 'Q':
            print("Saliendo del juego. ¡Adiós!")
            sys.exit()
        elif entrada == 'U':
            # Se llama a la función Deshacer que utiliza la clase Historial (Caretaker)
            cubo.deshacer()
        elif entrada in ['R', "R'"]:
            if not cubo.mover(entrada):
                print(f"Error: Movimiento '{entrada}' no reconocido o inválido.")
        elif entrada == 'S':
            cubo.mover(entrada)
        else:
            print("Entrada no válida. Por favor, usa R, R', S, U o Q.")
        
        cubo.mostrar_cubo()

if __name__ == "__main__":
    juego_rubik()