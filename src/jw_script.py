#!/usr/bin/python
# -*- c
# coding:utf-8 -*-
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
from typing import BinaryIO, TextIO
import click
from docopt import docopt
from translation_table import TranslationTable
import pyaml
import yaml
from jw_config import config, path
from hexint import HexInt
import translation_table
from yaml_writer import YamlWriter
from click_param_types import BASED_INT

rom = None
table = None


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

@click.group()
def cli():
    pass


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


@cli.command(context_settings={'show_default':True})
@click.argument("offset", type=BASED_INT)
@click.argument("end_offset", type=BASED_INT)
@click.argument("romfile", type=click.File('rb'), default=path(config["original_rom"]))
@click.option("--table", type=click.Path(), default=path(config["script"]["table"]))
@click.option('--outputfile', type=click.File('wb'), default=None, help='File to write the script to')
def dump(offset: int, end_offset: int, romfile: BinaryIO, table: click.Path, outputfile: BinaryIO|None):
    translation_table = TranslationTable(table) if table else None

    romfile.seek(offset)
    script = bytearray()
    cur_byte = romfile.read(1)
    while(offset != end_offset):
        script += cur_byte
        cur_byte = romfile.read(1)
        offset += 1

    if translation_table:
        script = translation_table.convert_bytearray(script).encode()
    if outputfile is not None:
        outputfile.write(script)
    else:
        click.echo(script)


@cli.command(context_settings={'show_default':True})
@click.argument("offset", type=BASED_INT)
@click.argument("end_offset", type=BASED_INT)
@click.argument("romfile", type=click.File('rb'), default=path(config["original_rom"]))
@click.option("--table", type=click.Path(), default=path(config["script"]["table"]))
@click.option('--outputfile', type=click.File('w', encoding="utf-8"), default=None, help='File to write the script to')
def yaml_dump(offset: int, end_offset: int, romfile: BinaryIO, table: click.Path, outputfile: TextIO|None):
    translation_table = TranslationTable(table) if table else None

    script = dict()
    messages = dict()

    romfile.seek(offset)
    message_bytes = bytearray()

    cur_byte = romfile.read(1)
    message_offset = HexInt(offset)
    message = dict()
    while(offset != end_offset):
        message_bytes += cur_byte
        if int.from_bytes(cur_byte, 'little') == int('FF', base=16) or int.from_bytes(cur_byte, 'little') == int('FC', base=16) :
            if translation_table:
                message["original"] = translation_table.convert_bytearray(message_bytes)
            else:
                message["original"] = message_bytes.copy()
            message["translation"] = "TODO_" + "{0:#0{1}x}".format(message_offset, 7)
            message["pointer_location"] = 0
            messages[message_offset] = message.copy()
            message_bytes.clear()
            message_offset = HexInt(offset)

        cur_byte = romfile.read(1)
        offset += 1

    script["script"] = messages
 
    if outputfile is not None:
        outputfile.write(pyaml.dump(script, indent=2, vspacing=True, width=-1, string_val_style='"'))
    else:
        click.echo(pyaml.dump(script, indent=2, vspacing=True, width=-1, string_val_style='"'))


if __name__ == '__main__':
    cli()

    arguments = docopt(__doc__, version='1.0')

    offset = None
    end_offset = None

    if arguments['<start>']:
        offset = int(arguments["<start>"], base=16)
    if arguments['<end>']:
        end_offset = int(arguments["<end>"], base=16)
    if (arguments['<tablefile>']):
        table = TranslationTable(arguments['<tablefile>'])

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
