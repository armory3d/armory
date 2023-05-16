import bpy
from bpy.utils import register_class, unregister_class
from . import addon_preferences
#from . import build, clean, explore, encode, installopencv

classes = [
    addon_preferences.TLM_AddonPreferences
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)