import os
import pyaml
from typing import Any

class YamlWriter:
    def __init__(self, output_file: str | os.PathLike):
        self.output_file = output_file

    def dump(self, data: Any):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(pyaml.dump(data, indent=2, width=float("inf"), string_val_style='"'))

    def __repr__(self) -> str:
        return f"YamlWriter for {self.output_file}"
