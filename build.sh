#!/bin/bash
set -e

echo "Building Jungle Wars Translation..."

# Check original ROM
if [ ! -f "scripts/roms/jw_original.gb" ]; then
    echo "Error: scripts/roms/jw_original.gb not found!"
    exit 1
fi

# 1. Clean/Prepare
echo "Creating working copy..."
cp scripts/roms/jw_original.gb scripts/roms/jw_patched.gb

# 2. Binary Patches
echo "Applying binary patches..."
pipenv run python3 scripts/jw_patcher.py apply --font scripts/patches/font.patch scripts/roms/jw_patched.gb
pipenv run python3 scripts/jw_patcher.py apply scripts/patches/extension_jump.patch scripts/roms/jw_patched.gb 0x0BAD
pipenv run python3 scripts/jw_patcher.py apply scripts/patches/extension_new_code.patch scripts/roms/jw_patched.gb 0x40000
pipenv run python3 scripts/jw_patcher.py apply scripts/patches/win_moved_code.patch scripts/roms/jw_patched.gb 0x7C700

# 3. Logic Patches
echo "Applying logic patches..."
pipenv run python3 scripts/jw_patcher.py apply_windows scripts/roms/jw_patched.gb
pipenv run python3 scripts/jw_patcher.py apply_enemies scripts/roms/jw_patched.gb
pipenv run python3 scripts/jw_patcher.py apply_npcs scripts/roms/jw_patched.gb

# 4. Insert Translations
echo "Inserting translations..."
pipenv run python3 scripts/jw_translation.py insert_windows --no-backup scripts/roms/jw_patched.gb scripts/translation/jw_windows.yaml tbl/jw-py-en.tbl
pipenv run python3 scripts/jw_translation.py insert --no-backup scripts/roms/jw_patched.gb scripts/jw_translation.yaml tbl/jw-py-en.tbl
pipenv run python3 scripts/jw_translation.py insert_enemies --no-backup scripts/roms/jw_patched.gb scripts/translation/jw_enemies.yaml tbl/jw-py-en.tbl
pipenv run python3 scripts/jw_translation.py insert_signs --no-backup scripts/roms/jw_patched.gb scripts/translation/jw_signs.yaml tbl/jw-py-en.tbl
pipenv run python3 scripts/jw_translation.py insert_npcs --no-backup scripts/roms/jw_patched.gb scripts/translation/jw_npcs.yaml tbl/jw-py-en.tbl

# 5. Fix Checksum
echo "Fixing checksum..."
if command -v rgbfix &> /dev/null; then
    rgbfix -v -p 0xFF scripts/roms/jw_patched.gb
else
    echo "Warning: rgbfix not found. Checksum not fixed."
fi

echo "Build complete: scripts/roms/jw_patched.gb"
