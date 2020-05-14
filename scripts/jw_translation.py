#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Usage: jw_translation.py insert [--no-backup] <romfile> <inputfile> <tablefile>
          jw_translation.py merge <existing> <inputfile> [<outputfile>]
          jw_translation.py insert_windows [--no-backup] <romfile> <inputfile> <tablefile>
          jw_translation.py insert_enemies [--no-backup] <romfile> <inputfile> <tablefile>


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
from jw_win import JWWindow


class HexInt(int):
    pass


def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, 7))


pyaml.add_representer(HexInt, representer)


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
        # print(prepared_text)
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
        # print(prepared_text)
        return prepared_text


rom = None
table = None


def insert_translation(rom_file, translation_data, table):

    script = translation_data["script"]
    combat = translation_data["combat"]
    combat_wide = translation_data["combat_wide"]
    in_place = translation_data["in_place"]

    messages = [TextString(0x1A581, "A morning in the Jungle.<FC>")]

    for msg_set in [(script, 17), (combat, 10), (combat_wide, 17)]:
        msg_len = msg_set[1]
        for m in msg_set[0].values():
            if m["translation"][0:4] != 'TODO' and m['pointer_location'] != 0:
                messages.append(TextString(m['pointer_location'],
                                           m['translation'],
                                           max_length=msg_len)
                                )

    for m in in_place:
        offset = m
        message_bytes = table.convert_script(in_place[m]["translation"])
        rom_file.seek(offset)
        rom_file.write(message_bytes)

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

        rom_file.seek(m.pointer_address)
        rom_file.write((message_index * 3).to_bytes(2, "little"))

        rom_file.seek(0x10 * 0x4000 + 0x1000 + message_index * 0x03)
        rom_file.write((m.new_bank).to_bytes(1, "little"))
        rom_file.write((m.new_pointer).to_bytes(2, "little"))

        rom_file.seek(m.new_bank * 0x4000 + m.new_pointer)
        rom_file.write(m.binary_text)
        message_index += 1

    print("Wrote up to bank " + hex(data_bank))


def insert_windows(rom_file, windows_data, table):

    POINTERS_START_FULLSCREEN = 0x1F * 0x4000
    POINTERS_START_OVERLAY = 0x1F * 0x4000 + 0x500
    DATA_START = 0x1F * 0x4000 + 0x1000

    total_size = 0

    for win_id in windows_data["fullscreen"]:
        data = windows_data["fullscreen"][win_id]
        win = JWWindow()
        win.from_yaml(data, win_id)
        rom_file.seek(POINTERS_START_FULLSCREEN + win.id * 2)
        rom.write((0x5000 + total_size).to_bytes(2, "little"))
        rom.seek(DATA_START + total_size)
        force_header = data.get("force_header", None)
        if force_header:
            rom.write(force_header.to_bytes(6, "big"))
        else:
            rom.write(win.recompute_header())
        total_size += 6
        translation = table.convert_script(win.translation)
        rom.write(translation)
        total_size += len(translation)

    for win_id in windows_data["overlay"]:
        data = windows_data["overlay"][win_id]
        win = JWWindow()
        win.from_yaml(data, win_id)
        rom_file.seek(POINTERS_START_OVERLAY + (win.id - 0x80) * 2)
        rom.write((0x5000 + total_size).to_bytes(2, "little"))
        rom.seek(DATA_START + total_size)
        force_header = data.get("force_header", None)
        if force_header:
            rom.write(force_header.to_bytes(6, "big"))
        else:
            rom.write(win.recompute_header())
        total_size += 6
        translation = table.convert_script(win.translation)
        rom.write(translation)
        total_size += len(translation)

