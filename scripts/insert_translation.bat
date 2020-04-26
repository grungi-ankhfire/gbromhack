@echo off

echo Copying original ROM before patching...
cp roms/jw_original.gb roms/jw_patched.gb

echo Patching in font...
python jw_patcher.py apply --font patches/font.patch roms/jw_patched.gb

echo Patching in code [1/2]
python jw_patcher.py apply patches/extension_jump.patch roms/jw_patched.gb 0x0BAD

echo Patching in code [2/2]
python jw_patcher.py apply patches/extension_new_code.patch roms/jw_patched.gb 0x40000

echo Inserting translation...
python jw_translation.py --no-backup roms/jw_patched.gb jw_translation.yaml ..\tbl\jw-py-en.tbl 

echo All done!
