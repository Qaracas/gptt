#!/usr/bin/env python3
import locale
import curses
import sys

#
# Funciones básicas
################################################################################

def octetos(val):
    return bytes([val >> i & 0xff
                  for i in range(0, val.bit_length(), 8)])

#
# Variables globales
################################################################################

v_codificación = locale.getpreferredencoding()
v_alto  = 0
v_ancho = 0

v_diccionario_teclas = {
    "REDIMENSIONA"     : octetos(curses.KEY_RESIZE),
    "TABULADOR"        : octetos(9),
    "CTRL_D"           : octetos(4),
    "FLECHA_ARRIBA"    : octetos(curses.KEY_UP),
    "FLECHA_ABAJO"     : octetos(curses.KEY_DOWN),
    "FLECHA_DERECHA"   : octetos(curses.KEY_RIGHT),
    "FLECHA_IZQUIERDA" : octetos(curses.KEY_LEFT),
    "RETROCESO_1"      : octetos(curses.KEY_BACKSPACE),
    "RETROCESO_2"      : octetos(127)
}
v_tecla = v_diccionario_teclas

v = {}

#
# Funciones comunes
################################################################################

def cod(mi):
    return mi.encode(v_codificación)

def dec(mi):
    return mi.decode(v_codificación)

def redimensiona(terminal, ventanas):
    """
    Redimensiona el interfaz de usuario. Se llama recibir la tecla especial de
    curses.KEY_RESIZE
    """
    # Obten las nuevas dimensiones del terminal
    v_alto, v_ancho = terminal.getmaxyx()

    ventanas["franja_título"].resize(1         , v_ancho)
    ventanas["zona_respuest"].resize(v_alto - 3, v_ancho)
    ventanas["franja_estado"].resize(1         , v_ancho)
    ventanas["zona_pregunta"].resize(1         , v_ancho)

    ventanas["franja_título"].mvwin(0         , 0)
    ventanas["zona_respuest"].mvwin(1         , 0)
    ventanas["franja_estado"].mvwin(v_alto - 2, 0)
    ventanas["zona_pregunta"].mvwin(v_alto - 1, 0)

    # Refresca
    for i in ventanas:
        ventanas[i].refresh()

def crea_panel_de_ventanas(terminal, ventanas):
    """
    Crea el interfaz de usuario
    """
    terminal.erase()
    terminal.refresh()

    # y, x - Obten tamaño del terminal
    v_alto, v_ancho = terminal.getmaxyx()

    # Divide la pantalla en tres partes
    ventanas["franja_título"] = curses.newwin(1         , v_ancho, 0       , 0)
    ventanas["zona_respuest"] = curses.newwin(v_alto - 3, v_ancho, 1       , 0)
    ventanas["franja_estado"] = curses.newwin(1       , v_ancho, v_alto - 2, 0)
    ventanas["zona_pregunta"] = curses.newwin(1       , v_ancho, v_alto - 1, 0)

    ## Borrar ##
    ventanas["zona_respuest"].scrollok(True)
    ## Borrar ##

    # Limpia las ventanas
    for i in ventanas:
        ventanas[i].erase()

    # Colorea la barras de título y modo
    ventanas["franja_título"].bkgd(' ', curses.color_pair(1))
    ventanas["franja_estado"].bkgd(' ', curses.color_pair(1))

    # Refresca
    for i in ventanas:
        ventanas[i].refresh()

#
# Clases
################################################################################

