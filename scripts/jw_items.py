#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_items.py info <romfile> <offset> [<tablefile>]
          jw_items.py list <romfile> <offset> [<tablefile>]

Display information about Jungle Wars items.

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


def read_item_name():
    """Read an item name from the rom, and translate with a table if any."""
    name = bytearray()
    cur_byte = rom.read(1)
    while (cur_byte != b'\xFF'):
        name += cur_byte
        cur_byte = rom.read(1)

    if table:
        name = table.convert_bytearray(name)

    return name


def parse_item(offset=None):
    if offset is not None:
        rom.seek(offset)
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
    purchase_price = int.from_bytes(rom.read(2), byteorder='little')

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


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    offset = int(arguments["<offset>"], base=16)
    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])
    if arguments['info']:
        item = parse_item(offset)

        print('Item name: %s' % item['name'])
        print('Item type: %s' % item['item_type'])
        print('Equipment effect: %s' % item['equipment_effect'])
        print('Purchase price: %s' % item['purchase_price'])
        print('Selling price: %s' % floor(item['purchase_price'] * 0.75))
        print('Byte 2): %s' % item['byte2'])

    elif arguments['list']:
        extract_list(offset)
