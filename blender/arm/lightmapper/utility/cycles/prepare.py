import bpy, math, time

from . import cache
from .. utility import *

def assemble():

    configure_world()

    configure_lights()

    configure_meshes()

def init(self, prev_container):

    store_existing(prev_container)

    set_settings()

    configure_world()

    configure_lights()

    configure_meshes(self)

    print("Config mesh catch omitted: REMEMBER TO SET IT BACK NAXELA")
    # try:
    #     configure_meshes(self)
    # except Exception as e:

    #     print("An error occured during mesh configuration. See error below:")

    #     print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

    #     if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
    #         print("Turn on verbose mode to get more detail.")

def configure_world():
    pass

def configure_lights():
    pass

def configure_meshes(self):

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Configuring meshes: Start")

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Configuring meshes: Material restore")
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                cache.backup_material_restore(obj)

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Configuring meshes: Material rename check")
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                cache.backup_material_rename(obj)

    for mat in bpy.data.materials:
        if mat.users < 1:
            bpy.data.materials.remove(mat)

    for mat in bpy.data.materials:
        if mat.name.startswith("."):
            if "_Original" in mat.name:
                bpy.data.materials.remove(mat)

    #for image in bpy.data.images:
    #    if image.name.endswith("_baked"):
    #        bpy.data.images.remove(image, do_unlink=True)

    iterNum = 0
    currentIterNum = 0

    scene = bpy.context.scene

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Object: Setting UV, converting modifiers and prepare channels")

    #OBJECT: Set UV, CONVERT AND PREPARE
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


            #Additional check for zero poly meshes
            mesh = obj.data
            if (len(mesh.polygons)) < 1:
                print("Found an object with zero polygons. Skipping object: " + obj.name)
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = False

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use and not hidden:
                
                print("Preparing: UV initiation for object: " + obj.name)

                if len(obj.data.vertex_colors) < 1:
                    obj.data.vertex_colors.new(name="TLM")

                if scene.TLM_SceneProperties.tlm_reset_uv:

                    uv_layers = obj.data.uv_layers
                    uv_channel = "UVMap_Lightmap"
                    for uvlayer in uv_layers:
                        if uvlayer.name == uv_channel:
                            uv_layers.remove(uvlayer)

                if scene.TLM_SceneProperties.tlm_apply_on_unwrap:
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Applying transform to: " + obj.name)
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                if scene.TLM_SceneProperties.tlm_apply_modifiers:
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Applying modifiers to: " + obj.name)
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.convert(target='MESH')

                for slot in obj.material_slots:
                    material = slot.material
                    skipIncompatibleMaterials(material)

                obj.hide_select = False #Remember to toggle this back
                for slot in obj.material_slots:
                    if "." + slot.name + '_Original' in bpy.data.materials:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("The material: " + slot.name + " shifted to " + "." + slot.name + '_Original')
                        slot.material = bpy.data.materials["." + slot.name + '_Original']

    #ATLAS UV PROJECTING
    print("PREPARE: ATLAS")
    for atlasgroup in scene.TLM_AtlasList:

        print("Adding UV Projection for Atlas group: " + atlasgroup.name)

        atlas = atlasgroup.name
        atlas_items = []

        bpy.ops.object.select_all(action='DESELECT')
        
        #Atlas: Set UV, CONVERT AND PREPARE
        for obj in bpy.context.scene.objects:

            if obj.TLM_ObjectProperties.tlm_atlas_pointer == atlasgroup.name:

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

                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA" and not hidden:

                    uv_layers = obj.data.uv_layers

                    if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                        uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                    else:
                        uv_channel = "UVMap_Lightmap"

                    if not uv_channel in uv_layers:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("UV map created for object: " + obj.name)
                        uvmap = uv_layers.new(name=uv_channel)
                        uv_layers.active_index = len(uv_layers) - 1
                    else:
                        print("Existing UV map found for object: " + obj.name)
                        for i in range(0, len(uv_layers)):
                            if uv_layers[i].name == 'UVMap_Lightmap':
                                uv_layers.active_index = i
                                break

                    atlas_items.append(obj)
                    obj.select_set(True)

                if atlasgroup.tlm_atlas_lightmap_unwrap_mode == "SmartProject":
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Atlasgroup Smart Project for: " + str(atlas_items))
                    for obj in atlas_items:
                        print("Applying Smart Project to: ")
                        print(obj.name + ": Active UV: " + obj.data.uv_layers[obj.data.uv_layers.active_index].name)


                    if len(atlas_items) > 0:
                        bpy.context.view_layer.objects.active = atlas_items[0]

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    #API changes in 2.91 causes errors:
                    if (2, 91, 0) > bpy.app.version:
                        bpy.ops.uv.smart_project(angle_limit=45.0, island_margin=obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin, user_area_weight=1.0, use_aspect=True, stretch_to_bounds=False)
                    else:
                        angle = math.radians(45.0)
                        bpy.ops.uv.smart_project(angle_limit=angle, island_margin=obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin, area_weight=1.0, correct_aspect=True, scale_to_bounds=False)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    print("Smart project done.")
                elif atlasgroup.tlm_atlas_lightmap_unwrap_mode == "Lightmap":

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.uv.lightmap_pack('EXEC_SCREEN', PREF_CONTEXT='ALL_FACES', PREF_MARGIN_DIV=atlasgroup.tlm_atlas_unwrap_margin)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')

                elif atlasgroup.tlm_atlas_lightmap_unwrap_mode == "Xatlas":

                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Using Xatlas on Atlas Group: " + atlas)

                    for obj in atlas_items:
                        obj.select_set(True)
                    if len(atlas_items) > 0:
                        bpy.context.view_layer.objects.active = atlas_items[0]

                    bpy.ops.object.mode_set(mode='EDIT')

                    Unwrap_Lightmap_Group_Xatlas_2_headless_call(obj)

                    bpy.ops.object.mode_set(mode='OBJECT')

                else:
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Copied Existing UV Map for Atlas Group: " + atlas)

                if atlasgroup.tlm_use_uv_packer:
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in atlas_items:
                        obj.select_set(True)
                    if len(atlas_items) > 0:
                        bpy.context.view_layer.objects.active = atlas_items[0]
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')

                    bpy.context.scene.UVPackerProps.uvp_padding = atlasgroup.tlm_uv_packer_padding
                    bpy.context.scene.UVPackerProps.uvp_engine = atlasgroup.tlm_uv_packer_packing_engine

                    #print(x)

                    print("!!!!!!!!!!!!!!!!!!!!! Using UV Packer on: " + obj.name)

                    if uv_layers.active == "UVMap_Lightmap":
                        print("YES")
                    else:
                        print("NO")
                        uv_layers.active_index = len(uv_layers) - 1

                    if uv_layers.active == "UVMap_Lightmap":
                        print("YES")
                    else:
                        print("NO")
                        uv_layers.active_index = len(uv_layers) - 1

                    bpy.ops.uvpackeroperator.packbtn()

                    # if bpy.context.scene.UVPackerProps.uvp_engine == "OP0":
                    #     time.sleep(1)
                    # else:
                    #     time.sleep(2)
                    time.sleep(2)

                    #FIX THIS! MAKE A SEPARATE CALL. THIS IS A THREADED ASYNC

                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')

                    #print(x)

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                iterNum = iterNum + 1

    #OBJECT UV PROJECTING
    print("PREPARE: OBJECTS")
    for obj in bpy.context.scene.objects:
        if obj.name in bpy.context.view_layer.objects: #Possible fix for view layer error
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

                    objWasHidden = False

                    #For some reason, a Blender bug might prevent invisible objects from being smart projected
                    #We will turn the object temporarily visible
                    obj.hide_viewport = False
                    obj.hide_set(False)

                    currentIterNum = currentIterNum + 1

                    #Configure selection
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    obs = bpy.context.view_layer.objects
                    active = obs.active

                    #Provide material if none exists
                    print("Preprocessing material for: " + obj.name)
                    preprocess_material(obj, scene)

                    #UV Layer management here
                    if not obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                        print("Managing layer for Obj: " + obj.name)

                        uv_layers = obj.data.uv_layers

                        if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                            uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                        else:
                            uv_channel = "UVMap_Lightmap"

                        if not uv_channel in uv_layers:
                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("UV map created for obj: " + obj.name)
                            uvmap = uv_layers.new(name=uv_channel)
                            uv_layers.active_index = len(uv_layers) - 1

                            #If lightmap
                            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "Lightmap":
                                bpy.ops.uv.lightmap_pack('EXEC_SCREEN', PREF_CONTEXT='ALL_FACES', PREF_MARGIN_DIV=obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin)
                            
                            #If smart project
                            elif obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "SmartProject":

                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Smart Project B")
                                bpy.ops.object.select_all(action='DESELECT')
                                obj.select_set(True)
                                bpy.ops.object.mode_set(mode='EDIT')
                                bpy.ops.mesh.select_all(action='SELECT')
                                #API changes in 2.91 causes errors:
                                if (2, 91, 0) > bpy.app.version:
                                    bpy.ops.uv.smart_project(angle_limit=45.0, island_margin=obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin, user_area_weight=1.0, use_aspect=True, stretch_to_bounds=False)
                                else:
                                    angle = math.radians(45.0)
                                    bpy.ops.uv.smart_project(angle_limit=angle, island_margin=obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin, area_weight=1.0, correct_aspect=True, scale_to_bounds=False)

                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.object.mode_set(mode='OBJECT')
                            
                            elif obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "Xatlas":
                                
                                Unwrap_Lightmap_Group_Xatlas_2_headless_call(obj)

                            elif obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("ATLAS GROUP: " + obj.TLM_ObjectProperties.tlm_atlas_pointer)
                                
                            else: #if copy existing

                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Copied Existing UV Map for object: " + obj.name)

                        if obj.TLM_ObjectProperties.tlm_use_uv_packer:
                            bpy.ops.object.select_all(action='DESELECT')
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')

                            bpy.context.scene.UVPackerProps.uvp_padding = obj.TLM_ObjectProperties.tlm_uv_packer_padding
                            bpy.context.scene.UVPackerProps.uvp_engine = obj.TLM_ObjectProperties.tlm_uv_packer_packing_engine

                            #print(x)

                            print("!!!!!!!!!!!!!!!!!!!!! Using UV Packer on: " + obj.name)

                            if uv_layers.active == "UVMap_Lightmap":
                                print("YES")
                            else:
                                print("NO")
                                uv_layers.active_index = len(uv_layers) - 1

                            if uv_layers.active == "UVMap_Lightmap":
                                print("YES")
                            else:
                                print("NO")
                                uv_layers.active_index = len(uv_layers) - 1

                            bpy.ops.uvpackeroperator.packbtn()

                            if bpy.context.scene.UVPackerProps.uvp_engine == "OP0":
                                time.sleep(1)
                            else:
                                time.sleep(2)

                            #FIX THIS! MAKE A SEPARATE CALL. THIS IS A THREADED ASYNC

                            bpy.ops.mesh.select_all(action='DESELECT')
                            bpy.ops.object.mode_set(mode='OBJECT')

                            #print(x)

                        else:
                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("Existing UV map found for obj: " + obj.name)
                            for i in range(0, len(uv_layers)):
                                if uv_layers[i].name == uv_channel:
                                    uv_layers.active_index = i
                                    break

                    #print(x)

                    #Sort out nodes
                    for slot in obj.material_slots:

                        nodetree = slot.material.node_tree

                        outputNode = nodetree.nodes[0] #Presumed to be material output node

                        if(outputNode.type != "OUTPUT_MATERIAL"):
                            for node in nodetree.nodes:
                                if node.type == "OUTPUT_MATERIAL":
                                    outputNode = node
                                    break

                        mainNode = outputNode.inputs[0].links[0].from_node

                        if mainNode.type not in ['BSDF_PRINCIPLED','BSDF_DIFFUSE','GROUP']:

                            #TODO! FIND THE PRINCIPLED PBR
                            self.report({'INFO'}, "The primary material node is not supported. Seeking first principled.")

                            if len(find_node_by_type(nodetree.nodes, Node_Types.pbr_node)) > 0: 
                                mainNode = find_node_by_type(nodetree.nodes, Node_Types.pbr_node)[0]
                            else:
                                self.report({'INFO'}, "No principled found. Seeking diffuse")
                                if len(find_node_by_type(nodetree.nodes, Node_Types.diffuse)) > 0: 
                                    mainNode = find_node_by_type(nodetree.nodes, Node_Types.diffuse)[0]
                                else:
                                    self.report({'INFO'}, "No supported nodes. Continuing anyway.")

                        if mainNode.type == 'GROUP':
                            if mainNode.node_tree != "Armory PBR":
                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("The material group is not supported!")

                        if (mainNode.type == "ShaderNodeMixRGB"):
                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("Mix shader found")

                            #Skip for now
                            slot.material.TLM_ignore = True

                        if (mainNode.type == "BSDF_PRINCIPLED"):
                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("BSDF_Principled")
                            if scene.TLM_EngineProperties.tlm_directional_mode == "None":
                                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                    print("Directional mode")
                                if not len(mainNode.inputs[22].links) == 0:
                                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                        print("NOT LEN 0")
                                    ninput = mainNode.inputs[22].links[0]
                                    noutput = mainNode.inputs[22].links[0].from_node
                                    nodetree.links.remove(noutput.outputs[0].links[0])

                            #Clamp metallic
                            if bpy.context.scene.TLM_SceneProperties.tlm_metallic_clamp == "limit":

                                MainMetNodeSocket = mainNode.inputs.get("Metallic")
                                if not len(MainMetNodeSocket.links) == 0:

                                    print("Creating new clamp node")

                                    nodes = nodetree.nodes
                                    MetClampNode = nodes.new('ShaderNodeClamp')
                                    MetClampNode.location = (-200,150)
                                    MetClampNode.inputs[2].default_value = 0.9
                                    minput = mainNode.inputs.get("Metallic").links[0] #Metal input socket
                                    moutput = mainNode.inputs.get("Metallic").links[0].from_socket #Output socket
                                    
                                    nodetree.links.remove(minput)

                                    nodetree.links.new(moutput, MetClampNode.inputs[0]) #minput node to clamp node
                                    nodetree.links.new(MetClampNode.outputs[0], MainMetNodeSocket) #clamp node to metinput

                                elif mainNode.type == "PRINCIPLED_BSDF" and MainMetNodeSocket.links[0].from_node.type == "CLAMP":

                                    pass

                                else:

                                    print("New clamp node NOT made")

                                    if mainNode.inputs[4].default_value > 0.9:
                                        mainNode.inputs[4].default_value = 0.9

                            elif bpy.context.scene.TLM_SceneProperties.tlm_metallic_clamp == "zero":

                                MainMetNodeSocket = mainNode.inputs[4]
                                if not len(MainMetNodeSocket.links) == 0:
                                    nodes = nodetree.nodes
                                    MetClampNode = nodes.new('ShaderNodeClamp')
                                    MetClampNode.location = (-200,150)
                                    MetClampNode.inputs[2].default_value = 0.0
                                    minput = mainNode.inputs[4].links[0] #Metal input socket
                                    moutput = mainNode.inputs[4].links[0].from_socket #Output socket

                                    nodetree.links.remove(minput)

                                    nodetree.links.new(moutput, MetClampNode.inputs[0]) #minput node to clamp node
                                    nodetree.links.new(MetClampNode.outputs[0], MainMetNodeSocket) #clamp node to metinput
                                else:
                                    mainNode.inputs[4].default_value = 0.0

                            else: #Skip
                                pass

                        if (mainNode.type == "BSDF_DIFFUSE"):
                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("BSDF_Diffuse")

                        # if (mainNode.type == "BSDF_DIFFUSE"):
                        #     if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        #         print("BSDF_Diffuse")

                    #TODO FIX THIS PART!
                    #THIS IS USED IN CASES WHERE FOR SOME REASON THE USER FORGETS TO CONNECT SOMETHING INTO THE OUTPUT MATERIAL
                    for slot in obj.material_slots:

                        nodetree = bpy.data.materials[slot.name].node_tree
                        nodes = nodetree.nodes

                        #First search to get the first output material type
                        for node in nodetree.nodes:
                            if node.type == "OUTPUT_MATERIAL":
                                mainNode = node
                                break

                        #Fallback to get search
                        if not mainNode.type == "OUTPUT_MATERIAL":
                            mainNode = nodetree.nodes.get("Material Output")

                        #Last resort to first node in list
                        if not mainNode.type == "OUTPUT_MATERIAL":
                            mainNode = nodetree.nodes[0].inputs[0].links[0].from_node

                    #     for node in nodes:
                    #         if "LM" in node.name:
                    #             nodetree.links.new(node.outputs[0], mainNode.inputs[0])

                    #     for node in nodes:
                    #         if "Lightmap" in node.name:
                    #                 nodes.remove(node)

