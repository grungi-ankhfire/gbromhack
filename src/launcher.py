import click
import subprocess
import platform
import sys
from ips_util import Patch
from jw_config import config, path

emulator = path(config["emulator"])
original_rom = path(config["original_rom"])
patched_rom = path(config["patched_rom"])

# set system/version dependent "start_new_session" analogs
run_kwargs = {}
if platform.system() == 'Windows':
    # from msdn [1]
    flags = 0
    flags |= 0x00000008  # DETACHED_PROCESS
    flags |= 0x00000200  # CREATE_NEW_PROCESS_GROUP
    flags |= 0x08000000  # CREATE_NO_WINDOW
    run_kwargs.update(creationflags=flags, close_fds=True)  
elif sys.version_info < (3, 2):  # assume posix
    run_kwargs.update(preexec_fn=os.setsid)
else:  # Python 3.2+ and Unix
    run_kwargs.update(start_new_session=True)


@click.group()
def cli():
    pass


@cli.command
def run_original():
    print("Launching original rom...")
    subprocess.Popen([emulator, original_rom], **run_kwargs)


@cli.command
def run_patched():
    print("Launching patched rom...")
    subprocess.Popen([emulator, patched_rom], **run_kwargs)


@cli.command
def make_patch():
    print("Making patch...")
    print("└─Step 1 : Fixing header using RGBDS")
    subprocess.run(["rgbfix", "-p 0x00", patched_rom])
    print("└─Step 2 : Outputting file")
    # subprocess.run(["ips_util", "create", "rom", original_rom, patched_rom, "-o", f"JungleWars_EnglishPatch_{config["patch_version"]}.ips"])
    with open(original_rom, 'rb') as original:
        with open(patched_rom, 'rb') as patched:
            patch = Patch.create(original.read(), patched.read())

    with open(path(config["output_dir"]) / f"JungleWars_EnglishPatch_{config['patch_version']}.ips", "wb") as output:
        output.write(patch.encode())


if __name__ == "__main__":
    cli()
