import bpy
from addon_utils import enable
from bpy.app.handlers import persistent

@persistent
def on_scene_update_post(scene):
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    # Enable addon by default for Armory integrated in Blender
    user_preferences = bpy.context.user_preferences
    if not 'armory' in user_preferences.addons:
        enable('armory', default_set=True, persistent=True, handle_error=None)
        bpy.ops.wm.save_userpref()

def register():
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.append(on_scene_update_post)

def unregister():
    pass

if __name__ == "__main__":
    register()
