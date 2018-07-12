#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_map.py read <romfile> <index>

Try and extract map data.

Arguments
    <romfile>   The rom file to open
    <index>     The index of the map

"""
from math import floor
from docopt import docopt
import os

rom = None

PALETTES_VALUES = {
    b'\x00': 'Jungle dungeon',
    b'\x01': 'Cave with tracks',
    b'\x02': 'Endgame tower',
    b'\x03': 'Town',
    b'\x04': 'Boat',
    b'\x05': 'City',
}


def find_map_data_pointer(index):
    rom.seek(0xD * 0x4000 + 2 * index)
    pointer = int.from_bytes(rom.read(2), byteorder='little')
    return pointer


def read_map_data_header(pointer, bank=0xD):
    header = {}
    rom.seek(bank * 0x4000 + pointer - 0x4000)
    header['width'] = int.from_bytes(rom.read(1), byteorder='little')
    header['height'] = int.from_bytes(rom.read(1), byteorder='little')
    header['out_of_bounds_tile'] = int.from_bytes(
        rom.read(1), byteorder='little')
    header['palette_index'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_1'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_2'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_3'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_4'] = int.from_bytes(rom.read(1), byteorder='little')
    header['items_in_bank_5'] = int.from_bytes(rom.read(2), byteorder='little')
    return header


def swap_byte(b):
    return (((b << 4) & 0xF0) | ((b >> 4) & 0x0F))


def hl_from_bytes(low, high):
    return high << 8 | low


def pointer_from_position(pos, bank):
    return pos - 0x4000 * (bank - 1)


def bytes_from_pointer(pointer):
    return ((pointer & 0xFF00) >> 8, pointer & 0x00FF)


def seek_to_pointer(pointer, bank):
    rom.seek(pointer + (bank - 1) * 0x4000)


def read_bytes(n=1):
    return int.from_bytes(rom.read(n), byteorder='little')


def read_map(index):
    map_data = {}
    map_data_pointer = find_map_data_pointer(index)
    map_data['header'] = read_map_data_header(map_data_pointer)

    # Position in the rom is now 10 bytes after the header
    C2A1 = read_bytes(1)
    C2A2 = read_bytes(1)

    # --- Load_Map (0D:4100)
    FFBB = read_bytes(1)
    FFBC = read_bytes(1)

    # This is supposed to be FFB2 & FFB1
    HL_ram = rom.tell()

    rom.seek(8, os.SEEK_CUR)

    reading = True
    map_data['decoded'] = []

    hl_read = rom.tell()

    c = 0
    while reading:
        # --- Start_Decompressing_Next_Map_Byte (0D:4119)
        rom.seek(hl_read)
        byte_a = read_bytes(1)
        hl_read = rom.tell()

        added = ""

        b_counter = 8

        while b_counter > 0:

            new_a = (byte_a * 2) & 0xFF
            if byte_a * 2 > 0xFF:
                byte_a = new_a
                c += 1
            else:
                byte_a = new_a
                HL_ram4126 = rom.tell()
                rom.seek(HL_ram + (c >> 1))
                a = read_bytes(1)
                if c & 0x01 == 0x00:
                    a = swap_byte(a)

                # --- jr_00d_413d
                a = a & 0x0F

                if FFBB & 0x01 == 0:
                    map_data['decoded'].append(a)
                else:
                    # --- 0d:4146
                    previous_a = map_data['decoded'][-1]
                    a = swap_byte(previous_a) | a
                    map_data['decoded'][-1] = a
                    added += format(a, 'x') + " "

                # --- jr_00d_4154
                if FFBB > 0:
                    FFBB -= 1
                else:
                    FFBB = 0xFF
                    FFBC -= 1
                if FFBB | FFBC == 0:
                    reading = False
                else:
                    c = 0
                rom.seek(HL_ram4126)
            b_counter -= 1

        # print(added)
    return map_data


def prettify_line(line):
    equivalence = {
        '56': '[]',
        '1': '.',
        'b': ' ',
        '8': ' ',
        '2': ' ',
        '9': ' ',
        'a': ' ',
        '4': '-',
        '6': '|',
        '5': 'o',
        '7': 'o',
        '3': 'o',
        'f': 'T',
    }
    for key in equivalence:
        line = line.replace(key, equivalence[key])

    return line


def print_ascii_map(map_data):
    w = map_data['header']['width']
    h = map_data['header']['height']

    for row in range(h):
        line = ""
        for col in range(int(w / 2)):
            line += format(map_data['decoded'][col + row * w // 2], '02x')
        print(prettify_line(line))
        #print(line)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    index = int(arguments["<index>"])

    if arguments['read']:
        # Example offset : 0xD90F
        if index != 999:
            index = [index]
        else:
            index = range(16 * 8)

        for i in index:
            try:
                map_data = read_map(i)
                #print(map_data)
                print_ascii_map(map_data)
                print("\n\n")
            except:
                pass