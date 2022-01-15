import bpy, os

def apply_lightmaps():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                hidden = False

                if obj.hide_get():
                    hidden = True
                if obj.hide_viewport:
                    hidden = True
                if obj.hide_render:
                    hidden = True

                if not hidden:

                    for slot in obj.material_slots:
                        mat = slot.material
                        node_tree = mat.node_tree
                        nodes = mat.node_tree.nodes

                        scene = bpy.context.scene

                        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

                        #Find nodes
                        for node in nodes:
                            if node.name == "Baked Image":

                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Finding node source for material: " + mat.name + " @ " + obj.name)

                                extension = ".hdr"

                                postfix = "_baked"

                                if scene.TLM_SceneProperties.tlm_denoise_use:
                                    postfix = "_denoised"
                                if scene.TLM_SceneProperties.tlm_filtering_use:
                                    postfix = "_filtered"

                                if node.image:
                                    node.image.source = "FILE"

                                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                                        print("Atlas object image")
                                        image_name = obj.TLM_ObjectProperties.tlm_atlas_pointer + postfix + extension #TODO FIX EXTENSION
                                    elif obj.TLM_ObjectProperties.tlm_postpack_object:
                                        print("Atlas object image (postpack)")
                                        image_name = obj.TLM_ObjectProperties.tlm_postatlas_pointer + postfix + extension #TODO FIX EXTENSION
                                    else:
                                        print("Baked object image")
                                        image_name = obj.name + postfix + extension #TODO FIX EXTENSION
                                    
                                    node.image.filepath_raw = os.path.join(dirpath, image_name)

