# Jungle Wars Tasks

## dump_script

> Dumps the various parts of the script into yaml files

```powershell
uv run src/jw_script.py yaml-dump 0x4000 0x7CAA --outputfile out/bank_01.yaml
uv run src/jw_script.py yaml-dump 0x20000 0x24000 --outputfile out/bank_08.yaml
uv run src/jw_script.py yaml-dump 0x2e52c 0x2fa9c --outputfile out/bank_0b.yaml
uv run src/jw_script.py yaml-dump 0x38000 0x3bfea --outputfile out/bank_08_0e.yaml
```
