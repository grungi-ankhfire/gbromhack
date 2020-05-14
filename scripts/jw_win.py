#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_win.py compute <x> <y> <width> <height>
          jw_win.py extract <romfile> <start> <end> <tablefile> <outputfile>

Calculate the 6 bytes defining a window geometry for the game
Jungle Wars (GB) or extract them.

Arguments
    <x>         The tile occupied by the left border
    <y>         The tile occupied by the top border
    <width>     The width of the desired window
    <height>    The height of the desired window
"""
import pyaml
import yaml
from docopt import docopt
from translation_table import TranslationTable

# Example invocation
# python jw_win.py extract roms\jw_original.gb 0x333fb 0x33499 ..\tbl\jw-py.tbl jw_wins.yaml

# Example YAML :
# 
# windows:
#   !! int 0x12345:
#     original_header: 0xaabbccddeeff
#     position_x: 0x00
#     position_y: 0x00
#     width: 0x00
#     height: 0x00
#     original_text: ""
#     translation: ""
#     id: 0x00


class HexInt(int):
    def __new__(cls, value, digits=2):
        obj = int.__new__(cls, int(value))
        obj.digits = digits
        return obj

def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, data.digits + 2))


pyaml.add_representer(HexInt, representer)


class JWWindow:

    def __init__(self):
        self.top_left = 0
        self.bottom_right = 0
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.text = ""
        self.id = 0
        self.location = 0
        self.bg_map = 0

    def initialize_from_header(self, header):
        """Header should be 6 bytes, as found in the ROM."""

        self.width = header[0]
        self.height = header[1]
        self.bottom_right = int.from_bytes(header[2:4], "little")
        self.top_left = int.from_bytes(header[4:6], "little")
        self.original_header = int.from_bytes(header, "big")
        if self.top_left >= 0x9C00:
            self.bg_map = 1
        else:
            self.bg_map = 0
        self.x = (self.top_left - (0x9800 + 0x400 * self.bg_map)) % 0x20
        self.y = (self.top_left - (0x9800 + 0x400 * self.bg_map)) // 0x20

    def initialize_from_data(self, width, height, x, y, bg_map=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.bg_map = bg_map
        self.top_left = (0x9800 + 0x400 * self.bg_map) + (y * 0x20) + x
        self.bottom_right = self.top_left + (height - 1) * 0x20 + width - 1

    def recompute_header(self):
        header = bytearray()
        header.append(self.width)
        header.append(self.height)
        header += (self.bottom_right).to_bytes(2, "little")
        header += (self.top_left).to_bytes(2, "little")
        return header

    def to_yaml(self):
        result = {
            "original_header": HexInt(self.original_header, digits=12),
            "bg_map": self.bg_map,
            "pos_x": self.x,
            "pos_y": self.y,
            "dim_x": HexInt(self.width, digits=2),
            "dim_y": HexInt(self.height, digits=2),
            "original_text": self.text,
            "translation": "TODO_" + "{0:#0{1}x}<FF>".format(self.location, 7),
            "location": HexInt(self.location, digits=5)
        }

        return result

    def from_yaml(self, data, id):
        self.initialize_from_data(data["dim_x"],
                                  data["dim_y"],
                                  data["pos_x"],
                                  data["pos_y"],
                                  data["bg_map"])
        self.translation = data["translation"]
        self.id = id


    def __repr__(self):
        return "{:#04x} {:#04x} {:#06x} {:#06x}".format(self.width, self.height, self.bottom_right, self.top_left)


def extract_windows(rom_file, start_offset, end_offset, table):
    rom_file.seek(start_offset)

    # Read the list of pointers to be able to seek directly from them
    pointers = []
    offset = start_offset
    while offset < end_offset:
        pointers.append(int.from_bytes(rom_file.read(2), "little"))
        offset += 2

    result = {}

    win_id = 0
    for pointer in pointers:
        location = (0x0C - 1) * 0x4000 + pointer
        rom_file.seek(location)
        header = rom_file.read(6)

        text = bytearray()
        cur_byte = None
        while cur_byte != b"\xFF":
            cur_byte = rom_file.read(1)
            text += cur_byte

        win = JWWindow()
        win.initialize_from_header(header)
        win.text = table.convert_bytearray(text)
        win.id = win_id
        win.location = location
        win_id += 1
        result[HexInt(win.id, digits=2)] = win.to_yaml()

    return result


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0', options_first=True)

    if arguments["extract"]:

        offset_start = int(arguments["<start>"], 16)
        offset_end = int(arguments["<end>"], 16)

        table = TranslationTable(arguments['<tablefile>'])

        rom = open(arguments["<romfile>"], 'rb+')

        res = {"windows" :extract_windows(rom, offset_start, offset_end, table)}

        rom.close()

        f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
        f.write(pyaml.dump(res, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
        f.close()

    elif arguments["compute"]:

        x = int(arguments["<x>"])
        y = int(arguments["<y>"])
        width = int(arguments["<width>"])
        height = int(arguments["<height>"])

        win = JWWindow()
        header = bytes([0x10, 0x0c, 0x6f, 0x99, 0x00, 0x98])

        win.initialize_from_data(width, height, x, y)
        print(win)
