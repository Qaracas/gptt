#!/usr/bin/env python3
import config
import curses
import locale
import sys
import srv.ia.controlador

#
# Funciones básicas
################################################################################

def octetos(val):
    return bytes([val >> i & 0xff
                  for i in range(0, val.bit_length(), 8)])

#
# Variables globales
################################################################################

versión = "1.0"

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
    if curses.has_colors() and curses.can_change_color():
        ventanas["franja_título"].bkgd(' ', curses.color_pair(1))
        ventanas["franja_estado"].bkgd(' ', curses.color_pair(1))

    ventanas["franja_título"].addstr(0, 1, "Gptt v" + versión, curses.color_pair(2))

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

    def __init__(mi, vntn, y = 0, x = 0, indc = "> "):
        mi.ventana         = vntn
        mi.indicador       = indc
        mi.cursor_y        = y
        mi.cursor_x        = 0
        mi.txt_total       = ""
        mi.puntero_txt     = 0
        mi.desp_x          = 0
        mi.desp_y          = 0
        mi.alto, mi.ancho  = mi.ventana.getmaxyx()
        mi.bloqueada       = False

        # Posición del cursor
        if x > 0:
            mi.cursor_x = x
        else:
            mi.cursor_x = len(indc)

        mi.ventana.addstr(0, 0, mi.indicador)
        mi.ventana.keypad(True)
        mi.ventana.nodelay(False)

    def redimensiona(mi):
        """
        Actualiza dimensiones de la caja
        """
        # Nueva dimensión de la pantalla
        mi.alto, mi.ancho = mi.ventana.getmaxyx()

        # Bloqua caja si ventana es pequeña
        if mi.ancho < mi.SALTO + len(mi.indicador):
            mi.bloqueada = True
        else:
            mi.bloqueada = False

        # Eje x: Recoloca cursor
        if mi.cursor_x > mi.ancho:
            resta_x =  mi.cursor_x - mi.ancho

            mi.cursor_x -= resta_x
            mi.puntero_txt -= resta_x

        # Eje x: Redibuja texto a partir del cursor
        try:
            mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                mi.txt_total[mi.puntero_txt:
                    mi.puntero_txt + (mi.ancho - mi.cursor_x)])
        except curses.error:
            pass

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

        try:
            mi.ventana.move(y, x)
        except curses.error:
            pass

    def suma_x(mi, cantidad):
        """
        Suma 'cantidad' a la posición x del cursor y al índice del texto
        """
        # Si la caja está bloqueada no se actúa
        if mi.bloqueada:
            return

        # Si la ventana está desbordada
        if (    mi.cursor_x == (mi.ancho - 1)
            and len(mi.txt_total) > (mi.ancho - len(mi.indicador) - 1)):
            # Desplaza texto alante
            mi.reinicia()
            mi.desp_x += mi.SALTO

            # Repinta texto
            try:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                    mi.txt_total[mi.desp_x:
                        mi.desp_x + (mi.ancho - len(mi.indicador))])
            except curses.error:
                pass

            # Mueve cursor
            mi.mcursor(0, mi.ancho - mi.SALTO - 1)

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
        # Si la caja está bloqueada no se actúa
        if mi.bloqueada:
            return

        # Si la ventana está desbordada
        if (    mi.cursor_x == len(mi.indicador)
            and mi.desp_x > 0):
            # Desplaza texto atrás
            mi.reinicia()
            mi.desp_x -= mi.SALTO

            # Repinta texto
            try:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                    mi.txt_total[mi.desp_x:
                        mi.desp_x + (mi.ancho - len(mi.indicador))])
            except curses.error:
                pass

            # Mueve cursor
            mi.mcursor(0, mi.SALTO + len(mi.indicador))

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
        # Si la caja está bloqueada no se actúa
        if mi.bloqueada:
            return

        # Texto memorizado: añade carácter y avanza puntero
        mi.txt_total = mi.__poncar(mi.txt_total, carácter, mi.puntero_txt)
        mi.puntero_txt += 1

        # Texto a la derecha del cursor
        txt_drcha = dec(mi.ventana.instr(mi.cursor_y, mi.cursor_x)).rstrip()

        try:
            # Pinta carácter y avanza el cursor
            mi.ventana.addch(mi.cursor_y, mi.cursor_x, carácter)
            mi.cursor_x = min(mi.cursor_x + 1, mi.ancho - 1)

            # Si hay texto a la derecha del cursor, desplázalo una posición
            if txt_drcha:
                mi.ventana.addstr(mi.cursor_y, mi.cursor_x, txt_drcha)

        except curses.error:
            # Cuando desborda la ventana
            if mi.cursor_x < mi.ancho - 1:
                # Si no es el final de la caja no pasa nada
                pass
            else:
                # Al final de la caja retrocedemos texto un SALTO
                v_cursor_x = mi.cursor_x

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
                    txt_drcha = dec(mi.ventana.instr(mi.cursor_y, mi.cursor_x)).rstrip()
                    mi.mcursor(mi.cursor_y, len(txt_drcha) + len(mi.indicador))
                else:
                    mi.mcursor(mi.cursor_y, v_cursor_x - mi.SALTO + 1)

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
        # Si la caja está bloqueada no se actúa
        if mi.bloqueada:
            return

        # Texto visible
        if mi.cursor_x > len(mi.indicador):
            mi.ventana.delch(mi.cursor_y, mi.cursor_x - 1)
            mi.cursor_x = max(mi.cursor_x - 1, len(mi.indicador))

            # Si la ventana está desbordada
            try:
                if len(mi.txt_total[mi.desp_x:]) > mi.ancho - len(mi.indicador) - 1:
                    mi.ventana.addstr(mi.cursor_y, mi.cursor_x,
                        mi.txt_total[mi.puntero_txt:
                            mi.puntero_txt + (mi.ancho - mi.cursor_x)])
            except curses.error:
                pass
        else:
            if mi.desp_x > 0:
                # Desplaza texto atrás
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
                mi.mcursor(0, mi.SALTO + len(mi.indicador))
                # Borra carácter (recursivo)
                mi.borrcar()
                return

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
        mi.mcursor(0, len(mi.indicador))

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

    # Crear caja pregunta
    caja_pregunta = CajaTxt(v["caja_pregunta"])

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
            break
        elif c == v_tecla["TABULADOR"]:
            # Pintar pregunta en zona_respuest
            pass
            # Enviar solicitud a la IA
            respuesta = srv.ia.controlador.pregunta("opengpts", caja_pregunta.txt_total)
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
        try:
            caja_pregunta.mcursor()
        except curses.error:
            pass

    terminal.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    print (caja_pregunta.txt_total)

# Ejecuta el programa
if __name__ == "__main__":
    stdscr = curses.initscr()

    # Muestra cursor y desactiva eco
    curses.curs_set(1)
    curses.noecho()

    # Configuración general
    config.colores()

    curses.wrapper(inicio)

    print ("Saliendo...")
    sys.exit(0)
