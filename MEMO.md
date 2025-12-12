# gbromhack memo (Jungle Wars GB)

This memo is a “context reload” so I can quickly resume work later.

## Repo purpose
- Tools/scripts to patch + translate the Game Boy game “Jungle Wars”.
- Output ROM: `scripts/roms/jw_patched.gb`
- Input ROM: `scripts/roms/jw_original.gb`

## Build pipeline (Linux)
- Main entry: `build.sh`
  - Copies `scripts/roms/jw_original.gb` → `scripts/roms/jw_patched.gb`
  - Applies binary patches via `scripts/jw_patcher.py`:
    - `scripts/patches/font.patch` at font offsets (`--font`)
    - `scripts/patches/extension_jump.patch` at `0x0BAD`
    - `scripts/patches/extension_new_code.patch` at `0x40000` (bank `0x10`)
    - `scripts/patches/win_moved_code.patch` at `0x7C700` (bank `0x1F`)
  - Applies logic patches via `scripts/jw_patcher.py`:
    - `apply_windows`, `apply_enemies`, `apply_npcs`
  - Inserts translated text via `scripts/jw_translation.py`:
    - windows (`scripts/translation/jw_windows.yaml`)
    - main script (`scripts/jw_translation.yaml`)
    - enemies (`scripts/translation/jw_enemies.yaml`)
    - signs (`scripts/translation/jw_signs.yaml`)
    - npcs (`scripts/translation/jw_npcs.yaml`)
  - Runs `rgbfix` if available.

## Where things live
- Translation tables: `tbl/*.tbl`
  - `tbl/jw-py-en.tbl` contains token→byte mappings (e.g. `<enemy>=F4`, `<FD>=FD`, `<FE>=FE`, `<FF>=FF`).
- Window definitions: `scripts/translation/jw_windows.yaml`
  - Includes geometry (`dim_x`, `dim_y`, `pos_x`, `pos_y`, `bg_map`) and `translation` strings.
- Enemy names: `scripts/translation/jw_enemies.yaml`
- General script/combat strings: `scripts/jw_translation.yaml`
- Patches:
  - `scripts/patches/extension_jump.patch`: 8-byte hook at `0x0BAD` (bank switch + call/jump glue)
  - `scripts/patches/extension_new_code.patch`: code payload written at `0x40000` (bank `0x10`)
  - `scripts/patches/win_moved_code.patch`: moved routine payload written at `0x7C700` (bank `0x1F`)

## Key gotchas / bugs we hit

### 1) Patch payloads can be swapped → ROM crashes later
- Symptom: game runs “for a while” then crashes when a hooked routine executes.
- Cause: wrong payload written to `0x40000` vs `0x7C700`.
- Mitigation: `build.sh` now sanity-checks patch headers and verifies ROM bytes at key offsets.

### 2) Bank restore is mandatory for hooks called from banked code
- Symptom: crash immediately when entering first battle.
- Root cause: enemy-name hook switched to bank `0x1F` and didn’t restore the previous bank, so returning to banked battle code executed the wrong bank.
- Fix: `scripts/jw_patcher.py` enemy-name trampoline at `0x0F95` now:
  - Saves current bank from HRAM `$FFA5`
  - Switches to bank `0x1F`, calls helper at `$4100`
  - Restores original bank, then continues at `$0FA4`

### 3) Combat target menu layout assumes enemy name width
- Symptom: enemy-target selection menu wraps oddly; words spill onto next line.
- Root cause: UI/control-code length assumptions treat `<enemy>` as an 8-character slot; a 9-char enemy name overflowed.
- Fix: keep translated enemy names within the UI slot (e.g., shortened enemy `0x21` from `CheatyFox` → `SlyFox`).

### 4) Malformed control codes in YAML break rendering
- Examples fixed:
  - `<senemy>` (invalid token) → `<enemy>`
  - `[FC]` (not a valid token) → `<FC>` (which maps to byte `0xFC`)
  - Ensure lines end with `<FF>` where required
- Quick validation approach: any translation string must be fully tokenizable by `tbl/jw-py-en.tbl` (after normalizing `<br>` → `<FE>` for validation).

## Useful offsets (from our investigation)
- `0x0BAD`: extension hook location
- `0x40000` (bank `0x10`): extension code payload start
- `0x7C700` (bank `0x1F`): moved routine payload start
- `0x0F95`: enemy-name redirection hook site in fixed bank
- `0x7C100` (bank `0x1F`, addr `$4100`): enemy-name helper routine location

## Commits that mattered (for archaeology)
- `95debe5`: fix swapped ROM patch payloads (initial)
- `27566c4`: fix patch bank placement regression
- `923e4ef`: fix first-battle crash by restoring bank in enemy-name hook
- `2795b2b`: fix combat target menu overflow + broken control codes

## Debugging checklist (future)
- If a crash is “timing dependent”: suspect bank switch / hook returns / overwritten code region.
- If UI text wraps strangely: check special-token lengths (`SPECIAL_BYTES` in `scripts/jw_translation.py`) and fixed-width UI assumptions (notably `<enemy>`=8).
- If text is garbled: check YAML for tokens not in `tbl/jw-py-en.tbl` and missing `<FF>`.
