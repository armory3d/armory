import bpy, os, time, blf, webbrowser
from .. utility import build
from .. utility.cycles import cache

class TLM_BuildLightmaps(bpy.types.Operator):
    bl_idname = "tlm.build_lightmaps"
    bl_label = "Build Lightmaps"
    bl_description = "Build Lightmaps"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):

        #Add progress bar from 0.15

        print("MODAL")

        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        if not bpy.app.background:

            build.prepare_build(self, False)

        else:

            print("Running in background mode. Contextual operator not available. Use command 'thelightmapper.addon.build.prepare_build()'")

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        pass

    def draw_callback_px(self, context, event):
        pass

class TLM_CleanLightmaps(bpy.types.Operator):
    bl_idname = "tlm.clean_lightmaps"
    bl_label = "Clean Lightmaps"
    bl_description = "Clean Lightmaps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        filepath = bpy.data.filepath
        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)
        if os.path.isdir(dirpath):
            for file in os.listdir(dirpath):
                os.remove(os.path.join(dirpath + "/" + file))

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    cache.backup_material_restore(obj)

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    cache.backup_material_rename(obj)

        for mat in bpy.data.materials:
            if mat.users < 1:
                bpy.data.materials.remove(mat)

        for mat in bpy.data.materials:
            if mat.name.startswith("."):
                if "_Original" in mat.name:
                    bpy.data.materials.remove(mat)

        for image in bpy.data.images:
            if image.name.endswith("_baked"):
                bpy.data.images.remove(image, do_unlink=True)

        return {'FINISHED'}

class TLM_ExploreLightmaps(bpy.types.Operator):
    bl_idname = "tlm.explore_lightmaps"
    bl_label = "Explore Lightmaps"
    bl_description = "Explore Lightmaps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene
        cycles = scene.cycles

        if not bpy.data.is_saved:
            self.report({'INFO'}, "Please save your file first")
            return {"CANCELLED"}

        filepath = bpy.data.filepath
        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

        if os.path.isdir(dirpath):
            webbrowser.open('file://' + dirpath)
        else:
            os.mkdir(dirpath)
            webbrowser.open('file://' + dirpath)

        return {'FINISHED'}

class TLM_EnableSelection(bpy.types.Operator):
    """Enable for selection"""
    bl_idname = "tlm.enable_selection"
    bl_label = "Enable for selection"
    bl_description = "Enable for selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        for obj in bpy.context.selected_objects:
            obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = True

            if scene.TLM_SceneProperties.tlm_override_object_settings:
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = scene.TLM_SceneProperties.tlm_mesh_lightmap_resolution
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = scene.TLM_SceneProperties.tlm_mesh_lightmap_unwrap_mode
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_margin = scene.TLM_SceneProperties.tlm_mesh_unwrap_margin

        return{'FINISHED'}

class TLM_DisableSelection(bpy.types.Operator):
    """Disable for selection"""
    bl_idname = "tlm.disable_selection"
    bl_label = "Disable for selection"
    bl_description = "Disable for selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = False

        return{'FINISHED'}

class TLM_RemoveLightmapUV(bpy.types.Operator):
    """Remove Lightmap UV for selection"""
    bl_idname = "tlm.remove_uv_selection"
    bl_label = "Remove Lightmap UV"
    bl_description = "Remove Lightmap UV for selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                uv_layers = obj.data.uv_layers

                for uvlayer in uv_layers:
                    if uvlayer.name == "UVMap_Lightmap":
                        uv_layers.remove(uvlayer)

        return{'FINISHED'}