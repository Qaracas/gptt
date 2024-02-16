#!/usr/bin/env python3
import curses
import sys

def pinta_en(pantalla, texto):
    """
    Pinta en una pantalla
    """
    pantalla.addstr(texto + "\n")
    pantalla.refresh()

def edita_pregunta_en(pantalla, carácter, y, x):
    """
    Edita el texto en la zona de la preguna
    """
    _x = x

    # Texto a la derecha del cursor
    txt_drcha = pantalla.instr(y, x).decode('utf-8')

    pantalla.addch(y, _x, carácter)
    # Avanza el cursor
    _x = min(_x + 1, curses.COLS - 1)
    if txt_drcha.strip():
        try:
            pantalla.addstr(y, _x, txt_drcha)
        except curses.error as e:
            pass # Error, pero addstr hace lo que debe ¿?
    return _x

def redimensiona(terminal, pantallas):
    """
    Redimensiona el interfaz de usuario. Se llama recibir la tecla especial de
    KEY_RESIZE
    """
    # Obten las nuevas dimensiones del terminal
    y, x = terminal.getmaxyx()

    pantallas["franja_título"].resize(1    , x)
    pantallas["zona_respuest"].resize(y - 3, x)
    pantallas["franja_estado"].resize(1    , x)
    pantallas["zona_pregunta"].resize(1    , x)

    pantallas["franja_título"].mvwin(0, 0)
    pantallas["zona_respuest"].mvwin(1, 0)
    pantallas["franja_estado"].mvwin(y - 2, 0)
    pantallas["zona_pregunta"].mvwin(y - 1, 0)

    # Refresca
    for i in pantallas:
        pantallas[i].refresh()

def crea_panel_de_pantallas(terminal, pantallas, indicador):
    """
    Crea el interfaz de usuario
    """
    terminal.clear()
    terminal.refresh()

    # y, x - Obten tamaño del terminal
    alto, ancho = terminal.getmaxyx()

    # Divide la pantalla en tres partes
    pantallas["franja_título"] = curses.newwin(1       , ancho, 0       , 0)
    pantallas["zona_respuest"] = curses.newwin(alto - 3, ancho, 1       , 0)
    pantallas["franja_estado"] = curses.newwin(1       , ancho, alto - 2, 0)
    pantallas["zona_pregunta"] = curses.newwin(1       , ancho, alto - 1, 0)

    ## Borrar ##
    #pantallas["zona_respuest"].scrollok(True)
    ## Borrar ##

    # Limpia las pantallas
    for i in pantallas:
        pantallas[i].clear()

    # Colorea la barras de título y modo
    pantallas["franja_título"].bkgd(' ', curses.color_pair(1))
    pantallas["franja_estado"].bkgd(' ', curses.color_pair(1))

    # Espacio para escribir
    pantallas["zona_pregunta"].addstr(0, 0, indicador)
    
    # Refresca
    for i in pantallas:
        pantallas[i].refresh()

def main(terminal):
    """
    Recubrimiento principal
    """

    ## Borrar ##
    with open('texto_ventana.txt', 'r') as fichero:
        # Lee el contenido del fichero
        texto = fichero.read()
    ## Borrar ##

    indicador = '> '
    p = {}
    crea_panel_de_pantallas(terminal, p, indicador)

    p["zona_pregunta"].keypad(True)
    curses.curs_set(1)  # Muestra el cursor
    y, x = 0, 2         # Posición inicial del cursor

    ## Borrar ##
    # Variables para el desplazamiento vertical.
    dv = 0
    h, w = p["zona_respuest"].getmaxyx()
    ## Borrar ##

    while True:

        ## Borrar ##
        p["zona_respuest"].clear()
        for i, linea in enumerate(texto.split('\n')[dv:dv+h]):
            p["zona_respuest"].addstr(i, 0, linea)
        p["zona_respuest"].refresh()
        ## Borrar ##

        c = p["zona_pregunta"].getch()

        # Texto mostrado en la zona de pregunta
        txt_prgnt = p["zona_pregunta"].instr(0, len(indicador)).decode('utf-8')
        txt_prgnt = txt_prgnt.strip()

        if c == curses.KEY_RESIZE:
            redimensiona(terminal, p)
        elif c == 4:       # Ctrl + D
            break;
        elif c == 9:     # Tabulador
            # Pintar pregunta
            # pinta_en(p["zona_respuest"], txt_prgnt)
            # Enviar solicitud a la IA
            # Pintar respuesta
            p["zona_pregunta"].clear()
            p["zona_pregunta"].addstr(0, 0, indicador)
            p["zona_pregunta"].refresh()
            y, x = 0, 2
            p["zona_pregunta"].move(y, x)
        ## Borrar ##
        elif c == curses.KEY_UP:
            dv = max(0, dv - 1)
        elif c == curses.KEY_DOWN:
            dv = min(len(texto) - h, dv + 1)
        ## Borrar ##
        elif c == curses.KEY_LEFT:
            x = max(x - 1, len(indicador))
        elif c == curses.KEY_RIGHT:
            x = min(x + 1, len(txt_prgnt) + len(indicador), curses.COLS - 1)
        elif (   c == curses.KEY_BACKSPACE
              or c == 127):
            if x > len(indicador):
                p["zona_pregunta"].delch(y, x - 1)
            x = max(x - 1, len(indicador))
        elif c >= 32 and c <= 126: ## Muestra en la ventana si es imprimible ##
            x = edita_pregunta_en(p["zona_pregunta"], c, y, x)
        elif c >= 127 and c <= 255:
            d = p["zona_pregunta"].getch()
            b = bytes([c, d]).decode('utf-8')
            x = edita_pregunta_en(p["zona_pregunta"], b, y, x)

        # Mueve el cursor a la posición actual
        p["zona_pregunta"].move(y, x)
        p["zona_pregunta"].refresh()

    curses.nocbreak()
    terminal.keypad(False)
    curses.echo()
    curses.endwin()

# Ejecutar el programa
if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)

    curses.wrapper(main)

    sys.exit(0)
