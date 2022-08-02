import bpy, os
from .. import build
from time import time, sleep

def bake(plus_pass=0):

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Initializing lightmap baking.")

    for obj in bpy.context.scene.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(False)

    iterNum = 0
    currentIterNum = 0

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:

            hidden = False

            #We check if the object is hidden
            if obj.hide_get():
                hidden = True
            if obj.hide_viewport:
                hidden = True
            if obj.hide_render:
                hidden = True

            #We check if the object's collection is hidden
            collections = obj.users_collection

            for collection in collections:

                if collection.hide_viewport:
                    hidden = True
                if collection.hide_render:
                    hidden = True
                    
                try:
                    if collection.name in bpy.context.scene.view_layers[0].layer_collection.children:
                        if bpy.context.scene.view_layers[0].layer_collection.children[collection.name].hide_viewport:
                            hidden = True
                except:
                    print("Error: Could not find collection: " + collection.name)

                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use and not hidden:
                    iterNum = iterNum + 1

    if iterNum > 1:
        iterNum = iterNum - 1

    for obj in bpy.context.scene.objects:

        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("Checking visibility status for object and collections: " + obj.name)

        hidden = False

        #We check if the object is hidden
        if obj.hide_get():
            hidden = True
        if obj.hide_viewport:
            hidden = True
        if obj.hide_render:
            hidden = True

        #We check if the object's collection is hidden
        collections = obj.users_collection

        for collection in collections:

            if collection.hide_viewport:
                hidden = True
            if collection.hide_render:
                hidden = True
                
            try:
                if collection.name in bpy.context.scene.view_layers[0].layer_collection.children:
                    if bpy.context.scene.view_layers[0].layer_collection.children[collection.name].hide_viewport:
                        hidden = True
            except:
                print("Error: Could not find collection: " + collection.name)

        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use and not hidden:

                scene = bpy.context.scene

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                obs = bpy.context.view_layer.objects
                active = obs.active
                obj.hide_render = False
                scene.render.bake.use_clear = False

                #os.system("cls")

                #if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Baking " + str(currentIterNum) + "/" + str(iterNum) + " (" + str(round(currentIterNum/iterNum*100, 2)) + "%) : " + obj.name)
                #elapsed = build.sec_to_hours((time() - bpy.app.driver_namespace["tlm_start_time"]))
                #print("Baked: " + str(currentIterNum) + " | Left: " + str(iterNum-currentIterNum))
                elapsedSeconds = time() - bpy.app.driver_namespace["tlm_start_time"]
                bakedObjects = currentIterNum
                bakedLeft = iterNum-currentIterNum
                if bakedObjects == 0:
                    bakedObjects = 1
                averagePrBake = elapsedSeconds / bakedObjects
                remaining = averagePrBake * bakedLeft
                #print(time() - bpy.app.driver_namespace["tlm_start_time"])
                print("Elapsed time: " + str(round(elapsedSeconds, 2)) + "s | ETA remaining: " + str(round(remaining, 2)) + "s") #str(elapsed[0])
                #print("Averaged: " + str(averagePrBake))
                #print("Remaining: " + str(remaining))

                if scene.TLM_EngineProperties.tlm_target == "vertex":
                    scene.render.bake.target = "VERTEX_COLORS"

                if scene.TLM_EngineProperties.tlm_lighting_mode == "combined":
                    print("Baking combined: Direct + Indirect")
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "indirect":
                    print("Baking combined: Indirect")
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "ao":
                    print("Baking combined: AO")
                    bpy.ops.object.bake(type="AO", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "combinedao":

                    if bpy.app.driver_namespace["tlm_plus_mode"] == 1:
                        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                    elif bpy.app.driver_namespace["tlm_plus_mode"] == 2:
                        bpy.ops.object.bake(type="AO", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)

                elif scene.TLM_EngineProperties.tlm_lighting_mode == "indirectao":

                    print("IndirAO")
                    
                    if bpy.app.driver_namespace["tlm_plus_mode"] == 1:
                        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                    elif bpy.app.driver_namespace["tlm_plus_mode"] == 2:
                        bpy.ops.object.bake(type="AO", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                
                elif scene.TLM_EngineProperties.tlm_lighting_mode == "complete":
                    bpy.ops.object.bake(type="COMBINED", margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)
                else:
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT","INDIRECT"}, margin=scene.TLM_EngineProperties.tlm_dilation_margin, use_clear=False)

                
                #Save image between
                if scene.TLM_SceneProperties.tlm_save_preprocess_lightmaps:
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
