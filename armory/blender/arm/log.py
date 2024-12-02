"""
CLI output.
"""

import platform
import subprocess
import sys
import bpy

DEBUG = 36
INFO = 37
WARN = 35
ERROR = 31

if platform.system() == "Windows":
    HAS_COLOR_SUPPORT = platform.release() == "10"

    if HAS_COLOR_SUPPORT:
        # Enable ANSI codes. Otherwise, the ANSI sequences might not be
        # evaluated correctly for the first colored print statement.
        import ctypes
        kernel32 = ctypes.windll.kernel32

        # -11: stdout
        handle_out = kernel32.GetStdHandle(-11)

        console_mode = ctypes.c_long()
        kernel32.GetConsoleMode(handle_out, ctypes.byref(console_mode))

        # 0b100: ENABLE_VIRTUAL_TERMINAL_PROCESSING, enables ANSI codes
        # see https://docs.microsoft.com/en-us/windows/console/setconsolemode
        console_mode.value |= 0b100
        kernel32.SetConsoleMode(handle_out, console_mode)
else:
    HAS_COLOR_SUPPORT = True

info_text = ''
num_warnings = 0
num_errors = 0

def clear(clear_warnings=False, clear_errors=False):
    global info_text, num_warnings, num_errors
    info_text = ''
    if clear_warnings:
        num_warnings = 0
    if clear_errors:
        num_errors = 0

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def log(text, color=None):
    print(colorize(text, color))

def debug(text):
    print(colorize(text, DEBUG))

def info(text):
    global info_text
    print(colorize(text, INFO))
    info_text = format_text(text)

def print_warn(text):
    print(colorize('WARNING: ' + text, WARN))

def warn(text):
    global num_warnings
    num_warnings += 1
    print_warn(text)

def error(text):
    global num_errors
    num_errors += 1
    print(colorize('ERROR: ' + text, ERROR), file=sys.stderr)

def colorize(text:str, color=None):
    if bpy.context.area is not None and bpy.context.area.type == 'CONSOLE':
        return text
    if HAS_COLOR_SUPPORT and color is not None:
        csi = '\033['
        text = csi + str(color) + 'm' + text + csi + '0m'
    return text

def warn_called_process_error(proc: subprocess.CalledProcessError):
    out = f'Command {proc.cmd} exited with code {proc.returncode}.'
    if proc.output is not None:
        out += (
            f'Command output:\n'
            f'---------------\n'
            f'{proc.output.decode(encoding="utf-8")}'  # Output is encoded as bytes by default
        )
    warn(out)
