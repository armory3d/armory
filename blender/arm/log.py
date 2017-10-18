import arm.utils
import arm.bridge as bridge
import arm.make_state as state

progress = 100.0
tag_redraw = False
info_text = ''
header_info_text = ''

def clear():
    global info_text
    global header_info_text
    info_text = ''
    if arm.utils.with_krom():
        header_info_text = ''

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def krom_trace(text):
    txt = text.split(' ', 1)
    if len(txt) > 1 and txt[1].startswith('__arm'):
        bridge.parse_operator(txt[1])
    else:
        print_info(text)

def print_info(text):
    global tag_redraw
    global info_text
    print(text)
    info_text = format_text(text)
    tag_redraw = True  

def print_player(text):
    global header_info_text
    if state.krom_running:
        header_info_text = format_text(text)

def print_progress(value):
    global progress
    global tag_redraw
    progress = value
    tag_redraw = True 

def get_progress(self):
    global progress
    return progress

def warn(text):
    print('Armory Warning: ' + text)