def apply_materials(load_atlas=0):

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Applying materials")
        if load_atlas:
            print("- In load Atlas mode")

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                hidden = False

                if obj.hide_get():
                    hidden = True
                if obj.hide_viewport:
                    hidden = True
                if obj.hide_render:
                    hidden = True

                if not hidden:

                    uv_layers = obj.data.uv_layers
                    uv_layers.active_index = 0
                    scene = bpy.context.scene

                    decoding = False

                    #Sort name
                    for slot in obj.material_slots:
                        mat = slot.material
                        if mat.name.endswith('_temp'):
                            old = slot.material
                            slot.material = bpy.data.materials[old.name.split('_' + obj.name)[0]]

                    if(scene.TLM_SceneProperties.tlm_decoder_setup):

                        tlm_rgbm = bpy.data.node_groups.get('RGBM Decode')
                        tlm_rgbd = bpy.data.node_groups.get('RGBD Decode')
                        tlm_logluv = bpy.data.node_groups.get('LogLuv Decode')

                        if tlm_rgbm == None:
                            load_library('RGBM Decode')

                        if tlm_rgbd == None:
                            load_library('RGBD Decode')

                        if tlm_logluv == None:
                            load_library('LogLuv Decode')

                    if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                        tlm_exposure = bpy.data.node_groups.get("Exposure")

                        if tlm_exposure == None:
                            load_library("Exposure")

                    #Apply materials
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print(obj.name)
                    for slot in obj.material_slots:
                        
                        mat = slot.material
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print(slot.material)


                        if not mat.TLM_ignore:

                            node_tree = mat.node_tree
                            nodes = mat.node_tree.nodes

                            foundBakedNode = False

                            #Find nodes
                            for node in nodes:
                                if node.name == "Baked Image":
                                    lightmapNode = node
                                    lightmapNode.location = -1200, 300
                                    lightmapNode.name = "TLM_Lightmap"
                                    foundBakedNode = True
                            
                            # if load_atlas:
                            #     print("Load Atlas for: " + obj.name)
                            #     img_name = obj.TLM_ObjectProperties.tlm_atlas_pointer + '_baked'
                            #     print("Src: " + img_name)
                            # else:
                            #     img_name = obj.name + '_baked'

                            img_name = obj.name + '_baked'

                            if not foundBakedNode:

                                if scene.TLM_EngineProperties.tlm_target == "vertex":

                                    lightmapNode = node_tree.nodes.new(type="ShaderNodeVertexColor")
                                    lightmapNode.location = -1200, 300
                                    lightmapNode.name = "TLM_Lightmap"

                                else:

                                    lightmapNode = node_tree.nodes.new(type="ShaderNodeTexImage")
                                    lightmapNode.location = -1200, 300
                                    lightmapNode.name = "TLM_Lightmap"
                                    lightmapNode.interpolation = bpy.context.scene.TLM_SceneProperties.tlm_texture_interpolation
                                    lightmapNode.extension = bpy.context.scene.TLM_SceneProperties.tlm_texture_extrapolation

                                    if (obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA" and obj.TLM_ObjectProperties.tlm_atlas_pointer != ""):
                                        lightmapNode.image = bpy.data.images[obj.TLM_ObjectProperties.tlm_atlas_pointer + "_baked"]
                                    else:
                                        lightmapNode.image = bpy.data.images[img_name]

                            #Find output node
                            outputNode = nodes[0]
                            if(outputNode.type != "OUTPUT_MATERIAL"):
                                for node in node_tree.nodes:
                                    if node.type == "OUTPUT_MATERIAL":
                                        outputNode = node
                                        break

                            #Find mainnode
                            mainNode = outputNode.inputs[0].links[0].from_node

                            if (mainNode.type == "MIX_SHADER"):
                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Mix shader found")

                                #TODO SHIFT BETWEEN from node input 1 or 2 based on which type
                                mainNode = outputNode.inputs[0].links[0].from_node.inputs[1].links[0].from_node

                            if (mainNode.type == "ADD_SHADER"):
                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Mix shader found")

                                mainNode = outputNode.inputs[0].links[0].from_node.inputs[0].links[0].from_node

                            if (mainNode.type == "ShaderNodeMixRGB"):
                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Mix RGB shader found")
                                
                                mainNode = outputNode.inputs[0].links[0].from_node.inputs[0].links[0].from_node

                            #Add all nodes first
                            #Add lightmap multipliction texture
                            mixNode = node_tree.nodes.new(type="ShaderNodeMixRGB")
                            mixNode.name = "Lightmap_Multiplication"
                            mixNode.location = -800, 300
                            if scene.TLM_EngineProperties.tlm_lighting_mode == "indirect" or scene.TLM_EngineProperties.tlm_lighting_mode == "indirectAO":
                                mixNode.blend_type = 'MULTIPLY'
                            else:
                                mixNode.blend_type = 'MULTIPLY'
                            
                            if scene.TLM_EngineProperties.tlm_lighting_mode == "complete":
                                mixNode.inputs[0].default_value = 0.0
                            else:
                                mixNode.inputs[0].default_value = 1.0

                            UVLightmap = node_tree.nodes.new(type="ShaderNodeUVMap")

                            if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                                uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                            else:
                                uv_channel = "UVMap_Lightmap"

                            UVLightmap.uv_map = uv_channel

                            UVLightmap.name = "Lightmap_UV"
                            UVLightmap.location = -1500, 300

                            if(scene.TLM_SceneProperties.tlm_decoder_setup):
                                if scene.TLM_SceneProperties.tlm_encoding_device == "CPU":
                                    if scene.TLM_SceneProperties.tlm_encoding_mode_a == 'RGBM':
                                        DecodeNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                        DecodeNode.node_tree = bpy.data.node_groups["RGBM Decode"]
                                        DecodeNode.location = -400, 300
                                        DecodeNode.name = "Lightmap_RGBM_Decode"
                                        decoding = True
                                    if scene.TLM_SceneProperties.tlm_encoding_mode_b == "RGBD":
                                        DecodeNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                        DecodeNode.node_tree = bpy.data.node_groups["RGBD Decode"]
                                        DecodeNode.location = -400, 300
                                        DecodeNode.name = "Lightmap_RGBD_Decode"
                                        decoding = True
                                else:
                                    if scene.TLM_SceneProperties.tlm_encoding_mode_b == 'RGBM':
                                        DecodeNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                        DecodeNode.node_tree = bpy.data.node_groups["RGBM Decode"]
                                        DecodeNode.location = -400, 300
                                        DecodeNode.name = "Lightmap_RGBM_Decode"
                                        decoding = True
                                    if scene.TLM_SceneProperties.tlm_encoding_mode_b == "RGBD":
                                        DecodeNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                        DecodeNode.node_tree = bpy.data.node_groups["RGBD Decode"]
                                        DecodeNode.location = -400, 300
                                        DecodeNode.name = "Lightmap_RGBD_Decode"
                                        decoding = True
                                    if scene.TLM_SceneProperties.tlm_encoding_mode_b == "LogLuv":
                                        DecodeNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                        DecodeNode.node_tree = bpy.data.node_groups["LogLuv Decode"]
                                        DecodeNode.location = -400, 300
                                        DecodeNode.name = "Lightmap_LogLuv_Decode"
                                        decoding = True

                                        if scene.TLM_SceneProperties.tlm_split_premultiplied:

                                            lightmapNodeExtra = node_tree.nodes.new(type="ShaderNodeTexImage")
                                            lightmapNodeExtra.location = -1200, 800
                                            lightmapNodeExtra.name = "TLM_Lightmap_Extra"
                                            lightmapNodeExtra.interpolation = bpy.context.scene.TLM_SceneProperties.tlm_texture_interpolation
                                            lightmapNodeExtra.extension = bpy.context.scene.TLM_SceneProperties.tlm_texture_extrapolation
                                            lightmapNodeExtra.image = lightmapNode.image

                                            # #IF OBJ IS USING ATLAS?
                                            # if (obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA" and obj.TLM_ObjectProperties.tlm_atlas_pointer != ""):
                                            #     #lightmapNode.image = bpy.data.images[obj.TLM_ObjectProperties.tlm_atlas_pointer + "_baked"]
                                            #     #print("OBS! OBJ IS USING ATLAS, RESULT WILL BE WRONG!")
                                            #     #bpy.app.driver_namespace["logman"].append("OBS! OBJ IS USING ATLAS, RESULT WILL BE WRONG!")
                                            #     pass
                                            # if (obj.TLM_ObjectProperties.tlm_postpack_object and obj.TLM_ObjectProperties.tlm_postatlas_pointer != ""):
                                            #     #print("OBS! OBJ IS USING ATLAS, RESULT WILL BE WRONG!")
                                            #     #bpy.app.driver_namespace["logman"].append("OBS! OBJ IS USING ATLAS, RESULT WILL BE WRONG!")
                                            #     print()
                                            #     lightmapNodeExtra.image = lightmapNode.image

                                            #lightmapPath = lightmapNode.image.filepath_raw
                                            #print("PREM: " + lightmapPath)

                            if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                                ExposureNode = node_tree.nodes.new(type="ShaderNodeGroup")
                                ExposureNode.node_tree = bpy.data.node_groups["Exposure"]
                                ExposureNode.inputs[1].default_value = scene.TLM_EngineProperties.tlm_exposure_multiplier
                                ExposureNode.location = -500, 300
                                ExposureNode.name = "Lightmap_Exposure"

                            #Add Basecolor node
                            if len(mainNode.inputs[0].links) == 0:
                                baseColorValue = mainNode.inputs[0].default_value
                                baseColorNode = node_tree.nodes.new(type="ShaderNodeRGB")
                                baseColorNode.outputs[0].default_value = baseColorValue
                                baseColorNode.location = ((mainNode.location[0] - 1100, mainNode.location[1] - 300))
                                baseColorNode.name = "Lightmap_BasecolorNode_A"
                            else:
                                baseColorNode = mainNode.inputs[0].links[0].from_node
                                baseColorNode.name = "LM_P"

                            #Linking
                            if decoding and scene.TLM_SceneProperties.tlm_encoding_use:

                                if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                                    
                                    mat.node_tree.links.new(lightmapNode.outputs[0], DecodeNode.inputs[0]) #Connect lightmap node to decodenode

                                    if scene.TLM_SceneProperties.tlm_split_premultiplied:
                                        mat.node_tree.links.new(lightmapNodeExtra.outputs[0], DecodeNode.inputs[1]) #Connect lightmap node to decodenode
                                    else:
                                        mat.node_tree.links.new(lightmapNode.outputs[1], DecodeNode.inputs[1]) #Connect lightmap node to decodenode

                                    mat.node_tree.links.new(DecodeNode.outputs[0], mixNode.inputs[1]) #Connect decode node to mixnode
                                    mat.node_tree.links.new(ExposureNode.outputs[0], mixNode.inputs[1]) #Connect exposure node to mixnode
                                
                                else:
                                    
                                    mat.node_tree.links.new(lightmapNode.outputs[0], DecodeNode.inputs[0]) #Connect lightmap node to decodenode
                                    if scene.TLM_SceneProperties.tlm_split_premultiplied:
                                        mat.node_tree.links.new(lightmapNodeExtra.outputs[0], DecodeNode.inputs[1]) #Connect lightmap node to decodenode
                                    else:
                                        mat.node_tree.links.new(lightmapNode.outputs[1], DecodeNode.inputs[1]) #Connect lightmap node to decodenode

                                    mat.node_tree.links.new(DecodeNode.outputs[0], mixNode.inputs[1]) #Connect lightmap node to mixnode
                                
                                mat.node_tree.links.new(baseColorNode.outputs[0], mixNode.inputs[2]) #Connect basecolor to pbr node
                                mat.node_tree.links.new(mixNode.outputs[0], mainNode.inputs[0]) #Connect mixnode to pbr node

                                if not scene.TLM_EngineProperties.tlm_target == "vertex":
                                    mat.node_tree.links.new(UVLightmap.outputs[0], lightmapNode.inputs[0]) #Connect uvnode to lightmapnode

                                    if scene.TLM_SceneProperties.tlm_split_premultiplied:
                                        mat.node_tree.links.new(UVLightmap.outputs[0], lightmapNodeExtra.inputs[0]) #Connect uvnode to lightmapnode

                            else:

                                if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                                    mat.node_tree.links.new(lightmapNode.outputs[0], ExposureNode.inputs[0]) #Connect lightmap node to mixnode
                                    mat.node_tree.links.new(ExposureNode.outputs[0], mixNode.inputs[1]) #Connect lightmap node to mixnode
                                else:
                                    mat.node_tree.links.new(lightmapNode.outputs[0], mixNode.inputs[1]) #Connect lightmap node to mixnode
                                mat.node_tree.links.new(baseColorNode.outputs[0], mixNode.inputs[2]) #Connect basecolor to pbr node
                                mat.node_tree.links.new(mixNode.outputs[0], mainNode.inputs[0]) #Connect mixnode to pbr node
                                if not scene.TLM_EngineProperties.tlm_target == "vertex":
                                    mat.node_tree.links.new(UVLightmap.outputs[0], lightmapNode.inputs[0]) #Connect uvnode to lightmapnode

                            #If skip metallic
                            if scene.TLM_SceneProperties.tlm_metallic_clamp == "skip":
                                if mainNode.inputs[4].default_value > 0.1: #DELIMITER
                                    moutput = mainNode.inputs[0].links[0].from_node
                                    mat.node_tree.links.remove(moutput.outputs[0].links[0])

def exchangeLightmapsToPostfix(ext_postfix, new_postfix, formatHDR=".hdr"):

    if not bpy.context.scene.TLM_EngineProperties.tlm_target == "vertex":

        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print(ext_postfix, new_postfix, formatHDR)

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                    #Here
                    #If the object is part of atlas
                    print("CHECKING FOR REPART")
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA": #TODO, ALSO CONFIGURE FOR POSTATLAS

                        if bpy.context.scene.TLM_AtlasList[obj.TLM_ObjectProperties.tlm_atlas_pointer].tlm_atlas_merge_samemat:

                            #For each material we check if it ends with a number
                            for slot in obj.material_slots:

                                part = slot.name.rpartition('.')
                                if part[2].isnumeric() and part[0] in bpy.data.materials:

                                    print("Material for obj: " + obj.name + " was numeric, and the material: " + part[0] + " was found.")
                                    slot.material = bpy.data.materials.get(part[0])


                            
                            # for slot in obj.material_slots:
                            #     mat = slot.material
                            #     node_tree = mat.node_tree
                            #     nodes = mat.node_tree.nodes

                    try:

                        hidden = False

                        if obj.hide_get():
                            hidden = True
                        if obj.hide_viewport:
                            hidden = True
                        if obj.hide_render:
                            hidden = True

                        if not hidden:

                            for slot in obj.material_slots:
                                mat = slot.material
                                node_tree = mat.node_tree
                                nodes = mat.node_tree.nodes

                                for node in nodes:
                                    if node.name == "Baked Image" or node.name == "TLM_Lightmap":
                                        img_name = node.image.filepath_raw
                                        cutLen = len(ext_postfix + formatHDR)
                                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                            print("Len:" + str(len(ext_postfix + formatHDR)) + "|" + ext_postfix + ".." + formatHDR)

                                        #Simple way to sort out objects with multiple materials
                                        if formatHDR == ".hdr" or formatHDR == ".exr":
                                            if not node.image.filepath_raw.endswith(new_postfix + formatHDR):
                                                print("Node1: " + node.image.filepath_raw + " => " + img_name[:-cutLen] + new_postfix + formatHDR)
                                                node.image.filepath_raw = img_name[:-cutLen] + new_postfix + formatHDR
                                        else:
                                            cutLen = len(ext_postfix + ".hdr")
                                            if not node.image.filepath_raw.endswith(new_postfix + formatHDR):
                                                if not node.image.filepath_raw.endswith("_XYZ.png"):
                                                    print("Node2: " + node.image.filepath_raw + " => " + img_name[:-cutLen] + new_postfix + formatHDR)
                                                    node.image.filepath_raw = img_name[:-cutLen] + new_postfix + formatHDR

                                for node in nodes:
                                    if bpy.context.scene.TLM_SceneProperties.tlm_encoding_use and bpy.context.scene.TLM_SceneProperties.tlm_encoding_mode_b == "LogLuv": 
                                        if bpy.context.scene.TLM_SceneProperties.tlm_split_premultiplied:
                                            if node.name == "TLM_Lightmap":
                                                img_name = node.image.filepath_raw
                                                print("PREM Main: " + img_name)
                                                if node.image.filepath_raw.endswith("_encoded.png"):
                                                    print(node.image.filepath_raw + " => " + node.image.filepath_raw[:-4] + "_XYZ.png")
                                                if not node.image.filepath_raw.endswith("_XYZ.png"):
                                                    node.image.filepath_raw = node.image.filepath_raw[:-4] + "_XYZ.png"
                                            if node.name == "TLM_Lightmap_Extra":
                                                img_path = node.image.filepath_raw[:-8] + "_W.png"
                                                img = bpy.data.images.load(img_path)
                                                node.image = img
                                                bpy.data.images.load(img_path)
                                                print("PREM Extra: " + img_path)
                                                node.image.filepath_raw = img_path
                                                node.image.colorspace_settings.name = "Linear"

                    except:

                        print("Error occured with postfix change for obj: " + obj.name)

    for image in bpy.data.images:
        image.reload()

def applyAOPass():

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                hidden = False

                if obj.hide_get():
                    hidden = True
                if obj.hide_viewport:
                    hidden = True
                if obj.hide_render:
                    hidden = True

                if not hidden:

                    for slot in obj.material_slots:
                        mat = slot.material
                        node_tree = mat.node_tree
                        nodes = mat.node_tree.nodes

                        for node in nodes:
                            if node.name == "Baked Image" or node.name == "TLM_Lightmap":

                                filepath = bpy.data.filepath
                                dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

                                LightmapPath = node.image.filepath_raw

                                filebase = os.path.basename(LightmapPath)
                                filename = os.path.splitext(filebase)[0]
                                extension = os.path.splitext(filebase)[1]
                                AOImagefile = filename[:-4] + "_ao"
                                AOImagePath = os.path.join(dirpath, AOImagefile + extension)

                                AOMap = nodes.new('ShaderNodeTexImage')
                                AOMap.name = "TLM_AOMap"
                                AOImage = bpy.data.images.load(AOImagePath)
                                AOMap.image = AOImage
                                AOMap.location = -800, 0

                                AOMult = nodes.new(type="ShaderNodeMixRGB")
                                AOMult.name = "TLM_AOMult"
                                AOMult.blend_type = 'MULTIPLY'
                                AOMult.inputs[0].default_value = 1.0
                                AOMult.location = -300, 300

                                multyNode = nodes["Lightmap_Multiplication"]
                                mainNode = nodes["Principled BSDF"]
                                UVMapNode = nodes["Lightmap_UV"]

                                node_tree.links.remove(multyNode.outputs[0].links[0])

                                node_tree.links.new(multyNode.outputs[0], AOMult.inputs[1])
                                node_tree.links.new(AOMap.outputs[0], AOMult.inputs[2])
                                node_tree.links.new(AOMult.outputs[0], mainNode.inputs[0])
                                node_tree.links.new(UVMapNode.outputs[0], AOMap.inputs[0])

def load_library(asset_name):

    scriptDir = os.path.dirname(os.path.realpath(__file__))

    if bpy.data.filepath.endswith('tlm_data.blend'): # Prevent load in library itself
        return

    data_path = os.path.abspath(os.path.join(scriptDir, '..', '..', 'assets/tlm_data.blend'))
    data_names = [asset_name]

    # Import
    data_refs = data_names.copy()
    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = data_refs

    for ref in data_refs:
        ref.use_fake_user = True