#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_script.py dump <romfile> <start> <end> [<tablefile>] [<outputfile>]
          jw_script.py yaml_dump <romfile> <start>  <end>  [<tablefile>] [<outputfile>]
          jw_script.py insert <scriptfile> <romfile> <start> <end> <tablefile>
          jw_script.py yaml_convert <oldfile> <outputfile>
          jw_script.py yaml_redump <oldfile> <outputfile>

Helping script for manipulating Jungle Wars text.

Arguments
    <romfile>    The rom file to open
    <start>      The offset in hex to start the dump
    <end>        The offset in hex to finish the dump
    <tablefile>  Translation table to use
    <scriptfile> File containing a Unicode script
    <outputfile> File in which to dump the script
    <oldfile>    File using the old YAML schema to convert
"""
import sys
from docopt import docopt
from translation_table import TranslationTable
import pyaml
import yaml


rom = None
table = None


class HexInt(int):
    pass


def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, 7))


pyaml.add_representer(HexInt, representer)


from yaml.constructor import Constructor


def add_hexint(self, node):
    print(node)
    return HexInt(node)


def my_construct_mapping(self, node, deep=False):
    data = self.construct_mapping_org(node, deep)
    return {(HexInt(key) if isinstance(key, int) else key): (HexInt(data[key]) if isinstance(data[key], int) else data[key]) for key in data}


yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
yaml.SafeLoader.construct_mapping = my_construct_mapping


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

    messages = {}

    message = dict()

    rom.seek(offset)
    message_bytes = bytearray()

    cur_byte = rom.read(1)
    message_offset = HexInt(offset)
    while(offset != end_offset):
        message_bytes += cur_byte
        if int.from_bytes(cur_byte, 'little') == int('FF', base=16) or int.from_bytes(cur_byte, 'little') == int('FC', base=16) :
            if table:
                message["original"] = table.convert_bytearray(message_bytes)
            else:
                message["original"] = message_bytes.copy()
            message["translation"] = "TODO_" + "{0:#0{1}x}".format(message_offset, 7)
            message["pointer_location"] = 0
            messages[message_offset] = message.copy()
            message_bytes.clear()
            message_offset = HexInt(offset)

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

    offset = None
    end_offset = None

    if arguments['<start>']:
        offset = int(arguments["<start>"], base=16)
    if arguments['<end>']:
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
            f.write(pyaml.dump(script, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
            f.close()
        else:
            print(pyaml.dump(script, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))

    if arguments['insert']:
        rom = open(arguments["<romfile>"], 'rb+')
        f = open(arguments['<scriptfile>'], 'r', encoding='utf-8')
        script = f.read()
        f.close()
        insert_script(offset, end_offset, script)

    if arguments['yaml_convert']:

        input_file = open(arguments["<oldfile>"], encoding='utf-8')
        content = yaml.load(input_file, Loader=yaml.FullLoader)
        input_file.close()

        data = dict()

        for section in content:
            data[section] = dict()
            for element in content[section]:
                location = HexInt(element["location"])
                while location in data[section]:
                    location += "_"
                data[section][location] = dict()
                for key, value in element.items():
                    if key != "location":
                        if type(value) is int:
                            data[section][location][key] = hex(value)
                        else:
                            data[section][location][key] = value

        f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
        f.write(pyaml.dump(data, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
        f.close()

    if arguments['yaml_redump']:
        input_file = open(arguments["<oldfile>"], encoding='utf-8')
        content = yaml.safe_load(input_file)
        input_file.close()

        f = open(arguments['<outputfile>'], 'w', encoding='utf-8')
        f.write(pyaml.dump(content, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
        f.close()
