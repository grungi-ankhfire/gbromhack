#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_translation.py insert [--no-backup] <romfile> <inputfile> <tablefile>
          jw_translation.py merge <existing> <inputfile> [<outputfile>]

Helping script for manipulating Jungle Wars text.

Arguments
    <romfile>    The rom file to open
    <inputfile>  YAML file containing translation (or the one to merge)
    <tablefile>  Translation table to use
    <existing>   Existing YAML file in which to merge
    <outputfile> If specified save the merge there, if not, in place

Options
    --no-backup  Disable the automatic backup before patching
"""
from docopt import docopt
from translation_table import TranslationTable
import pyaml
import yaml
import shutil
import datetime


MAX_LENGTH = 17


# Encodes the actual length represented by "special bytes in text"
SPECIAL_BYTES = {
    "<var0>": 4,          # F0
    "<character>": 4,     # F0
    "<var1>": 4,          # F1
    "<var2>": 8,          # F2
    "<item>": 8,          # F2
    "<var3>": 4,          # F3
    "<var4>": 8,          # F4
    "<enemy>": 8,         # F4
    "<var5>": 4,          # F5
    "<var6>": 4,          # F6
    "<var7>": 4,          # F7
    "<var8>": 4,          # F8
    "<amount>": 4,        # F8
    "<var9>": 4,          # F9
    "<gold>": 4,          # F9
    "<price>": 4,         # FA
    "<FC>": 1,            # FC
}


class TextString:

    def __init__(self, pointer_address, text, max_length=MAX_LENGTH):

        self.pointer_address = pointer_address
        self.text = text
        self.new_bank = None
        self.new_pointer = None
        self.binary_text = None
        self.length = 0
        self.max_length = max_length

    def prepare(self):
        """ Returns the text, ready to be written in the ROM.

        Assumptions:
        <var0> is 4 characters long
        <var1> is 4 characters long
        <F4> is 8 characters
        """

        words = self.text.split()
        lines = [l.strip() for l in self.text.split("<br>")]

        prepared_text = ""
        self.length = 0
        line_num = 0
        for line in range(len(lines)):
            words = lines[line].split()
            cur_line_length = 0
            for i in range(len(words)):
                word = words[i]
                word_length = len(word)

                for b in SPECIAL_BYTES:
                    if word.find(b) != -1:
                        word_length -= len(b)
                        word_length += SPECIAL_BYTES[b]

                if i == 0:
                    prepared_text += word
                    self.length += word_length
                    cur_line_length += word_length

                else:
                    if cur_line_length + 1 + word_length <= self.max_length:
                        prepared_text += " " + word
                        self.length += word_length + 1
                        cur_line_length += word_length + 1
                    else:
                        if line_num % 2 == 0:
                            prepared_text += "<FE>"
                        else:
                            prepared_text += "<FD>"
                        line_num += 1
                        self.length += 1
                        cur_line_length = 0

                        prepared_text += word
                        self.length += word_length
                        cur_line_length += word_length

            if line < len(lines) - 1:
                if line_num % 2 == 0:
                    prepared_text += "<FE>"
                else:
                    prepared_text += "<FD>"
            else:
                prepared_text += "<FF>"
            self.length += 1
            line_num += 1
            cur_line_length = 0
        print(prepared_text)
        return prepared_text

        cur_line_length = 0
        prepared_text = ""
        self.length = 0
        line_num = 0
        for word in words:
            if len(word) + cur_line_length + 1 >= self.max_length:
                if line_num % 2 == 0:
                    prepared_text += "<FE>"
                else:
                    prepared_text += "<FD>"
                line_num += 1
                self.length += 1
                cur_line_length = 0

            prepared_text += word
            cur_line_length += len(word)
            if(word != words[-1]):
                cur_line_length += 1
                prepared_text += " "
                self.length += 1
            self.length += len(word)

        prepared_text += "<FF>"
        self.length += 1
        print(prepared_text)
        return prepared_text


rom = None
table = None

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments["insert"]:

        table = TranslationTable(arguments['<tablefile>'])

        if not arguments["--no-backup"]:
            # Make a backup of the rom file in case...
            shutil.copy(arguments["<romfile>"], arguments["<romfile>"] + ".backup." + datetime.datetime.now().strftime(format="%Y%m%d_%H_%M_%S"))

        rom = open(arguments["<romfile>"], 'rb+')

        translation_file = open(arguments["<inputfile>"], encoding='utf-8')
        data = yaml.load(translation_file, Loader=yaml.FullLoader)

        script = data["script"]
        combat = data["combat"]
        combat_wide = data["combat_wide"]
        in_place = data["in_place"]

        messages = [
            TextString(0x1A581,
                       "A morning in the Jungle.<FC>")
        ]

        for m in combat.values():
            if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
                messages.append(TextString(m['pointer_location'],
                                           m['translation'],
                                           max_length=10)
                                )

        for m in combat_wide.values():
            if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
                messages.append(TextString(m['pointer_location'],
                                           m['translation'])
                                )

        for m in script.values():
            if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
                messages.append(TextString(m['pointer_location'],
                                           m['translation'])
                                )
                print(m["translation"])

        for m in in_place:
            offset = m
            message_bytes = table.convert_script(in_place[m]["translation"])
            rom.seek(offset)
            rom.write(message_bytes)

        message_index = 0
        total_length = 0
        data_bank = 0x11

        for m in messages:
            m.binary_text = table.convert_script(m.prepare())

            m.new_bank = data_bank
            m.new_pointer = total_length
            total_length += m.length

            # Code to flow over to the next bank, might be bugged!
            if total_length > 0x4000:
                data_bank += 1
                m.new_bank = data_bank
                m.new_pointer = 0
                total_length = m.length

            rom.seek(m.pointer_address)
            rom.write((message_index * 3).to_bytes(2, "little"))

            rom.seek(0x10 * 0x4000 + 0x1000 + message_index * 0x03)
            rom.write((m.new_bank).to_bytes(1, "little"))
            rom.write((m.new_pointer).to_bytes(2, "little"))

            rom.seek(m.new_bank * 0x4000 + m.new_pointer)
            rom.write(m.binary_text)
            message_index += 1

        rom.close()

    elif arguments["merge"]:

        # jw_translation.py merge <existing> <inputfile> [<outputfile>]

        file1 = open(arguments["<existing>"], encoding='utf-8')
        data_existing = yaml.load(file1, Loader=yaml.FullLoader)
        file1.close()

        file2 = open(arguments["<inputfile>"], encoding='utf-8')
        data_new = yaml.load(file2, Loader=yaml.FullLoader)
        file2.close()


        for section2 in data_new:
            for loc2 in data_new[section2]:
                found = False
                found_element = None
                found_section = None
                for section1 in data_existing:
                    if loc2 in data_existing[section1]:
                        found = True
                        #found_element = data_existing[section1][loc2]
                        found_section = section1

                if found:
                    print("\n\n")
                    print(loc2)
                    print(data_existing[section1][loc2])
                    print("\n------------\n")
                    print(data_new[section2][loc2])
                    print("\n\n")
                else:
                    pass
                    # data_existing["script"][loc2] = section2[loc2]


        # outfile = None
        # if arguments["<outputfile>"]:
        #     outfile = open(arguments['<outputfile>'], 'w', encoding='utf-8')
        # else:
        #     outfile = open(arguments['<existing>'], 'w', encoding='utf-8')

        # outfile.write(pyaml.dump(data, indent=2, vspacing=[2, 1], width=float("inf")))
        # outfile.close()
