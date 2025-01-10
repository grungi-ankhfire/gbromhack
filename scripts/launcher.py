import click
import subprocess
import platform
import sys

emulator = "../../bgb/bgb64.exe"
original_rom = "roms/jw_original.gb"
patched_rom = "roms/jw_patched.gb"

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


if __name__ == "__main__":
    cli()