def preprocess_material(obj, scene):
    if len(obj.material_slots) == 0:
        single = False
        number = 0
        while single == False:
            matname = obj.name + ".00" + str(number)
            if matname in bpy.data.materials:
                single = False
                number = number + 1
            else:
                mat = bpy.data.materials.new(name=matname)
                mat.use_nodes = True
                obj.data.materials.append(mat)
                single = True

    #We copy the existing material slots to an ordered array, which corresponds to the slot index
    matArray = []
    for slot in obj.material_slots:
        matArray.append(slot.name)
    
    obj["TLM_PrevMatArray"] = matArray

    #We check and safeguard against NoneType
    for slot in obj.material_slots:
        if slot.material is None:
            matName = obj.name + ".00" + str(0)
            bpy.data.materials.new(name=matName)
            slot.material = bpy.data.materials[matName]
            slot.material.use_nodes = True

    for slot in obj.material_slots:

        cache.backup_material_copy(slot)

        mat = slot.material
        if mat.users > 1:
                copymat = mat.copy()
                slot.material = copymat

    #SOME ATLAS EXCLUSION HERE?
    ob = obj
    for slot in ob.material_slots:
        #If temporary material already exists
        if slot.material.name.endswith('_temp'):
            continue
        n = slot.material.name + '_' + ob.name + '_temp'
        if not n in bpy.data.materials:
            slot.material = slot.material.copy()
        slot.material.name = n

    #Add images for baking
    img_name = obj.name + '_baked'
    #Resolution is object lightmap resolution divided by global scaler

    if scene.TLM_EngineProperties.tlm_setting_supersample == "2x":
        supersampling_scale = 2
    elif scene.TLM_EngineProperties.tlm_setting_supersample == "4x":
        supersampling_scale = 4
    else:
        supersampling_scale = 1


    if (obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA" and obj.TLM_ObjectProperties.tlm_atlas_pointer != ""):

        atlas_image_name = obj.TLM_ObjectProperties.tlm_atlas_pointer + "_baked"

        res = int(scene.TLM_AtlasList[obj.TLM_ObjectProperties.tlm_atlas_pointer].tlm_atlas_lightmap_resolution) / int(scene.TLM_EngineProperties.tlm_resolution_scale) * int(supersampling_scale)

        #If image not in bpy.data.images or if size changed, make a new image
        if atlas_image_name not in bpy.data.images or bpy.data.images[atlas_image_name].size[0] != res or bpy.data.images[atlas_image_name].size[1] != res:
            img = bpy.data.images.new(img_name, int(res), int(res), alpha=True, float_buffer=True)

            num_pixels = len(img.pixels)
            result_pixel = list(img.pixels)

            for i in range(0,num_pixels,4):

                if scene.TLM_SceneProperties.tlm_override_bg_color:
                    result_pixel[i+0] = scene.TLM_SceneProperties.tlm_override_color[0]
                    result_pixel[i+1] = scene.TLM_SceneProperties.tlm_override_color[1]
                    result_pixel[i+2] = scene.TLM_SceneProperties.tlm_override_color[2]
                else:
                    result_pixel[i+0] = 0.0
                    result_pixel[i+1] = 0.0
                    result_pixel[i+2] = 0.0
                    result_pixel[i+3] = 1.0

            img.pixels = result_pixel

            img.name = atlas_image_name
        else:
            img = bpy.data.images[atlas_image_name]

        for slot in obj.material_slots:
            mat = slot.material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            if "Baked Image" in nodes:
                img_node = nodes["Baked Image"]
            else:
                img_node = nodes.new('ShaderNodeTexImage')
                img_node.name = 'Baked Image'
                img_node.location = (100, 100)
                img_node.image = img
            img_node.select = True
            nodes.active = img_node

        #We need to save this file first in Blender 3.3 due to new filmic option?
        image = img
        saveDir = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
        bakemap_path = os.path.join(saveDir, image.name)
        filepath_ext = ".hdr"
        image.filepath_raw = bakemap_path + filepath_ext
        image.file_format = "HDR"
        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("Saving to: " + image.filepath_raw)
        image.save()

    else:

        res = int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution) / int(scene.TLM_EngineProperties.tlm_resolution_scale) * int(supersampling_scale)

        #If image not in bpy.data.images or if size changed, make a new image
        if img_name not in bpy.data.images or bpy.data.images[img_name].size[0] != res or bpy.data.images[img_name].size[1] != res:
            img = bpy.data.images.new(img_name, int(res), int(res), alpha=True, float_buffer=True)

            num_pixels = len(img.pixels)
            result_pixel = list(img.pixels)

            for i in range(0,num_pixels,4):
                if scene.TLM_SceneProperties.tlm_override_bg_color:
                    result_pixel[i+0] = scene.TLM_SceneProperties.tlm_override_color[0]
                    result_pixel[i+1] = scene.TLM_SceneProperties.tlm_override_color[1]
                    result_pixel[i+2] = scene.TLM_SceneProperties.tlm_override_color[2]
                else:
                    result_pixel[i+0] = 0.0
                    result_pixel[i+1] = 0.0
                    result_pixel[i+2] = 0.0
                    result_pixel[i+3] = 1.0

            img.pixels = result_pixel

            img.name = img_name
        else:
            img = bpy.data.images[img_name]

        for slot in obj.material_slots:
            mat = slot.material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            if "Baked Image" in nodes:
                img_node = nodes["Baked Image"]
            else:
                img_node = nodes.new('ShaderNodeTexImage')
                img_node.name = 'Baked Image'
                img_node.location = (100, 100)
                img_node.image = img
            img_node.select = True
            nodes.active = img_node

        #We need to save this file first in Blender 3.3 due to new filmic option?
        image = img
        saveDir = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
        bakemap_path = os.path.join(saveDir, image.name)
        filepath_ext = ".hdr"
        image.filepath_raw = bakemap_path + filepath_ext
        image.file_format = "HDR"
        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("Saving to: " + image.filepath_raw)
        image.save()

