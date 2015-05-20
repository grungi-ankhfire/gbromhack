#!/usr/bin/python
"""Usage: jw_win.py <x> <y> <width> <height>

Calculate the 6 bytes defining a window geometry for the game
Jungle Wars (GB).

Arguments
    <x>         The tile occupied by the left border
    <y>         The tile occupied by the top border
    <width>     The width of the desired window
    <height>    The height of the desired window
"""
from math import floor
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    x = int(arguments["<x>"])
    y = int(arguments["<y>"])
    width = int(arguments["<width>"])
    height = int(arguments["<height>"])

    byte1 = width
    byte2 = height
    byte3 = (x + width) * 8
    byte4 = (y + height + 1) * 8
    byte5 = 16 + y * 8
    byte6 = 8 + x * 8

    hex_string = ""
    hex_string += "{0:0{1}X} ".format(byte1, 2)
    hex_string += "{0:0{1}X} ".format(byte2, 2)
    hex_string += "{0:0{1}X} ".format(byte3, 2)
    hex_string += "{0:0{1}X} ".format(byte4, 2)
    hex_string += "{0:0{1}X} ".format(byte5, 2)
    hex_string += "{0:0{1}X} ".format(byte6, 2)

    print()
    print(hex_string)
    print()