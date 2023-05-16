import bpy, math

#from . import cache
from .. utility import *

def init(self, prev_container):

    #store_existing(prev_container)

    #set_settings()

    configure_world()

    configure_lights()

    configure_meshes(self)

def configure_world():
    pass

def configure_lights():
    pass

def configure_meshes(self):

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

    iterNum = 1
    currentIterNum = 0

    scene = bpy.context.scene

    for obj in scene.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                obj.hide_select = False #Remember to toggle this back

                currentIterNum = currentIterNum + 1

                obj.octane.baking_group_id = 1 + currentIterNum #0 doesn't exist, 1 is neutral and 2 is first baked object

                print("Obj: " + obj.name + " set to baking group: " + str(obj.octane.baking_group_id))

                for slot in obj.material_slots:
                    if "." + slot.name + '_Original' in bpy.data.materials:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("The material: " + slot.name + " shifted to " + "." + slot.name + '_Original')
                        slot.material = bpy.data.materials["." + slot.name + '_Original']

                
                objWasHidden = False

                #For some reason, a Blender bug might prevent invisible objects from being smart projected
                #We will turn the object temporarily visible
                obj.hide_viewport = False
                obj.hide_set(False)

                #Configure selection
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                obs = bpy.context.view_layer.objects
                active = obs.active

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
                        print("Setting active UV to: " + uv_layers.active_index)

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

                    else:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("Existing UV map found for obj: " + obj.name)
                        for i in range(0, len(uv_layers)):
                            if uv_layers[i].name == uv_channel:
                                uv_layers.active_index = i
                                break

    set_camera()

def set_camera():

    cam_name = "TLM-BakeCam"

    if not cam_name in bpy.context.scene:
        camera = bpy.data.cameras.new(cam_name)
        camobj_name = "TLM-BakeCam-obj"
        cam_obj = bpy.data.objects.new(camobj_name, camera)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = ((0,0,0))

        bpy.context.scene.camera = cam_obj 

def set_settings():

    scene = bpy.context.scene
    cycles = scene.cycles
    scene.render.engine = "CYCLES"
    sceneProperties = scene.TLM_SceneProperties
    engineProperties = scene.TLM_EngineProperties
    cycles.device = scene.TLM_EngineProperties.tlm_mode

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