class Zona_ES:
    """
    Zona de inteacción con el usuario para entrada y salida de texto
    """

    @property
    def SALTO(mi):
        return 20

    def __init__(mi, ventn, y, x, sno = "> "):
        mi.ventana         = ventn
        mi.indicador       = sno
        mi.cursor_y        = y
        mi.cursor_x        = x
        mi.txt_ventn       = ""
        mi.txt_total       = ""
        mi.txt_total_y     = y
        mi.txt_total_x     = x
        mi.puntero_txt     = 0
        mi.desp_x          = 0
        mi.desp_y          = 0
        mi.alto, mi.ancho  = mi.ventana.getmaxyx()

        mi.ventana.addstr(0, 0, mi.indicador)
        mi.ventana.keypad(True)
        mi.ventana.nodelay(False)

    def actualiza_dimensiones(mi):
        """
        Actualiza dimensiones de la zona de e/s
        """
        mi.alto, mi.ancho = mi.patalla.getmaxyx()

    def mcursor(mi, y = None, x = None):
        """
        Mueve el cursor a la posición (y, x) de la zona de e/s
        """
        if y is None:
            y = mi.cursor_y
        else:
            mi.cursor_y = y
        if x is None:
            x = mi.cursor_x
        else:
            mi.cursor_x = x
        mi.ventana.move(y, x)

    def suma_x(mi, cantidad):
        """
        Suma 'cantidad' a la posición x del cursor y al índice del texto
        """

        v["zona_respuest"].erase()
        v["zona_respuest"].addstr(0, 0,
              "Cursor: " + str(mi.cursor_x)
            + "; Pos. texto: " + str(mi.puntero_txt)
            + "; Ancho: " + str(mi.ancho)
            + "; Log. texto: " + str(len(mi.txt_total)))
        v["zona_respuest"].refresh()

        # Si la ventana está desbordada
        if (    mi.cursor_x == (mi.ancho - 1)
            and len(mi.txt_total) > (mi.ancho - len(mi.indicador) - 1)):
            mi.reinicia()
            mi.desp_x += mi.SALTO
            mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                mi.txt_total[mi.desp_x:
                    mi.desp_x + (mi.ancho - len(mi.indicador) - 1)])
            # Desplaza puntero
            mi.puntero_txt = mi.desp_x

        # Texto visible
        mi.txt_ventn = mi.trae_txt_visible()

        # Texto visible: avanza posición del cursor
        mi.cursor_x = min(mi.cursor_x + cantidad,
                    len(mi.txt_ventn) + len(mi.indicador), mi.ancho - 1)

        # Texto memorizado: avanza puntero
        mi.puntero_txt = min(mi.puntero_txt + cantidad, len(mi.txt_total))

    def resta_x(mi, cantidad):
        """
        Resta 'cantidad' a la posición x del cursor y al índice del texto
        """

        v["zona_respuest"].erase()
        v["zona_respuest"].addstr(0, 0,
              "Cursor: " + str(mi.cursor_x)
            + "; Pos. texto: " + str(mi.puntero_txt)
            + "; Ancho: " + str(mi.ancho)
            + "; Log. texto: " + str(len(mi.txt_total)))
        v["zona_respuest"].refresh()

        # Si la ventana está desbordada
        if (    mi.cursor_x == len(mi.indicador)
            and mi.desp_x > 0):
            # Desplazamos texto
            mi.reinicia()
            mi.desp_x -= mi.SALTO
            mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                mi.txt_total[mi.desp_x:
                    mi.desp_x + (mi.ancho - len(mi.indicador) - 1)])
            # Mueve cursor al final del texto
            txt_drcha = dec(mi.ventana.instr(mi.cursor_y,
                mi.cursor_x)).rstrip()
            mi.mcursor(0, len(txt_drcha) + len(mi.indicador))
            # Desplaza puntero
            mi.puntero_txt = mi.desp_x + (mi.ancho - len(mi.indicador) - 1)

        # Texto visible: retrocede posición del cursor
        mi.cursor_x = max(mi.cursor_x - cantidad, len(mi.indicador))

        # Texto memorizado: retrocede puntero
        mi.puntero_txt = max(mi.puntero_txt - cantidad, 0)

    def __poncar(mi, texto, carácter, posición):
        return texto[:posición] + carácter + texto[posición:]

    def poncar(mi, carácter):
        """
        Pon carácter alfanumérico en la zona de e/s
        """

        v["zona_respuest"].erase()
        v["zona_respuest"].addstr(0, 0,
              "Cursor: " + str(mi.cursor_x)
            + "; Pos. texto: " + str(mi.puntero_txt)
            + "; Ancho: " + str(mi.ancho)
            + "; Log. texto: " + str(len(mi.txt_total)))
        v["zona_respuest"].refresh()

        # Texto memorizado: añade carácter y avanza puntero
        mi.txt_total = mi.__poncar(mi.txt_total, carácter, mi.puntero_txt)
        mi.puntero_txt += 1

        # Texto a la derecha del cursor
        txt_drcha = dec(mi.ventana.instr(mi.cursor_y, mi.cursor_x)).rstrip()

        try:
            # Pinta carácter y avanza el cursor
            mi.ventana.addch(mi.cursor_y, mi.cursor_x, carácter)
            mi.cursor_x = min(mi.cursor_x + 1, mi.ancho - 1)

            # Si hay texto a la derecha del cursor se desplaza
            if txt_drcha:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x, txt_drcha)
        except curses.error:
            # Cuando desborda la ventana
            if (   mi.cursor_x >= mi.ancho
                or len(mi.txt_total) > (mi.ancho - len(mi.indicador))):
                pass
            else:
                mi.reinicia()
                mi.desp_x += mi.SALTO
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                    mi.txt_total[mi.desp_x:
                        mi.desp_x + (mi.ancho - len(mi.indicador))])
                txt_drcha = dec(mi.ventana.instr(mi.cursor_y,
                    mi.cursor_x)).rstrip()
                mi.mcursor(0, len(txt_drcha) + len(mi.indicador))

    def __existe_tecla(mi, tecla):
        for clave, valor in v_diccionario_teclas.items():
            if valor == tecla:
                return True
        return False

    def traecar(mi):
        """
        Trae carácter alfanumérico de la zona de e/s
        """
        c1 = mi.ventana.getch()
        car = octetos(c1)

        if (mi.__existe_tecla(car) or c1 < 127):
            return car
        else:
            c2 = mi.ventana.getch()
            car = bytes([c1, c2])

        return car

    def __borrcar(mi, texto, posición):
        return texto[:posición] + texto[posición + 1:]

    def borrcar(mi):
        """
        Borra carácter a la izquierda del cursor y retrocedelo una posición
        """

        # Texto visible
        if mi.cursor_x > len(mi.indicador):
            mi.ventana.delch(mi.cursor_y, mi.cursor_x - 1)
            mi.cursor_x = max(mi.cursor_x - 1, len(mi.indicador))

        # Texto memorizado
        if mi.puntero_txt > 0:
            mi.puntero_txt -= 1
            mi.txt_total = mi.__borrcar(mi.txt_total, mi.puntero_txt)

    def reinicia(mi):
        """
        Borra zona de e/s y pon el cursor al inicio. También borra la copia de
        lo que se ve en la ventana (txt_ventn)
        """
        mi.ventana.erase()
        mi.ventana.addstr(0, 0, mi.indicador)
        mi.ventana.refresh()
        mi.mcursor(0, len(mi.indicador));

    def borra_y_reinicia(mi):
        """
        Borra zona de e/s y pon el cursor al inicio. El borrado incluye el
        texto completo (txt_total), y el que se ve en la ventana (txt_ventn)
        """
        mi.txt_ventn = ""
        mi.txt_total = ""
        mi.reinicia()

    def trae_txt_visible(mi):
        """
        Devuelve el texto visible a partir del indicador
        """
        return dec(mi.ventana.instr(0, len(mi.indicador))).strip()

    def trae_txt_total(mi):
        """
        Devuelve el texto memorizado
        """
        return mi.txt_total

