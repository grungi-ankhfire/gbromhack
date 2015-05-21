#!/usr/bin/python
"""Usage: jw_items.py <romfile> <offset> [<tablefile>]

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
    b'\x80': '?Weapon (Boy)',
    b'\x81': 'Armour - Body (Boy)',
}

EQUIPMENT_EFFECTS = {
    b'\x00': 'None',
    b'\x01': 'Atk 2',
    b'\x02': 'Atk 7',
    b'\x03': '?Atk 11',
    b'\x04': '?Atk 19',
    b'\x05': 'Atk 8 Def 5 Spd 10',
    b'\x10': '?Atk 49',
    b'\x11': 'Def 4',
}


def parse_item(offset):
    rom.seek(offset)
    item_type = ITEM_TYPES[rom.read(1)]
    byte2 = rom.read(1)
    equipment_effect = EQUIPMENT_EFFECTS[rom.read(1)]
    purchase_price = ord(rom.read(1))
    byte5 = rom.read(1)

    name = bytearray()
    cur_byte = rom.read(1)
    while(cur_byte != b'\xFF'):
        name += cur_byte
        cur_byte = rom.read(1)

    if table:
        name = table.convert_bytearray(name)

    print('Item name: %s' % name)
    print('Item type: %s' % item_type)
    print('Equipment effect: %s' % equipment_effect)
    print('Purchase price: %s' % purchase_price)
    print('Selling price: %s' % floor(purchase_price*0.75))
    print('Info bytes (2, 5): %s %s' % (byte2, byte5))
if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    rom = open(arguments["<romfile>"], 'rb')
    offset = int(arguments["<offset>"], base=16)
    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])

    parse_item(offset)
