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
    header['out_of_bounds_tile'] = int.from_bytes(rom.read(1), byteorder='little')
    header['palette_index'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_1'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_2'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_3'] = int.from_bytes(rom.read(1), byteorder='little')
    header['unknown_4'] = int.from_bytes(rom.read(1), byteorder='little')
    header['items_in_bank_5'] = int.from_bytes(rom.read(2), byteorder='little')
    return header


def swap_byte(b):
    return (((b << 4) & 0xF0) |
            ((b >> 4) & 0x0F))


def read_map(index):
    map_data = {}
    map_data_pointer = find_map_data_pointer(index)
    # print(hex(map_data_pointer))
    map_data['header'] = read_map_data_header(map_data_pointer)

    # Position in the rom is now 10 bytes after the header
    C2A1 = int.from_bytes(rom.read(1), byteorder='little')
    C2A2 = int.from_bytes(rom.read(1), byteorder='little')
    FFBB = int.from_bytes(rom.read(1), byteorder='little')
    FFBC = int.from_bytes(rom.read(1), byteorder='little')

    HL_ram = rom.tell()
    # HL_ram = rom.tell() - (0xD - 1) * 0x4000
    # print(bytes.fromhex(hex(rom.tell() - (0xD - 1) * 0x4000)[2:]))

    # print(hex(HL_ram))
    rom.seek(8, os.SEEK_CUR)

    A = int.from_bytes(rom.read(1), byteorder='little')
    # print(hex(A))

    A = A * 2
    # print(hex(rom.tell() - (0xD - 1) * 0x4000))
    swap = False
    map_data['decoded'] = []
    for i in range(8):
        HL_stack = rom.tell()
        rom.seek(HL_ram)

        decoding = int.from_bytes(rom.read(1), byteorder='little')
        swap = not swap
        if swap:
            decoding = swap_byte(decoding)
        decoding = decoding & 0x0F

        if FFBB & 0x01 == 0:
            if FFBB > 0:
                FFBB -= 1
            else:
                FFBB = 0xFF
                FFBC -= 1

            FFBB = FFBB | FFBC
            new_byte = swap_byte(decoding)
            print(hex(new_byte))
            map_data['decoded'].append(new_byte)
        else:
            print(hex(decoding))
            map_data['decoded'].append(decoding)

        if FFBB > 0:
            FFBB -= 1
        else:
            FFBB = 0xFF
            FFBC -= 1

        rom.seek(HL_ram)


    return map_data

# def parse_next_pointer(offset=None):
#     if offset is not None:
#         rom.seek(offset)

#     b = rom.read(1)
#     while b != b'\x21':
#         b = rom.read(1)

#     pointer = int.from_bytes(rom.read(2), byteorder='little')

#     rom.seek(0x4000 + pointer)

#     return read_script()

#     return
#     item_type = rom.read(1)
#     try:
#         item_type = ITEM_TYPES[item_type]
#     except KeyError:
#         item_type = str(hex(ord(item_type)))
#     byte2 = rom.read(1)
#     equipment_effect = rom.read(1)
#     try:
#         equipment_effect = EQUIPMENT_EFFECTS[equipment_effect]
#     except KeyError:
#         equipment_effect = str(hex(ord(equipment_effect)))
#     purchase_price = int(''.join(reversed(rom.read(2))).encode('hex'), 16)

#     name = read_item_name()

#     item = {
#         'name': name,
#         'item_type': item_type,
#         'purchase_price': purchase_price,
#         'equipment_effect': equipment_effect,
#         'byte2': byte2,
#         'byte_count': 5 + len(name),
#     }

#     return item


# def extract_list(offset):
#     rom.seek(offset)
#     print('%17s %-20s %20s %10s : %-12s' % ('Range', 'Type', 'Effect', 'Price',
#                                             'Name'))
#     for i in range(87):
#         item = parse_item()
#         length = item['byte_count']
#         print("%s - %s %-20s %20s %10s : %-12s" %
#               (hex(offset), hex(offset + length), item['item_type'],
#                item['equipment_effect'], item['purchase_price'], item['name']))
#         offset += length + 1


# def extract_script(offset):
#     rom.seek(offset)

#     for i in range(100):
#         location = int(rom.tell() - offset)
#         pointer = location.to_bytes(2, byteorder='little')
#         pointer_print = int.from_bytes(pointer, byteorder='big')
#         print('{0:#06x} {1:#06x} {2}'.format(location, pointer_print,
#                                              read_script()))


# def look_for_potential_pointers(pointer):
#     potential_candidates = []
#     while True:
#         b = rom.read(1)
#         if not b:
#             break

#         if b == b'\x21':
#             if int.from_bytes(rom.read(2), byteorder='big') == pointer:
#                 potential_candidates.append(hex(rom.tell() - 2))

#     print(potential_candidates)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    index = int(arguments["<index>"])


    if arguments['read']:
        # Example offset : 0xD90F
        map_data = read_map(index)
        print(map_data)
