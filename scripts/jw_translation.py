#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_translation.py [--no-backup] <romfile> <inputfile> <tablefile>

Helping script for manipulating Jungle Wars text.

Arguments
    <romfile>    The rom file to open
    <inputfile>  YAML file containing translation
    <tablefile>  Translation table to use

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

                if word.find("<var0>") != -1:
                    word_length -= 6  # Don't count "<var0>"
                    word_length += 4  # Count the actual length

                if word.find("<var1>") != -1:
                    word_length -= 6
                    word_length += 4

                if word.find("<var2>") != -1:
                    word_length -= 6
                    word_length += 4

                if word.find("<var8>") != -1:
                    word_length -= 6
                    word_length += 4

                if word.find("<var9>") != -1:
                    word_length -= 6
                    word_length += 4

                if word.find("<F4>") != -1:
                    word_length -= 6
                    word_length += 8

                if word.find("<FC>") != -1:
                    word_length -= 4
                    word_length += 1

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

    for m in combat:
        if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
            messages.append(TextString(m['pointer_location'],
                                       m['translation'],
                                       max_length=10)
                            )

    for m in combat_wide:
        if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
            messages.append(TextString(m['pointer_location'],
                                       m['translation'])
                            )

    for m in script:
        if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
            messages.append(TextString(m['pointer_location'],
                                       m['translation'])
                            )

    for m in in_place:
        offset = m["location"]
        message_bytes = table.convert_script(m["translation"])
        rom.seek(offset)
        rom.write(message_bytes)

    message_index = 0
    total_length = 0

    for m in messages:
        m.binary_text = table.convert_script(m.prepare())

        m.new_bank = b'\x11'
        m.new_pointer = total_length.to_bytes(2, "little")
        total_length += m.length
        rom.seek(m.pointer_address)
        rom.write((message_index * 3).to_bytes(2, "little"))

        rom.seek(0x10 * 0x4000 + 0x1000 + message_index * 0x03)
        rom.write(m.new_bank)
        rom.write(m.new_pointer)

        rom.seek(int.from_bytes(m.new_bank, "little") * 0x4000 + int.from_bytes(m.new_pointer, "little"))
        rom.write(m.binary_text)
        message_index += 1

    rom.close()

# Need:
#   The old pointer adress (where the pointer is in the ROM)
#   The new script
#  
# Insert the  
# Write new pointer in rom in place of the old one
#