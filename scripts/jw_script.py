#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_script.py dump <romfile> <start> <end> [<tablefile>] [<outputfile>]
          jw_script.py yaml_dump <romfile> <start>  <end>  [<tablefile>] [<outputfile>]
          jw_script.py insert <scriptfile> <romfile> <start> <end> <tablefile>

Helping script for manipulating Jungle Wars text.

Arguments
    <romfile>    The rom file to open
    <start>      The offset in hex to start the dump
    <end>        The offset in hex to finish the dump
    <tablefile>  Translation table to use
    <scriptfile> File containing a Unicode script
    <outputfile> File in which to dump the script
"""
from docopt import docopt
from translation_table import TranslationTable
import pyaml

rom = None
table = None


def dump_script(offset, end_offset):
    rom.seek(offset)
    script = bytearray()
    cur_byte = rom.read(1)
    while(offset != end_offset):
        script += cur_byte
        cur_byte = rom.read(1)
        offset += 1

    if table:
        script = table.convert_bytearray(script)

    return script


def yaml_dump_script(offset, end_offset):

    script = dict()

    messages = []

    message = dict()

    rom.seek(offset)
    message_bytes = bytearray()

    cur_byte = rom.read(1)
    message["location"] = hex(offset)
    while(offset != end_offset):
        message_bytes += cur_byte
        if int.from_bytes(cur_byte, 'little') == int('FF', base=16):
            if table:
                message["original"] = table.convert_bytearray(message_bytes)
            else:
                message["original"] = message_bytes.copy()
            message["translation"] = "TODO_" + message["location"]
            message["pointer_location"] = 0
            messages.append(message.copy())
            message_bytes.clear()
            message["location"] = hex(offset)

        cur_byte = rom.read(1)
        offset += 1

    script["script"] = messages

    return script


def insert_script(offset, end_offset, script):
    rom.seek(offset)
    binary_script = table.convert_script(script)
    rom.write(binary_script)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    offset = int(arguments["<start>"], base=16)
    end_offset = int(arguments["<end>"], base=16)
    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])

    if arguments['dump']:
        rom = open(arguments["<romfile>"], 'rb')
        script = dump_script(offset, end_offset)
        if arguments['<outputfile>']:
            f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
            f.write(script)
            f.close()
        else:
            print(script)

    if arguments['yaml_dump']:
        rom = open(arguments["<romfile>"], 'rb')
        script = yaml_dump_script(offset, end_offset)
        if arguments['<outputfile>']:
            f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
            f.write(pyaml.dump(script, indent=2, vspacing=[2, 1]))
            f.close()
        else:
            print(pyaml.p(script))

    if arguments['insert']:
        rom = open(arguments["<romfile>"], 'rb+')
        f = open(arguments['<scriptfile>'], 'r', encoding='utf-8')
        script = f.read()
        f.close()
        insert_script(offset, end_offset, script)
