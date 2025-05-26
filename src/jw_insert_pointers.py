#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_insert_pointers.py <pointersfile> <translationfile> [<outputfile>]

Helping script for manipulating Jungle Wars text.

Arguments
    <pointersfile>    YAML file containing the pointers
    <translationfile> YAML file containing the translation
    <outputfile>      File in which to save the results, if not given, doing in translationfile
"""
import sys
from docopt import docopt
from translation_table import TranslationTable
import pyaml
import yaml
from yaml.constructor import Constructor


class HexInt(int):
    pass


def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, 7))


pyaml.add_representer(HexInt, representer)


def add_hexint(self, node):
    print(node)
    return HexInt(node)


def my_construct_mapping(self, node, deep=False):
    data = self.construct_mapping_org(node, deep)
    return {(HexInt(key) if isinstance(key, int) else key): (HexInt(data[key]) if isinstance(data[key], int) else data[key]) for key in data}



if __name__ == '__main__':

    yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
    yaml.SafeLoader.construct_mapping = my_construct_mapping


    arguments = docopt(__doc__, version='1.0')

    pointersfile = open(arguments["<pointersfile>"], encoding='utf-8')
    pointers = yaml.safe_load(pointersfile)
    pointersfile.close()

    translationfile = open(arguments["<translationfile>"], encoding='utf-8')
    translation = yaml.safe_load(translationfile)
    translationfile.close()

    remaining_pointers = dict()

    for location in pointers:
        if location in translation["script"] and translation["script"][location]["pointer_location"] == 0:
            guesses = pointers[location]["confident"]
            if len(guesses) > 1:
                remaining_pointers["{0:#0{1}x}".format(location, 7)] = {"confident": ["{0:#0{1}x}".format(g, 7) for g in guesses]}
            translation["script"][location]["pointer_location"] = HexInt(guesses[0])

    print(pyaml.dump(remaining_pointers, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))

    outputfile = None
    if arguments["<outputfile>"]:
        outputfile = arguments["<outputfile>"]
    else:
        outputfile = arguments["<translationfile>"]
    
    f = open(outputfile, 'w', encoding='utf-8')
    f.write(pyaml.dump(translation, indent=2, vspacing=[2, 1], width=float("inf"), string_val_style='"'))
    f.close()