def set_settings():

    scene = bpy.context.scene
    cycles = scene.cycles
    scene.render.engine = "CYCLES"
    sceneProperties = scene.TLM_SceneProperties
    engineProperties = scene.TLM_EngineProperties
    cycles.device = scene.TLM_EngineProperties.tlm_mode
    
    print(bpy.app.version)

    if bpy.app.version[0] == 3:
        if cycles.device == "GPU":
            scene.cycles.tile_size = 256
        else:
            scene.cycles.tile_size = 32
    else:    
        if cycles.device == "GPU":
            scene.render.tile_x = 256
            scene.render.tile_y = 256
        else:
            scene.render.tile_x = 32
            scene.render.tile_y = 32
    
    if engineProperties.tlm_quality == "0":
        cycles.samples = 32
        cycles.max_bounces = 1
        cycles.diffuse_bounces = 1
        cycles.glossy_bounces = 1
        cycles.transparent_max_bounces = 1
        cycles.transmission_bounces = 1
        cycles.volume_bounces = 1
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
    elif engineProperties.tlm_quality == "1":
        cycles.samples = 64
        cycles.max_bounces = 2
        cycles.diffuse_bounces = 2
        cycles.glossy_bounces = 2
        cycles.transparent_max_bounces = 2
        cycles.transmission_bounces = 2
        cycles.volume_bounces = 2
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
    elif engineProperties.tlm_quality == "2":
        cycles.samples = 512
        cycles.max_bounces = 2
        cycles.diffuse_bounces = 2
        cycles.glossy_bounces = 2
        cycles.transparent_max_bounces = 2
        cycles.transmission_bounces = 2
        cycles.volume_bounces = 2
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
    elif engineProperties.tlm_quality == "3":
        cycles.samples = 1024
        cycles.max_bounces = 256
        cycles.diffuse_bounces = 256
        cycles.glossy_bounces = 256
        cycles.transparent_max_bounces = 256
        cycles.transmission_bounces = 256
        cycles.volume_bounces = 256
        cycles.caustics_reflective = False
        cycles.caustics_refractive = False
    elif engineProperties.tlm_quality == "4":
        cycles.samples = 2048
        cycles.max_bounces = 512
        cycles.diffuse_bounces = 512
        cycles.glossy_bounces = 512
        cycles.transparent_max_bounces = 512
        cycles.transmission_bounces = 512
        cycles.volume_bounces = 512
        cycles.caustics_reflective = True
        cycles.caustics_refractive = True
    else: #Custom
        pass

