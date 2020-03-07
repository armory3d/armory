info_text = ''
num_warnings = 0

def clear(clear_warnings=False):
    global info_text, num_warnings
    info_text = ''
    if clear_warnings:
        num_warnings = 0

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def print_info(text):
    global info_text
    print(text)
    info_text = format_text(text)

def warn(text):
    global num_warnings
    num_warnings += 1
    print('Armory Warning: ' + text)
