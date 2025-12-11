# Jungle Wars (GB) ROM Hacking Project

## Project Overview
This project contains a suite of Python scripts and tools designed for hacking and translating the GameBoy game "Jungle Wars". It includes utilities for dumping text, inserting translations, managing pointers, and applying assembly patches.

## key Features
- **Text Injection:** Tools to extract and re-insert text using custom encoding tables (`.tbl`).
- **Pointer Management:** scripts to recalculate and update pointers for translated text.
- **Patching:** Utilities to apply binary patches for fonts, window layouts, and game logic changes.
- **ROM Info:** A tool to inspect GameBoy ROM headers.

## Setup & Prerequisites

### Dependencies
The project uses `pipenv` for Python dependency management.
- **Python:** Version 3.9 is specified in `Pipfile`.
- **Libraries:** `docopt`, `pyaml`, `ips-util`.

To install dependencies:
```bash
pipenv install
```

### External Tools
- **RGBDS:** The `make_patch.bat` script references `rgbfix` (part of Rednex Game Boy Development System) to fix the ROM header checksums. Ensure this is available in your PATH if you intend to produce valid ROMs.

## Directory Structure

- **`scripts/`**: Core Python scripts and batch files.
    - `jw_patcher.py`: The main utility for applying various patches (fonts, windows, enemies).
    - `rominfo.py`: Displays metadata about a GB ROM file.
    - `jw_translation.py`: Handles text extraction/insertion.
    - `patches/`: Directory containing binary or assembly patches.
    - `translation/`: YAML files containing the translated text data.
    - `roms/`: Place for input (`jw_original.gb`) and output (`jw_patched.gb`) ROM files.
- **`tbl/`**: Character mapping tables (`.tbl`) used to decode/encode the game's text.

## Usage Guidelines

### Common Commands

**1. Display ROM Information:**
```bash
python scripts/rominfo.py path/to/rom.gb
```

**2. Apply Patches:**
The `jw_patcher.py` script is the primary interface for modifying the ROM.
```bash
# General usage
python scripts/jw_patcher.py <command> [options]

# Examples
python scripts/jw_patcher.py apply_windows roms/jw_patched.gb
python scripts/jw_patcher.py apply --font patches/overworld_font.patch roms/jw_patched.gb
```

**3. Workflow Scripts (Windows .bat):**
The project includes batch files that document the intended workflow. Translating them to shell commands for Linux/macOS is straightforward:
- `make_patch.bat`: Fixes checksums and creates an IPS patch.
- `dump_script.bat`: likely dumps text from the ROM.
- `insert_translation.bat`: likely inserts the translated text from YAML files.

### Translation Workflow
1.  **Dump:** Extract text from the original ROM (using `jw_translation.py` or similar).
2.  **Translate:** Edit the YAML files in `scripts/translation/`.
3.  **Insert:** Run the insertion scripts to put text back into the ROM and update pointers.
4.  **Patch:** Apply necessary code patches (fonts, windows) using `jw_patcher.py`.
5.  **Fix:** Run `rgbfix` to correct the header checksum.

## Conventions
- **Encoding:** The game uses a custom character encoding defined in the `tbl/` files.
- **Configuration:** Most data (enemies, signs, NPCs) is stored in YAML format.
- **Patching:** Intermediate patching is done directly on the ROM binary; final distribution uses IPS patches.
