import props_ui
import space_armory
import utils

progress = 100.0
tag_redraw = False

def clear():
    props_ui.ArmoryProjectPanel.info_text = ''
    if utils.with_chromium():
        space_armory.ArmorySpaceHeader.info_text = ''

def format_text(text):
    return (text[:80] + '..') if len(text) > 80 else text # Limit str size

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
