import platform

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
        # -11: stdout, 7 (0b111): ENABLE_PROCESSED_OUTPUT, ENABLE_WRAP_AT_EOL_OUTPUT, ENABLE_VIRTUAL_TERMINAL_PROCESSING
        # see https://docs.microsoft.com/en-us/windows/console/setconsolemode
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
else:
    HAS_COLOR_SUPPORT = True

info_text = ''
num_warnings = 0

def clear(clear_warnings=False):
    global info_text, num_warnings
    info_text = ''
    if clear_warnings:
        num_warnings = 0

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def log(text, color=None):
    if HAS_COLOR_SUPPORT and color is not None:
        csi = '\033['
        text = csi + str(color) + 'm' + text + csi + '0m'
    print(text)

def debug(text):
    log(text, DEBUG)

def info(text):
    global info_text
    log(text, INFO)
    info_text = format_text(text)

def print_warn(text):
    log('Warning: ' + text, WARN)

def warn(text):
    global num_warnings
    num_warnings += 1
    print_warn(text)

def error(text):
    log('ERROR: ' + text, ERROR)
