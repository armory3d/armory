
info_text = ''

def clear():
    global info_text
    info_text = ''

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size    

def print_info(text):
    global info_text
    print(text)
    info_text = format_text(text)

def warn(text):
    print('Armory Warning: ' + text)
