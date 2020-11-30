import bpy, os, time

class TLM_ImageUpscale(bpy.types.Operator):
    bl_idname = "tlm.image_upscale"
    bl_label = "Upscale image"
    bl_description = "Upscales the image to double resolution"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        print("Upscale")

        return {'RUNNING_MODAL'}

class TLM_ImageDownscale(bpy.types.Operator):
    bl_idname = "tlm.image_downscale"
    bl_label = "Downscale image"
    bl_description = "Downscales the image to double resolution"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        print("Downscale")

        return {'RUNNING_MODAL'}