import props_ui
import space_armory
import armutils
import bridge

progress = 100.0
tag_redraw = False

def clear():
    props_ui.ArmoryProjectPanel.info_text = ''
    if armutils.with_chromium():
        space_armory.ArmorySpaceHeader.info_text = ''

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

def electron_trace(text):
    txt = text.split(' ', 1)
    if len(txt) > 1 and txt[1].startswith('__arm'):
        bridge.parse_operator(text)
    else:
        print_info(text)

def print_info(text):
    global tag_redraw
    print(text)
    props_ui.ArmoryProjectPanel.info_text = format_text(text)
    tag_redraw = True  

def print_player(text):
    print(text)
    space_armory.ArmorySpaceHeader.info_text = format_text(text)

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
