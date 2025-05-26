@echo off

echo Copying original ROM before patching...
xcopy .\roms\jw_original.gb .\roms\jw_patched.gb /Y

echo Patching in font...
uv run jw_patcher.py apply --font patches/font.patch roms/jw_patched.gb

:: echo Patching in overworld font...
:: python jw_patcher.py apply patches/overworld_font.patch roms/jw_patched.gb 0x1EDAD

echo Patching in code [1/7]
uv run jw_patcher.py apply patches/extension_jump.patch roms/jw_patched.gb 0x0BAD

echo Patching in code [2/7]
uv run jw_patcher.py apply patches/extension_new_code.patch roms/jw_patched.gb 0x40000

echo Patching in code [3/7]
uv run jw_patcher.py apply patches/win_moved_code.patch roms/jw_patched.gb 0x7C700

echo Patching in code [4/7]
uv run jw_patcher.py apply_windows roms/jw_patched.gb

echo Patching in code [5/7]
uv run jw_patcher.py apply_enemies roms/jw_patched.gb

echo Patching in code [6/7]
uv run jw_patcher.py apply_npcs roms/jw_patched.gb

echo Patching in code[7/7]
uv run jw_patcher.py apply_intro roms/jw_patched.gb

echo Inserting windows translation...
uv run jw_translation.py insert_windows --no-backup roms/jw_patched.gb translation/jw_windows.yaml ..\tbl\jw-py-en.tbl 

echo Inserting translation...
uv run jw_translation.py insert --no-backup roms/jw_patched.gb jw_translation.yaml ..\tbl\jw-py-en.tbl 

echo Inserting enemy translation...
uv run jw_translation.py insert_enemies --no-backup roms/jw_patched.gb translation/jw_enemies.yaml ..\tbl\jw-py-en.tbl 

echo Inserting sign translation...
uv run jw_translation.py insert_signs --no-backup roms/jw_patched.gb translation/jw_signs.yaml ..\tbl\jw-py-en.tbl 

echo Inserting npc names translation...
uv run jw_translation.py insert_npcs --no-backup roms/jw_patched.gb translation/jw_npcs.yaml ..\tbl\jw-py-en.tbl 

echo Inserting intro credits translation...
uv run jw_intro.py roms/jw_patched.gb ..\tbl\jw-py-en.tbl

echo All done!
