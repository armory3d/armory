import bpy, os

def bake():

    for obj in bpy.data.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(False)

    iterNum = 0
    currentIterNum = 0

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                iterNum = iterNum + 1

    if iterNum > 1:
        iterNum = iterNum - 1

    for obj in bpy.data.objects:
        if obj.type == 'MESH':

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                scene = bpy.context.scene

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                obs = bpy.context.view_layer.objects
                active = obs.active
                obj.hide_render = False
                scene.render.bake.use_clear = False

                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    print("Baking " + str(currentIterNum) + "/" + str(iterNum) + " (" + str(round(currentIterNum/iterNum*100, 2)) + "%) : " + obj.name)

                if scene.TLM_EngineProperties.tlm_lighting_mode == "combined" or scene.TLM_EngineProperties.tlm_lighting_mode == "combinedAO":
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "indirect" or scene.TLM_EngineProperties.tlm_lighting_mode == "indirectAO":
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "ao":
                    bpy.ops.object.bake(type="AO", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "complete":
                    bpy.ops.object.bake(type="COMBINED", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)         
                else:
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                
                bpy.ops.object.select_all(action='DESELECT')
                currentIterNum = currentIterNum + 1

    for image in bpy.data.images:
        if image.name.endswith("_baked"):

            saveDir = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
            bakemap_path = os.path.join(saveDir, image.name)
            filepath_ext = ".hdr"
            image.filepath_raw = bakemap_path + filepath_ext
            image.file_format = "HDR"
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Saving to: " + image.filepath_raw)
            image.save()