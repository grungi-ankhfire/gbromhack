import click

class ParamTypeBasedInt(click.ParamType):
    name = 'int'

    def convert(self, value, param, ctx):
        if isinstance(value, int):
            return value
        
        try:
            if value[:2] == "0x":
                return int(value, 16)
            elif value[:2] == "0b":
                return int(value, 2)
            return int(value)
        except ValueError:
            self.fail('%s is not a valid integer' % value, param, ctx)

BASED_INT = ParamTypeBasedInt()
