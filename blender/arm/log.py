DEBUG = 36
INFO = 37
WARN = 35
ERROR = 31

no_colors = False
info_text = ''
num_warnings = 0

def clear(clear_warnings=False):
    global info_text, num_warnings
    info_text = ''
    if clear_warnings:
        num_warnings = 0

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def log(text,color=None):
    if not no_colors and color is not None:
        csi = '\033['
        text = csi + str(color) + 'm' + text + csi + '0m';
    print(text)

def debug(text):
    log(text,DEBUG)

def info(text):
    global info_text
    log(text,INFO)
    info_text = format_text(text)

def print_warn(text):
    log('Warning: ' + text,WARN)

def warn(text):
    global num_warnings
    num_warnings += 1
    print_warn(text)

def error(text):
    log('ERROR: ' + text,ERROR)
