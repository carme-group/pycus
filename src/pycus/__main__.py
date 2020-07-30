from . import commands

if __name__ != "__main__":
    raise ImportError("This module should not be imported")

commands.main_command.run()