#
# Función principal
################################################################################

def inicio(terminal):
    """
    Recubrimiento principal
    """

    ## Borrar ##
    with open('texto_ventana.txt', 'r') as fichero:
        # Lee el contenido del fichero
        texto = fichero.read()
    ## Borrar ##

#    v = {}
    crea_panel_de_ventanas(terminal, v)

    # Posición inicial del cursor
    zona_pregunta = Zona_ES(v["zona_pregunta"], 0, 2)

    ## Borrar ##
    # Variables para el desplazamiento vertical.
    dv = 0
    h, w = v["zona_respuest"].getmaxyx()
    ## Borrar ##

    while True:
        c = zona_pregunta.traecar()

        if   c == v_tecla["REDIMENSIONA"]:
            redimensiona(terminal, v)
        elif c == v_tecla["CTRL_D"]:
            break;
        elif c == v_tecla["TABULADOR"]:
            # Pintar pregunta en zona_respuest
            pass
            # Enviar solicitud a la IA
            pass
            # Pintar respuesta en zona_respuest
            pass
            # Borrar para realizar otra pregunta
            zona_pregunta.borra_y_reinicia()
        ## Borrar ##
        elif c == v_tecla["FLECHA_ARRIBA"]:
            dv = max(0, dv - 1)
        elif c == v_tecla["FLECHA_ABAJO"]:
            dv = min(len(texto) - h, dv + 1)
        ## Borrar ##
        elif c == v_tecla["FLECHA_IZQUIERDA"]:
            zona_pregunta.resta_x(1)
        elif c == v_tecla["FLECHA_DERECHA"]:
            zona_pregunta.suma_x(1)
        elif (   c == v_tecla["RETROCESO_1"]
              or c == v_tecla["RETROCESO_2"]):
            zona_pregunta.borrcar()
        else: # Pon en la ventana si es un carácter imprimible
            zona_pregunta.poncar(dec(c))

        ## Borrar ##
#        v["zona_respuest"].erase()
#        for i, linea in enumerate(texto.split('\n')[dv:dv+h]):
#            v["zona_respuest"].addstr(i, 0, linea)
#        v["zona_respuest"].refresh()
        ## Borrar ##

        # Mueve el cursor a la posición actual
        zona_pregunta.mcursor()

    terminal.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print (zona_pregunta.txt_total)

# Ejecutar el programa
if __name__ == "__main__":
    stdscr = curses.initscr()

    # Colores por defecto, mostrar el cursor y desactiva eco
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(1)
    curses.noecho()

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)

    curses.wrapper(inicio)

    print ("Saliendo...")
    sys.exit(0)
