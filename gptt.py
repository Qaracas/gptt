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
    ventanas["caja_pregunta"].resize(1         , v_ancho)

    ventanas["franja_título"].mvwin(0         , 0)
    ventanas["zona_respuest"].mvwin(1         , 0)
    ventanas["franja_estado"].mvwin(v_alto - 2, 0)
    ventanas["caja_pregunta"].mvwin(v_alto - 1, 0)

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
    ventanas["caja_pregunta"] = curses.newwin(1       , v_ancho, v_alto - 1, 0)

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

class CajaTxt:
    """
    Caja donde se introduce texto
    """

    @property
    def SALTO(mi):
        return 20

    def __init__(mi, ventn, y, x, sno = "> "):
        mi.ventana         = ventn
        mi.indicador       = sno
        mi.cursor_y        = y
        mi.cursor_x        = x
        mi.txt_total       = ""
        mi.puntero_txt     = 0
        mi.desp_x          = 0
        mi.desp_y          = 0
        mi.alto, mi.ancho  = mi.ventana.getmaxyx()

        mi.ventana.addstr(0, 0, mi.indicador)
        mi.ventana.keypad(True)
        mi.ventana.nodelay(False)

    def redimensiona(mi):
        """
        Actualiza dimensiones de la caja
        """
        # Nueva dimensión de la pantalla
        n_alto, n_ancho = mi.ventana.getmaxyx()

        # Eje x: Diferencia
        dif_x = abs(n_ancho - mi.ancho)

        # Eje y: Diferencia
        # inc_y = n_alto - mi.alto

        # Eje x: Recoloca cursor
        if mi.cursor_x > n_ancho:
            resta_x = (dif_x - (mi.ancho - mi.cursor_x)) + 1
            mi.cursor_x -= resta_x
            mi.puntero_txt -= resta_x

        # Eje x: Redibuja texto a partir del cursor
        mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
            mi.txt_total[mi.puntero_txt:
                mi.puntero_txt + (n_ancho - len(mi.indicador) - mi.cursor_x) + 1])

        # Cambia dimensión de la caja
        mi.alto = n_alto
        mi.ancho = n_ancho

    def mcursor(mi, y = None, x = None):
        """
        Mueve el cursor a la posición (y, x) de la caja
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
            + "; Log. texto: " + str(len(mi.txt_total))
            + "; Desplazamiento: " + str(mi.desp_x))
        v["zona_respuest"].refresh()

        # Si la ventana está desbordada
        if (    mi.cursor_x == (mi.ancho - 1)
            and len(mi.txt_total) > (mi.ancho - len(mi.indicador) - 1)):
            # Desplaza texto
            mi.reinicia()
            mi.desp_x += mi.SALTO
            try:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                    mi.txt_total[mi.desp_x:
                        mi.desp_x + (mi.ancho - len(mi.indicador))])
            except curses.error:
                pass
            # Mueve cursor
            mi.mcursor(0, mi.ancho - mi.SALTO - 1)
            # No es necesario ajustar puntero
            # mi.puntero_txt = mi.desp_x

        # Texto visible
        txt_ventn = mi.trae_txt_visible()

        # Texto visible: avanza posición del cursor
        mi.cursor_x = min(mi.cursor_x + cantidad,
                    len(txt_ventn) + len(mi.indicador), mi.ancho - 1)

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
            + "; Log. texto: " + str(len(mi.txt_total))
            + "; Desplazamiento: " + str(mi.desp_x))
        v["zona_respuest"].refresh()

        # Si la ventana está desbordada
        if (    mi.cursor_x == len(mi.indicador)
            and mi.desp_x > 0):
            # Desplaza texto
            mi.reinicia()
            mi.desp_x -= mi.SALTO
            try:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                    mi.txt_total[mi.desp_x:
                        mi.desp_x + (mi.ancho - len(mi.indicador))])
            except curses.error:
                pass
            # Mueve cursor
            mi.mcursor(0, mi.SALTO)
            # Ajusta puntero
            mi.puntero_txt -= 2

        # Texto visible: retrocede posición del cursor
        mi.cursor_x = max(mi.cursor_x - cantidad, len(mi.indicador))

        # Texto memorizado: retrocede puntero
        mi.puntero_txt = max(mi.puntero_txt - cantidad, 0)

    def __poncar(mi, texto, carácter, posición):
        return texto[:posición] + carácter + texto[posición:]

    def poncar(mi, carácter):
        """
        Pon carácter imprimible en la caja
        """

        v["zona_respuest"].erase()
        v["zona_respuest"].addstr(0, 0,
              "Cursor: " + str(mi.cursor_x)
            + "; Pos. texto: " + str(mi.puntero_txt)
            + "; Ancho: " + str(mi.ancho)
            + "; Log. texto: " + str(len(mi.txt_total))
            + "; Desplazamiento: " + str(mi.desp_x))
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
                if mi.cursor_x + len(txt_drcha) > mi.ancho - 1:
                    txt_drcha = txt_drcha[0:len(txt_drcha)]
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x, txt_drcha)

        except curses.error:
            # Cuando desborda la ventana
            if mi.cursor_x < mi.ancho - 1:
                # Si no es el final de la caja no pasa nada
                pass
            else:
                # Al final de la caja retrocedemos texto un SALTO
                v_cursor_x = mi.cursor_x;

                mi.reinicia()
                mi.desp_x += mi.SALTO
                try:
                    mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                        mi.txt_total[mi.desp_x:
                            mi.desp_x + (mi.ancho - len(mi.indicador))])
                except curses.error:
                    pass

                # Coloca cursor en función de si es final de texto
                if mi.puntero_txt == len(mi.txt_total):
                    txt_drcha = dec(mi.ventana.instr(mi.cursor_y,
                        mi.cursor_x)).rstrip()
                    mi.mcursor(0, len(txt_drcha) + len(mi.indicador))
                else:
                    mi.mcursor(0, v_cursor_x - mi.SALTO + 1)

    def __existe_tecla(mi, tecla):
        for clave, valor in v_diccionario_teclas.items():
            if valor == tecla:
                return True
        return False

    def traecar(mi):
        """
        Trae carácter imprimible de la caja
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
        Borra carácter a la izquierda del cursor y retrocede una posición
        """

        # Texto visible
        if mi.cursor_x > len(mi.indicador):
            mi.ventana.delch(mi.cursor_y, mi.cursor_x - 1)
            mi.cursor_x = max(mi.cursor_x - 1, len(mi.indicador))

            # Si la ventana está desbordada
            try:
                if len(mi.txt_total[mi.desp_x:]) > mi.ancho - len(mi.indicador) - 1:
                    mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                        mi.txt_total[mi.puntero_txt:
                            mi.puntero_txt + (mi.ancho - len(mi.indicador) - mi.cursor_x) + 2])
            except curses.error:
                pass
        else:
            if mi.desp_x > 0:
                # Deshaz desplazamiento
                mi.reinicia()
                mi.desp_x -= mi.SALTO
                # Repinta texto
                try:
                    mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                        mi.txt_total[mi.desp_x:
                            mi.desp_x + (mi.ancho - len(mi.indicador))])
                except curses.error:
                    pass
                # Coloca cursor

        # Texto memorizado
        if mi.puntero_txt > 0:
            mi.puntero_txt -= 1
            mi.txt_total = mi.__borrcar(mi.txt_total, mi.puntero_txt)

    def reinicia(mi):
        """
        Borra contenido de la caja y pon el cursor al inicio.
        """
        mi.ventana.erase()
        mi.ventana.addstr(0, 0, mi.indicador)
        mi.ventana.refresh()
        mi.mcursor(0, len(mi.indicador));

    def borra_y_reinicia(mi):
        """
        Borra contenido de la caja y pon el cursor al inicio. También se borra
        el texto que no se ve.
        """
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
    caja_pregunta = CajaTxt(v["caja_pregunta"], 0, 2)

    ## Borrar ##
    # Variables para el desplazamiento vertical.
    dv = 0
    h, w = v["zona_respuest"].getmaxyx()
    ## Borrar ##

    while True:
        c = caja_pregunta.traecar()

        if   c == v_tecla["REDIMENSIONA"]:
            redimensiona(terminal, v)
            caja_pregunta.redimensiona()
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
            caja_pregunta.borra_y_reinicia()
        ## Borrar ##
        elif c == v_tecla["FLECHA_ARRIBA"]:
            dv = max(0, dv - 1)
        elif c == v_tecla["FLECHA_ABAJO"]:
            dv = min(len(texto) - h, dv + 1)
        ## Borrar ##
        elif c == v_tecla["FLECHA_IZQUIERDA"]:
            caja_pregunta.resta_x(1)
        elif c == v_tecla["FLECHA_DERECHA"]:
            caja_pregunta.suma_x(1)
        elif (   c == v_tecla["RETROCESO_1"]
              or c == v_tecla["RETROCESO_2"]):
            caja_pregunta.borrcar()
        else: # Pon en la ventana si es un carácter imprimible
            caja_pregunta.poncar(dec(c))

        ## Borrar ##
#        v["zona_respuest"].erase()
#        for i, linea in enumerate(texto.split('\n')[dv:dv+h]):
#            v["zona_respuest"].addstr(i, 0, linea)
#        v["zona_respuest"].refresh()
        ## Borrar ##

        # Mueve el cursor a la posición actual
        caja_pregunta.mcursor()

    terminal.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print (caja_pregunta.txt_total)

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
