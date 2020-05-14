#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_enemy.py extract <romfile> <start> <end> <tablefile> <outputfile>

Extract enemy data for Jungle Wars.

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

# Example invocation :
# 
# python jw_enemy.py extract roms\jw_original.gb 0x30000 0x30085 ..\tbl\jw-py.tbl jw_enemies.yaml


class HexInt(int):
    def __new__(cls, value, digits=2):
        obj = int.__new__(cls, int(value))
        obj.digits = digits
        return obj


def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, data.digits + 2))


pyaml.add_representer(HexInt, representer)


class JWEnemy:

    def __init__(self, id, header, name, location):
        self.id = id
        self.header = header
        self.name = name
        self.location = location

    def to_yaml(self):
        result = {
            "original_header": HexInt(int.from_bytes(self.header, "big"), digits=44),
            "original_name": self.name,
            "id": self.id,
            "translated_name": "TODO" + "{0:#0{1}x}<FF>".format(self.id, 4),
            "location": HexInt(self.location, digits=5)
        }

        return result

    def from_yaml(self, data, id):
        pass


def extract_ennemies(rom_file, start_offset, end_offset, table):
    rom_file.seek(start_offset)

    # Read the list of pointers to be able to seek directly from them
    pointers = []
    offset = start_offset
    while offset < end_offset:
        pointers.append(int.from_bytes(rom_file.read(2), "little"))
        offset += 2

    result = {}

    enemy_id = 0
    for pointer in pointers:
        location = (0x0C - 1) * 0x4000 + pointer
        rom_file.seek(location)
        header = rom_file.read(22)

        text = bytearray()
        cur_byte = None
        while cur_byte != b"\xFF":
            cur_byte = rom_file.read(1)
            text += cur_byte

        enemy = JWEnemy(enemy_id, header, table.convert_bytearray(text), location)

        result[HexInt(enemy_id, digits=2)] = enemy.to_yaml()
        enemy_id += 1

    return result


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0', options_first=True)

    offset_start = int(arguments["<start>"], 16)
    offset_end = int(arguments["<end>"], 16)

    table = TranslationTable(arguments['<tablefile>'])

    rom = open(arguments["<romfile>"], 'rb+')

    res = {"enemies": extract_ennemies(rom, offset_start, offset_end, table)}

    rom.close()

    f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
    f.write(pyaml.dump(res, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
    f.close()
