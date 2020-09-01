import bpy, os

def apply_lightmaps():
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                for slot in obj.material_slots:
                    mat = slot.material
                    node_tree = mat.node_tree
                    nodes = mat.node_tree.nodes

                    scene = bpy.context.scene

                    dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

                    #Find nodes
                    for node in nodes:
                        if node.name == "Baked Image":

                            extension = ".hdr"

                            postfix = "_baked"

                            if scene.TLM_SceneProperties.tlm_denoise_use:
                               postfix = "_denoised"
                            if scene.TLM_SceneProperties.tlm_filtering_use:
                                postfix = "_filtered"

                            node.image.source = "FILE"
                            image_name = obj.name + postfix + extension #TODO FIX EXTENSION
                            node.image.filepath_raw = os.path.join(dirpath, image_name)


def apply_materials():
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

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

                if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                    tlm_exposure = bpy.data.node_groups.get("Exposure")

                    if tlm_exposure == None:
                        load_library("Exposure")

                #Apply materials
                print(obj.name)
                for slot in obj.material_slots:
                    mat = slot.material
                    print(slot.material)

                    node_tree = mat.node_tree
                    nodes = mat.node_tree.nodes

                    foundBakedNode = False

                    #Find nodes
                    for node in nodes:
                        if node.name == "Baked Image":
                            lightmapNode = node
                            lightmapNode.location = -800, 300
                            lightmapNode.name = "TLM_Lightmap"
                            foundBakedNode = True
                    
                    img_name = obj.name + '_baked'

                    if not foundBakedNode:
                        lightmapNode = node_tree.nodes.new(type="ShaderNodeTexImage")
                        lightmapNode.location = -300, 300
                        lightmapNode.image = bpy.data.images[img_name]
                        lightmapNode.name = "TLM_Lightmap"
                        lightmapNode.interpolation = "Smart"

                    #Find output node
                    outputNode = nodes[0]
                    if(outputNode.type != "OUTPUT_MATERIAL"):
                        for node in node_tree.nodes:
                            if node.type == "OUTPUT_MATERIAL":
                                outputNode = node
                                break

                    #Find mainnode
                    mainNode = outputNode.inputs[0].links[0].from_node

                    #Add all nodes first
                    #Add lightmap multipliction texture
                    mixNode = node_tree.nodes.new(type="ShaderNodeMixRGB")
                    mixNode.name = "Lightmap_Multiplication"
                    mixNode.location = -300, 300
                    mixNode.blend_type = 'MULTIPLY'
                    mixNode.inputs[0].default_value = 1.0

                    UVLightmap = node_tree.nodes.new(type="ShaderNodeUVMap")
                    UVLightmap.uv_map = "UVMap_Lightmap"
                    UVLightmap.name = "Lightmap_UV"
                    UVLightmap.location = -1000, 300

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
                        baseColorNode.location = ((mainNode.location[0] - 500, mainNode.location[1] - 300))
                        baseColorNode.name = "Lightmap_BasecolorNode_A"
                    else:
                        baseColorNode = mainNode.inputs[0].links[0].from_node
                        baseColorNode.name = "LM_P"

                    #Linking
                    if(scene.TLM_EngineProperties.tlm_exposure_multiplier > 0):
                        mat.node_tree.links.new(lightmapNode.outputs[0], ExposureNode.inputs[0]) #Connect lightmap node to mixnode
                        mat.node_tree.links.new(ExposureNode.outputs[0], mixNode.inputs[1]) #Connect lightmap node to mixnode
                    else:
                        mat.node_tree.links.new(lightmapNode.outputs[0], mixNode.inputs[1]) #Connect lightmap node to mixnode
                    mat.node_tree.links.new(baseColorNode.outputs[0], mixNode.inputs[2]) #Connect basecolor to pbr node
                    mat.node_tree.links.new(mixNode.outputs[0], mainNode.inputs[0]) #Connect mixnode to pbr node
                    mat.node_tree.links.new(UVLightmap.outputs[0], lightmapNode.inputs[0]) #Connect uvnode to lightmapnode

def exchangeLightmapsToPostfix(ext_postfix, new_postfix, formatHDR=".hdr"):

    print(ext_postfix, new_postfix, formatHDR)

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                for slot in obj.material_slots:
                    mat = slot.material
                    node_tree = mat.node_tree
                    nodes = mat.node_tree.nodes

                    for node in nodes:
                        if node.name == "Baked Image" or node.name == "TLM_Lightmap":
                            img_name = node.image.filepath_raw
                            cutLen = len(ext_postfix + formatHDR)
                            print("Len:" + str(len(ext_postfix + formatHDR)) + "|" + ext_postfix + ".." + formatHDR)

                            #Simple way to sort out objects with multiple materials
                            if formatHDR == ".hdr" or formatHDR == ".exr":
                                if not node.image.filepath_raw.endswith(new_postfix + formatHDR):
                                    node.image.filepath_raw = img_name[:-cutLen] + new_postfix + formatHDR
                            else:
                                cutLen = len(ext_postfix + ".hdr")
                                if not node.image.filepath_raw.endswith(new_postfix + formatHDR):
                                    node.image.filepath_raw = img_name[:-cutLen] + new_postfix + formatHDR

    for image in bpy.data.images:
        image.reload()

def load_library(asset_name):

    scriptDir = os.path.dirname(os.path.realpath(__file__))

    if bpy.data.filepath.endswith('tlm_data.blend'): # Prevent load in library itself
        return

    data_path = os.path.abspath(os.path.join(scriptDir, '..', '..', 'Assets/tlm_data.blend'))
    data_names = [asset_name]

    # Import
    data_refs = data_names.copy()
    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = data_refs

    for ref in data_refs:
        ref.use_fake_user = True