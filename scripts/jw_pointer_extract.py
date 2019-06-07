#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_pointer_extract.py info <romfile> <offset> [<tablefile>]
          jw_pointer_extract.py list <romfile> <offset> [<tablefile>]
          jw_pointer_extract.py script <romfile> <offset> [<tablefile>]
          jw_pointer_extract.py seek <romfile> <offset> [<tablefile>]

Try and extract pointers and script.

Arguments
    <romfile>   The rom file to open
    <offset>    The offset in hex of the item
    <tablefile> Translation table to use

"""

from math import floor
from docopt import docopt
from translation_table import TranslationTable

rom = None
table = None

ITEM_TYPES = {
    b'\x40': 'Weapon (Mio)',
    b'\x41': 'Armour - Body (Mio)',
    b'\x80': 'Weapon (Boy)',
    b'\x90': '?Weapon (Boy)',
    b'\x81': 'Armour - Body (Boy)',
}

EQUIPMENT_EFFECTS = {
    b'\x00': 'None',
    b'\x01': 'Atk 2',
    b'\x02': 'Atk 7',
    b'\x03': 'Atk 12',
    b'\x04': 'Atk 20',
    b'\x05': 'Atk 8 Def 5 Spd 10',
    b'\x06': 'Atk 40',
    b'\x07': 'Atk 50',
    b'\x10': 'Atk 50, Blotted MP',
    b'\x11': 'Def 4',
}


def read_script():
    script = bytearray()
    cur_byte = rom.read(1)
    while (cur_byte != b'\xFF'):
        script += cur_byte
        cur_byte = rom.read(1)

    if table:
        script = table.convert_bytearray(script)

    return script


def parse_next_pointer(offset=None):
    if offset is not None:
        rom.seek(offset)

    b = rom.read(1)
    while b != b'\x21':
        b = rom.read(1)

    pointer = int.from_bytes(rom.read(2), byteorder='little')

    rom.seek(0x4000 + pointer)

    return read_script()

    return
    item_type = rom.read(1)
    try:
        item_type = ITEM_TYPES[item_type]
    except KeyError:
        item_type = str(hex(ord(item_type)))
    byte2 = rom.read(1)
    equipment_effect = rom.read(1)
    try:
        equipment_effect = EQUIPMENT_EFFECTS[equipment_effect]
    except KeyError:
        equipment_effect = str(hex(ord(equipment_effect)))
    purchase_price = int(''.join(reversed(rom.read(2))).encode('hex'), 16)

    name = read_item_name()

    item = {
        'name': name,
        'item_type': item_type,
        'purchase_price': purchase_price,
        'equipment_effect': equipment_effect,
        'byte2': byte2,
        'byte_count': 5 + len(name),
    }

    return item


def extract_list(offset):
    rom.seek(offset)
    print('%17s %-20s %20s %10s : %-12s' % ('Range', 'Type', 'Effect', 'Price',
                                            'Name'))
    for i in range(87):
        item = parse_item()
        length = item['byte_count']
        print("%s - %s %-20s %20s %10s : %-12s" %
              (hex(offset), hex(offset + length), item['item_type'],
               item['equipment_effect'], item['purchase_price'], item['name']))
        offset += length + 1


def extract_script(offset):
    rom.seek(offset)

    for i in range(100):
        location = int(rom.tell() - offset)
        pointer = location.to_bytes(2, byteorder='little')
        pointer_print = int.from_bytes(pointer, byteorder='big')
        print('{0:#06x} {1:#06x} {2}'.format(location, pointer_print,
                                             read_script()))


def look_for_potential_pointers(pointer):
    potential_candidates = []
    while True:
        b = rom.read(1)
        if not b:
            break

        if b == b'\x21':
            if int.from_bytes(rom.read(2), byteorder='big') == pointer:
                potential_candidates.append(hex(rom.tell() - 2))

    print(potential_candidates)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    offset = int(arguments["<offset>"], base=16)

    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])

    if arguments['info']:
        # Example offset : 0xD90F
        script_line = parse_next_pointer(offset)
        print(script_line)

    elif arguments['list']:
        extract_list(offset)

    elif arguments['script']:
        extract_script(offset)

    elif arguments['seek']:
        look_for_potential_pointers(offset)
