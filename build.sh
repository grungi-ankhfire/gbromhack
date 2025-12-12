#!/bin/bash
set -e

echo "Building Jungle Wars Translation..."

# Sanity-check patch payloads so we don't build a ROM that crashes later.
python3 - <<'PY'
from pathlib import Path

def must(path, size, prefix_hex):
    b = Path(path).read_bytes()
    if len(b) != size:
        raise SystemExit(f"Error: {path} is {len(b)} bytes, expected {size}.")
    prefix = bytes.fromhex(prefix_hex)
    if not b.startswith(prefix):
        raise SystemExit(f"Error: {path} has unexpected header bytes (expected {prefix_hex}).")

must("scripts/patches/extension_jump.patch", 8, "3e10c7cd0040181f")
must("scripts/patches/extension_new_code.patch", 0x4000, "facac13deacac13c")
must("scripts/patches/win_moved_code.patch", 160, "7cc650672a5e2356")
PY

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

python3 - <<'PY'
from pathlib import Path
rom = Path("scripts/roms/jw_patched.gb").read_bytes()
def at(off, prefix_hex):
    prefix = bytes.fromhex(prefix_hex)
    got = rom[off:off+len(prefix)]
    if got != prefix:
        raise SystemExit(f"Error: ROM bytes at {hex(off)} mismatch; expected {prefix_hex}, got {got.hex()}.")
at(0x0BAD, "3e10c7cd0040181f")
at(0x40000, "facac13deacac13c")
at(0x7C700, "7cc650672a5e2356")
PY

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
