import bpy, os

def bake():

    cam_name = "TLM-BakeCam-obj"

    if cam_name in bpy.context.scene.objects:

        print("Camera found...")

        camera = bpy.context.scene.objects[cam_name]

        camera.data.octane.baking_camera = True

        for obj in bpy.context.scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(False)

        iterNum = 2
        currentIterNum = 1

        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    iterNum = iterNum + 1

        if iterNum > 1:
            iterNum = iterNum - 1

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                    currentIterNum = currentIterNum + 1

                    scene = bpy.context.scene

                    print("Baking obj: " + obj.name)

                    print("Baking ID: " + str(currentIterNum) + " out of " + str(iterNum))

                    bpy.ops.object.select_all(action='DESELECT')

                    camera.data.octane.baking_group_id = currentIterNum

                    savedir = os.path.dirname(bpy.data.filepath)
                    user_dir = scene.TLM_Engine3Properties.tlm_lightmap_savedir
                    directory = os.path.join(savedir, user_dir)

                    image_settings = bpy.context.scene.render.image_settings
                    image_settings.file_format = "HDR"
                    image_settings.color_depth = '32'

                    filename = os.path.join(directory, "LM") + "_" + obj.name + ".hdr"
                    bpy.context.scene.render.filepath = filename

                    resolution = int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution)

                    bpy.context.scene.render.resolution_x = resolution
                    bpy.context.scene.render.resolution_y = resolution

                    bpy.ops.render.render(write_still=True)

    else:

        print("No baking camera found")




    print("Baking in Octane!")