#!/usr/bin/env python3

import curses


def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    curses.echo()

    alto, ancho = stdscr.getmaxyx()

    # Dividir la pantalla en tres partes
    pntll_01 = curses.newwin(alto - 2, ancho, 0       , 0)
    barra_00 = curses.newwin(1       , ancho, alto - 2, 0)
    pntll_02 = curses.newwin(1       , ancho, alto - 1, 0)


    pntll_01.clear()

    # Colorear la barra_00 que separa las dos partes
    barra_00.bkgd(' ', curses.color_pair(1))
    barra_00.refresh()

    # Mostrar el prompt en la parte de abajo
    pntll_02.clear()
    pntll_02.addstr(0, 0, '> ')
    pntll_02.refresh()

    c = ''
    while True:
        c = pntll_02.getch()

        if c == 9:  # Tabulador
            text = pntll_02.instr(0, 2).decode('utf-8')
            pntll_01.addstr(text + "\n")
            pntll_01.refresh()
            pntll_02.clear()
            pntll_02.addstr(0, 0, '> ')
            pntll_02.refresh()
        elif c == 17:  # Ctrl + q
            break
        else:
            pntll_02.refresh()

stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()

curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)

curses.wrapper(main)