def store_existing(prev_container):

    scene = bpy.context.scene
    cycles = scene.cycles

    selected = []

    for obj in bpy.context.scene.objects:
        if obj.select_get():
            selected.append(obj.name)

    prev_container["settings"] = [
        cycles.samples,
        cycles.max_bounces,
        cycles.diffuse_bounces,
        cycles.glossy_bounces,
        cycles.transparent_max_bounces,
        cycles.transmission_bounces,
        cycles.volume_bounces,
        cycles.caustics_reflective,
        cycles.caustics_refractive,
        cycles.device,
        scene.render.engine,
        bpy.context.view_layer.objects.active,
        selected,
        [scene.render.resolution_x, scene.render.resolution_y]
    ]

def skipIncompatibleMaterials(material):
    node_tree = material.node_tree
    nodes = material.node_tree.nodes

    #ADD OR MIX SHADER? CUSTOM/GROUP?
    #IF Principled has emissive or transparency?

    SkipMatList = ["EMISSION",
                    "BSDF_TRANSPARENT",
                    "BACKGROUND", 
                    "BSDF_HAIR",
                    "BSDF_HAIR_PRINCIPLED",
                    "HOLDOUT",
                    "PRINCIPLED_VOLUME",
                    "BSDF_REFRACTION",
                    "EEVEE_SPECULAR",
                    "BSDF_TRANSLUCENT",
                    "VOLUME_ABSORPTION",
                    "VOLUME_SCATTER"]

    #Find output node
    outputNode = nodes[0]
    if(outputNode.type != "OUTPUT_MATERIAL"):
        for node in node_tree.nodes:
            if node.type == "OUTPUT_MATERIAL":
                outputNode = node
                break

    #Find mainnode
    mainNode = outputNode.inputs[0].links[0].from_node

    if mainNode.type in SkipMatList:
        material.TLM_ignore = True
        print("Ignored material: " + material.name)

def packUVPack():



    pass
