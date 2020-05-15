@echo off

echo Copying original ROM before patching...
cp roms/jw_original.gb roms/jw_patched.gb

rem echo Patching in font...
rem python jw_patcher.py apply --font patches/font.patch roms/jw_patched.gb

echo Patching in overworld font...
python jw_patcher.py apply patches/overworld_font.patch roms/jw_patched.gb 0x1EDAD

echo Patching in code [1/5]
python jw_patcher.py apply patches/extension_jump.patch roms/jw_patched.gb 0x0BAD

echo Patching in code [2/5]
python jw_patcher.py apply patches/extension_new_code.patch roms/jw_patched.gb 0x40000

echo Patching in code [3/5]
python jw_patcher.py apply patches/win_moved_code.patch roms/jw_patched.gb 0x7C700

echo Patching in code [4/5]
python jw_patcher.py apply_windows roms/jw_patched.gb

echo Patching in code [5/5]
python jw_patcher.py apply_enemies roms/jw_patched.gb


echo Inserting windows translation...
python jw_translation.py insert_windows --no-backup roms/jw_patched.gb jw_windows.yaml ..\tbl\jw-py-en.tbl 

echo Inserting translation...
python jw_translation.py insert --no-backup roms/jw_patched.gb jw_translation.yaml ..\tbl\jw-py-en.tbl 

echo Inserting enemy translation...
python jw_translation.py insert_enemies --no-backup roms/jw_patched.gb jw_enemies.yaml ..\tbl\jw-py-en.tbl 


echo All done!
