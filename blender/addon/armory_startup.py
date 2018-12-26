import bpy
from addon_utils import enable
from bpy.app.handlers import persistent

@persistent
def handler(scene):
    blenderVersion = bpy.app.version_string
    if blenderVersion.find('2.7') != -1:
        user_preferences = bpy.context.user_preferences
    elif blenderVersion.find('2.8') != -1:
        user_preferences = bpy.context.preferences
    if not 'armory' in user_preferences.addons:
        enable('armory', default_set=True, persistent=True, handle_error=None)
        bpy.ops.wm.save_userpref()

def register():
    bpy.app.handlers.load_post.append(handler)

def unregister():
    pass

if __name__ == "__main__":
    register()
