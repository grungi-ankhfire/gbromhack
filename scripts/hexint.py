"""hexint.py - Helper class to enforce hexadecimal representation in YAML dumps."""
import yaml
import pyaml


class HexInt(int):
    def __new__(cls, value: int, digits: int = 2):
        obj = int.__new__(cls, int(value))
        obj.digits = digits
        return obj


def hexint_representer(dumper, data: int) -> yaml.ScalarNode:
    return yaml.ScalarNode('tag:yaml.org,2002:int', "{0:#0{1}x}".format(data, data.digits + 2))

pyaml.add_representer(HexInt, hexint_representer)