def insert_enemies(rom_file, enemies_data, table):

    POINTERS_START = 0x1E * 0x4000
    DATA_START = 0x1E * 0x4000 + 0x1000

    total_size = 0

    for enemy_id in enemies_data["enemies"]:
        data = enemies_data["enemies"][enemy_id]
        rom_file.seek(POINTERS_START + enemy_id * 2)
        rom.write((0x5000 + total_size).to_bytes(2, "little"))

        rom.seek(DATA_START + total_size)
        rom.write(data["original_header"].to_bytes(22, "big"))
        total_size += 22
        translation = table.convert_script(data["translated_name"])
        rom.write(translation)
        rom.seek(data["location"] + 22)
        rom.write(translation)
        total_size += len(translation)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments["insert"]:

        table = TranslationTable(arguments['<tablefile>'])

        if not arguments["--no-backup"]:
            # Make a backup of the rom file in case...
            now = datetime.datetime.now().strftime(format="%Y%m%d_%H_%M_%S")
            shutil.copy(arguments["<romfile>"], arguments["<romfile>"] + ".backup." + now)

        rom = open(arguments["<romfile>"], 'rb+')

        translation_file = open(arguments["<inputfile>"], encoding='utf-8')
        data = yaml.load(translation_file, Loader=yaml.FullLoader)
        translation_file.close()

        insert_translation(rom, data, table)

        rom.close()

    elif arguments["insert_windows"]:

        table = TranslationTable(arguments['<tablefile>'])

        if not arguments["--no-backup"]:
            # Make a backup of the rom file in case...
            now = datetime.datetime.now().strftime(format="%Y%m%d_%H_%M_%S")
            shutil.copy(arguments["<romfile>"], arguments["<romfile>"] + ".backup." + now)

        rom = open(arguments["<romfile>"], 'rb+')

        translation_file = open(arguments["<inputfile>"], encoding='utf-8')
        data = yaml.load(translation_file, Loader=yaml.FullLoader)
        translation_file.close()

        insert_windows(rom, data, table)

        rom.close()

    elif arguments["insert_enemies"]:

        table = TranslationTable(arguments['<tablefile>'])

        if not arguments["--no-backup"]:
            # Make a backup of the rom file in case...
            now = datetime.datetime.now().strftime(format="%Y%m%d_%H_%M_%S")
            shutil.copy(arguments["<romfile>"], arguments["<romfile>"] + ".backup." + now)

        rom = open(arguments["<romfile>"], 'rb+')

        translation_file = open(arguments["<inputfile>"], encoding='utf-8')
        data = yaml.load(translation_file, Loader=yaml.FullLoader)
        translation_file.close()

        insert_enemies(rom, data, table)

        rom.close()

    elif arguments["merge"]:

        # jw_translation.py merge <existing> <inputfile> [<outputfile>]

        file1 = open(arguments["<existing>"], encoding='utf-8')
        data_existing = yaml.load_safe(file1, Loader=yaml.FullLoader)
        file1.close()

        file2 = open(arguments["<inputfile>"], encoding='utf-8')
        data_new = yaml.load_safe(file2, Loader=yaml.FullLoader)
        file2.close()

        for section2 in data_new:
            for loc2 in data_new[section2]:
                found = False
                found_element = None
                found_section = None
                for section1 in data_existing:
                    if loc2 in data_existing[section1]:
                        found = True
                        # found_element = data_existing[section1][loc2]
                        found_section = section1
                        break

                if found:

                    element1 = data_existing[section1][loc2]
                    element2 = data_new[section2][loc2]

                    if data_existing[section1][loc2] != data_new[section2][loc2]:
                        if (section1 == "script" and
                                element1["translation"][0:4] == "TODO" and
                                element1["pointer_location"] == 0):

                            data_existing[section1][loc2] = element2
                        else:
                            if element1["original"] != element2["original"]:
                                print("\n\n")
                                print(hex(loc2) + " - Changes in the original string:")
                                print("1 OLD : " + element1["original"])
                                print("2 NEW : " + element2["original"])
                                keep = input("Which to keep? (1/[2]) ")
                                if keep.strip() == "1":
                                    pass
                                else:
                                    element1["original"] = element2["original"]

                            if element1['pointer_location'] == 0 and element2['pointer_location'] != 0:
                                element1['pointer_location'] == element2['pointer_location']
                            elif element1['pointer_location'] != 0 and element2['pointer_location'] != 0:
                                print("\n\n")
                                print(hex(loc2) + " - Different pointer locations found:")
                                print("1 OLD : " + element1["original"])
                                print("2 NEW : " + element2["original"])
                                keep = input("Which to keep? (1/[2]) ")
                                if keep.strip() == "1":
                                    pass
                                else:
                                    element1["pointer_location"] = element2["pointer_location"]

                            if element1["translation"][0:4] == "TODO" and element2["translation"][0:4] != "TODO":
                                element1["translation"] = element2["translation"]
                            elif element1['translation'][0:4] != "TODO" and element2['translation'][0:4] != "TODO":
                                print("\n\n")
                                print(hex(loc2) + " - Different translations found:")
                                print("1 OLD : " + element1["original"])
                                print("2 NEW : " + element2["original"])
                                keep = input("Which to keep? (1/[2]) ")
                                if keep.strip() == "1":
                                    pass
                                else:
                                    element1["translation"] = element2["translation"]

                else:
                    pass
                    # data_existing["script"][loc2] = section2[loc2]

        outfile = None
        if arguments["<outputfile>"]:
            outfile = open(arguments['<outputfile>'], 'w', encoding='utf-8')
        else:
            outfile = open(arguments['<existing>'], 'w', encoding='utf-8')

        outfile.write(pyaml.dump(data_existing, indent=2, vspacing=[2, 1], width=float("inf")))
        outfile.close()
