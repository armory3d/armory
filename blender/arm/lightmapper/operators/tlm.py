import bpy, os, time, blf, webbrowser, platform, numpy, bmesh
import math, subprocess, multiprocessing
from .. utility import utility
from .. utility import build
from .. utility.cycles import cache
from .. network import server

def setObjectLightmapByWeight(minimumRes, maximumRes, objWeight):
        
        availableResolutions = [32,64,128,256,512,1024,2048,4096,8192]
        
        minRes = minimumRes
        minResIdx = availableResolutions.index(minRes)
        maxRes = maximumRes
        maxResIdx = availableResolutions.index(maxRes)
        
        exampleWeight = objWeight
        
        if minResIdx == maxResIdx:
            pass
        else:
        
            increment = 1.0/(maxResIdx-minResIdx)
            
            assortedRange = []
            
            for a in numpy.arange(0.0, 1.0, increment):
                assortedRange.append(round(a, 2))
                
            assortedRange.append(1.0)
            nearestWeight = min(assortedRange, key=lambda x:abs(x - exampleWeight))
            return (availableResolutions[assortedRange.index(nearestWeight) + minResIdx])

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

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    cache.backup_material_restore(obj)

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

        for image in bpy.data.images:
            if image.name.endswith("_baked"):
                bpy.data.images.remove(image, do_unlink=True)

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:

                        atlas = obj.TLM_ObjectProperties.tlm_postatlas_pointer
                        atlas_resize = False

                        for atlasgroup in scene.TLM_PostAtlasList:
                            if atlasgroup.name == atlas:
                                atlas_resize = True

                        if atlas_resize:

                            bpy.ops.object.select_all(action='DESELECT')
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj

                            uv_layers = obj.data.uv_layers

                            if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                                uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                            else:
                                uv_channel = "UVMap_Lightmap"
                            
                            for i in range(0, len(uv_layers)):
                                if uv_layers[i].name == uv_channel:
                                    uv_layers.active_index = i
                                    break

                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.uv.select_all(action='SELECT')
                            bpy.ops.uv.pack_islands(rotate=False, margin=0.001)
                            bpy.ops.uv.select_all(action='DESELECT')
                            bpy.ops.mesh.select_all(action='DESELECT')
                            bpy.ops.object.mode_set(mode='OBJECT')

                            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                                print("Resized for obj: " + obj.name)

                    if "Lightmap" in obj:
                        del obj["Lightmap"]

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
        
        if platform.system() != "Linux":

            if os.path.isdir(dirpath):
                webbrowser.open('file://' + dirpath)
            else:
                os.mkdir(dirpath)
                webbrowser.open('file://' + dirpath)
        else:

            if os.path.isdir(dirpath):
                os.system('xdg-open "%s"' % dirpath)
                #webbrowser.open('file://' + dirpath)
            else:
                os.mkdir(dirpath)
                os.system('xdg-open "%s"' % dirpath)
                #webbrowser.open('file://' + dirpath)

        return {'FINISHED'}

class TLM_EnableSet(bpy.types.Operator):
    """Enable for set"""
    bl_idname = "tlm.enable_set"
    bl_label = "Enable for set"
    bl_description = "Enable for set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        weightList = {} #ObjName : [Dimension,Weight]
        max = 0

        if bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Scene":
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":

                    print("Enabling for scene: " + obj.name)
                    
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    
                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = True
                    
                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = bpy.context.scene.TLM_SceneProperties.tlm_mesh_lightmap_unwrap_mode
                    obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin = bpy.context.scene.TLM_SceneProperties.tlm_mesh_unwrap_margin
                    obj.TLM_ObjectProperties.tlm_postpack_object = bpy.context.scene.TLM_SceneProperties.tlm_postpack_object

                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                        obj.TLM_ObjectProperties.tlm_atlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_atlas_pointer

                    obj.TLM_ObjectProperties.tlm_postatlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_postatlas_pointer
                    
                    if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Single":
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = scene.TLM_SceneProperties.tlm_mesh_lightmap_resolution
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Dimension":
                        obj_dimensions = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z
                        weightList[obj.name] = [obj_dimensions, 0]
                        if obj_dimensions > max:
                            max = obj_dimensions
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Surface":
                        bm = bmesh.new()
                        bm.from_mesh(obj.data)
                        area = sum(f.calc_area() for f in bm.faces)
                        weightList[obj.name] = [area, 0]
                        if area > max:
                            max = area
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Volume":
                        bm = bmesh.new()
                        bm.from_mesh(obj.data)
                        volume = float( bm.calc_volume())
                        weightList[obj.name] = [volume, 0]
                        if volume > max:
                            max = volume
        
        elif bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Selection":
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    
                    print("Enabling for selection: " + obj.name)
                    
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    
                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = True
                    
                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = bpy.context.scene.TLM_SceneProperties.tlm_mesh_lightmap_unwrap_mode
                    obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin = bpy.context.scene.TLM_SceneProperties.tlm_mesh_unwrap_margin
                    obj.TLM_ObjectProperties.tlm_postpack_object = bpy.context.scene.TLM_SceneProperties.tlm_postpack_object

                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                        obj.TLM_ObjectProperties.tlm_atlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_atlas_pointer

                    obj.TLM_ObjectProperties.tlm_postatlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_postatlas_pointer
                    
                    if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Single":
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = scene.TLM_SceneProperties.tlm_mesh_lightmap_resolution
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Dimension":
                        obj_dimensions = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z
                        weightList[obj.name] = [obj_dimensions, 0]
                        if obj_dimensions > max:
                            max = obj_dimensions
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Surface":
                        bm = bmesh.new()
                        bm.from_mesh(obj.data)
                        area = sum(f.calc_area() for f in bm.faces)
                        weightList[obj.name] = [area, 0]
                        if area > max:
                            max = area
                    elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Volume":
                        bm = bmesh.new()
                        bm.from_mesh(obj.data)
                        volume = float( bm.calc_volume())
                        weightList[obj.name] = [volume, 0]
                        if volume > max:
                            max = volume
        
        else: #Enabled
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                        print("Enabling for designated: " + obj.name)
                        
                        bpy.context.view_layer.objects.active = obj
                        obj.select_set(True)
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                        
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = True
                        
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = bpy.context.scene.TLM_SceneProperties.tlm_mesh_lightmap_unwrap_mode
                        obj.TLM_ObjectProperties.tlm_mesh_unwrap_margin = bpy.context.scene.TLM_SceneProperties.tlm_mesh_unwrap_margin
                        obj.TLM_ObjectProperties.tlm_postpack_object = bpy.context.scene.TLM_SceneProperties.tlm_postpack_object

                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                            obj.TLM_ObjectProperties.tlm_atlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_atlas_pointer

                        obj.TLM_ObjectProperties.tlm_postatlas_pointer = bpy.context.scene.TLM_SceneProperties.tlm_postatlas_pointer
                        
                        if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Single":
                            obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = scene.TLM_SceneProperties.tlm_mesh_lightmap_resolution
                        elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Dimension":
                            obj_dimensions = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z
                            weightList[obj.name] = [obj_dimensions, 0]
                            if obj_dimensions > max:
                                max = obj_dimensions
                        elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Surface":
                            bm = bmesh.new()
                            bm.from_mesh(obj.data)
                            area = sum(f.calc_area() for f in bm.faces)
                            weightList[obj.name] = [area, 0]
                            if area > max:
                                max = area
                        elif bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight == "Volume":
                            bm = bmesh.new()
                            bm.from_mesh(obj.data)
                            volume = float( bm.calc_volume())
                            weightList[obj.name] = [volume, 0]
                            if volume > max:
                                max = volume

        if bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Scene":
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
        
                    if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight != "Single":
                        for key in weightList:
                            weightList[obj.name][1] = weightList[obj.name][0] / max
                        a = setObjectLightmapByWeight(int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_min), int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_max), weightList[obj.name][1])
                        print(str(a) + "/" + str(weightList[obj.name][1]))
                        print("Scale: " + str(weightList[obj.name][0]))
                        print("Obj: " + obj.name)
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = str(a)

        elif bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Selection":
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":

                    if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight != "Single":
                        for key in weightList:
                            weightList[obj.name][1] = weightList[obj.name][0] / max
                        a = setObjectLightmapByWeight(int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_min), int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_max), weightList[obj.name][1])
                        print(str(a) + "/" + str(weightList[obj.name][1]))
                        print("Scale: " + str(weightList[obj.name][0]))
                        print("Obj: " + obj.name)
                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = str(a)


        else: #Enabled
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                        if bpy.context.scene.TLM_SceneProperties.tlm_resolution_weight != "Single":
                            for key in weightList:
                                weightList[obj.name][1] = weightList[obj.name][0] / max
                            a = setObjectLightmapByWeight(int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_min), int(bpy.context.scene.TLM_SceneProperties.tlm_resolution_max), weightList[obj.name][1])
                            print(str(a) + "/" + str(weightList[obj.name][1]))
                            print("Scale: " + str(weightList[obj.name][0]))
                            print("Obj: " + obj.name)
                            print("")
                            obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution = str(a)
        
        return{'FINISHED'}

class TLM_DisableSelection(bpy.types.Operator):
    """Disable for set"""
    bl_idname = "tlm.disable_selection"
    bl_label = "Disable for set"
    bl_description = "Disable for selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        weightList = {} #ObjName : [Dimension,Weight]
        max = 0

        if bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Scene":
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":

                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = False

        elif bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Selection":
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":

                    obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = False


        else: #Enabled
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                        obj.TLM_ObjectProperties.tlm_mesh_lightmap_use = False


        return{'FINISHED'}

class TLM_RemoveLightmapUV(bpy.types.Operator):
    """Remove Lightmap UV for set"""
    bl_idname = "tlm.remove_uv_selection"
    bl_label = "Remove Lightmap UV"
    bl_description = "Remove Lightmap UV for set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Scene":
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":

                    uv_layers = obj.data.uv_layers

                    if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                        uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                    else:
                        uv_channel = "UVMap_Lightmap"

                    for uvlayer in uv_layers:
                        if uvlayer.name == uv_channel:
                            uv_layers.remove(uvlayer)

        elif bpy.context.scene.TLM_SceneProperties.tlm_utility_set == "Selection":
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":

                    uv_layers = obj.data.uv_layers

                    if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                        uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                    else:
                        uv_channel = "UVMap_Lightmap"

                    for uvlayer in uv_layers:
                        if uvlayer.name == uv_channel:
                            uv_layers.remove(uvlayer)

        else: #Enabled
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                        uv_layers = obj.data.uv_layers

                        if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                            uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                        else:
                            uv_channel = "UVMap_Lightmap"

                        for uvlayer in uv_layers:
                            if uvlayer.name == uv_channel:
                                uv_layers.remove(uvlayer)

        return{'FINISHED'}

class TLM_SelectLightmapped(bpy.types.Operator):
    """Select all objects for lightmapping"""
    bl_idname = "tlm.select_lightmapped_objects"
    bl_label = "Select lightmap objects"
    bl_description = "Remove Lightmap UV for selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                    obj.select_set(True)

        return{'FINISHED'}

class TLM_AtlasListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "tlm_atlaslist.new_item"
    bl_label = "Add a new item"
    bl_description = "Create a new AtlasGroup"

    def execute(self, context):
        scene = context.scene
        scene.TLM_AtlasList.add()
        scene.TLM_AtlasListItem = len(scene.TLM_AtlasList) - 1

        scene.TLM_AtlasList[len(scene.TLM_AtlasList) - 1].name = "AtlasGroup"

        return{'FINISHED'}

class TLM_PostAtlasListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "tlm_postatlaslist.new_item"
    bl_label = "Add a new item"
    bl_description = "Create a new AtlasGroup"
    bl_description = ""

    def execute(self, context):
        scene = context.scene
        scene.TLM_PostAtlasList.add()
        scene.TLM_PostAtlasListItem = len(scene.TLM_PostAtlasList) - 1

        scene.TLM_PostAtlasList[len(scene.TLM_PostAtlasList) - 1].name = "AtlasGroup"

        return{'FINISHED'}

class TLM_AtlastListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "tlm_atlaslist.delete_item"
    bl_label = "Deletes an item"
    bl_description = "Delete an AtlasGroup"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        scene = context.scene
        return len(scene.TLM_AtlasList) > 0

    def execute(self, context):
        scene = context.scene
        list = scene.TLM_AtlasList
        index = scene.TLM_AtlasListItem

        for obj in bpy.context.scene.objects:

            atlasName = scene.TLM_AtlasList[index].name

            if obj.TLM_ObjectProperties.tlm_atlas_pointer == atlasName:
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = "SmartProject"

        list.remove(index)

        if index > 0:
            index = index - 1

        scene.TLM_AtlasListItem = index
        return{'FINISHED'}

class TLM_PostAtlastListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "tlm_postatlaslist.delete_item"
    bl_label = "Deletes an item"
    bl_description = "Delete an AtlasGroup"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        scene = context.scene
        return len(scene.TLM_PostAtlasList) > 0

    def execute(self, context):
        scene = context.scene
        list = scene.TLM_PostAtlasList
        index = scene.TLM_PostAtlasListItem

        for obj in bpy.context.scene.objects:

            atlasName = scene.TLM_PostAtlasList[index].name

            if obj.TLM_ObjectProperties.tlm_atlas_pointer == atlasName:
                obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode = "SmartProject"

        list.remove(index)

        if index > 0:
            index = index - 1

        scene.TLM_PostAtlasListItem = index
        return{'FINISHED'}

class TLM_AtlasListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "tlm_atlaslist.move_item"
    bl_label = "Move an item in the list"
    bl_description = "Move an item in the list"
    direction: bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        # Move index of an item render queue while clamping it
        scene = context.scene
        index = scene.TLM_AtlasListItem
        list_length = len(scene.TLM_AtlasList) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        scene.TLM_AtlasList.move(index, new_index)
        scene.TLM_AtlasListItem = new_index

    def execute(self, context):
        scene = context.scene
        list = scene.TLM_AtlasList
        index = scene.TLM_AtlasListItem

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

class TLM_PostAtlasListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "tlm_postatlaslist.move_item"
    bl_label = "Move an item in the list"
    bl_description = "Move an item in the list"
    direction: bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        # Move index of an item render queue while clamping it
        scene = context.scene
        index = scene.TLM_PostAtlasListItem
        list_length = len(scene.TLM_PostAtlasList) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        scene.TLM_PostAtlasList.move(index, new_index)
        scene.TLM_PostAtlasListItem = new_index

    def execute(self, context):
        scene = context.scene
        list = scene.TLM_PostAtlasList
        index = scene.TLM_PostAtlasListItem

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

class TLM_StartServer(bpy.types.Operator):
    bl_idname = "tlm.start_server"
    bl_label = "Start Network Server"
    bl_description = "Start Network Server"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):

        #Add progress bar from 0.15

        print("MODAL")

        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        server.startServer()

        return {'RUNNING_MODAL'}

class TLM_BuildEnvironmentProbes(bpy.types.Operator):
    bl_idname = "tlm.build_environmentprobe"
    bl_label = "Build Environment Probes"
    bl_description = "Build all environment probes from reflection cubemaps"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        for obj in bpy.context.scene.objects:

            if obj.type == "LIGHT_PROBE":
                if obj.data.type == "CUBEMAP":

                    cam_name = "EnvPCam_" + obj.name
                    camera = bpy.data.cameras.new(cam_name)
                    camobj_name = "EnvPCamera_" + obj.name
                    cam_obj = bpy.data.objects.new(camobj_name, camera)
                    bpy.context.collection.objects.link(cam_obj)
                    cam_obj.location = obj.location
                    camera.angle = math.radians(90)

                    prevResx = bpy.context.scene.render.resolution_x
                    prevResy = bpy.context.scene.render.resolution_y
                    prevCam = bpy.context.scene.camera
                    prevEngine = bpy.context.scene.render.engine
                    bpy.context.scene.camera = cam_obj

                    bpy.context.scene.render.engine = bpy.context.scene.TLM_SceneProperties.tlm_environment_probe_engine
                    bpy.context.scene.render.resolution_x = int(bpy.context.scene.TLM_SceneProperties.tlm_environment_probe_resolution)
                    bpy.context.scene.render.resolution_y = int(bpy.context.scene.TLM_SceneProperties.tlm_environment_probe_resolution)

                    savedir = os.path.dirname(bpy.data.filepath)
                    directory = os.path.join(savedir, "Probes")

                    t = 90

                    inverted = bpy.context.scene.TLM_SceneProperties.tlm_invert_direction

                    if inverted:

                        positions = {
                                "xp" : (math.radians(t), 0, math.radians(0)),
                                "zp" : (math.radians(t), 0, math.radians(t)),
                                "xm" : (math.radians(t), 0, math.radians(t*2)),
                                "zm" : (math.radians(t), 0, math.radians(-t)),
                                "yp" : (math.radians(t*2), 0, math.radians(t)),
                                "ym" : (0, 0, math.radians(t))
                        }

                    else:

                        positions = {
                                "xp" : (math.radians(t), 0, math.radians(t*2)),
                                "zp" : (math.radians(t), 0, math.radians(-t)),
                                "xm" : (math.radians(t), 0, math.radians(0)),
                                "zm" : (math.radians(t), 0, math.radians(t)),
                                "yp" : (math.radians(t*2), 0, math.radians(-t)),
                                "ym" : (0, 0, math.radians(-t))
                        }



                    cam = cam_obj
                    image_settings = bpy.context.scene.render.image_settings
                    image_settings.file_format = "HDR"
                    image_settings.color_depth = '32'

                    for val in positions:
                        cam.rotation_euler = positions[val]
                        
                        filename = os.path.join(directory, val) + "_" + camobj_name + ".hdr"
                        bpy.context.scene.render.filepath = filename
                        print("Writing out: " + val)
                        bpy.ops.render.render(write_still=True)

                    cmft_path = bpy.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_SceneProperties.tlm_cmft_path))

                    output_file_irr = camobj_name + ".hdr"

                    posx = directory + "/" + "xp_" + camobj_name + ".hdr"
                    negx = directory + "/" + "xm_" + camobj_name + ".hdr"
                    posy = directory + "/" + "yp_" + camobj_name + ".hdr"
                    negy = directory + "/" + "ym_" + camobj_name + ".hdr"
                    posz = directory + "/" + "zp_" + camobj_name + ".hdr"
                    negz = directory + "/" + "zm_" + camobj_name + ".hdr"
                    output = directory + "/" + camobj_name

                    if platform.system() == 'Windows':
                        envpipe = [cmft_path, 
                        '--inputFacePosX', posx, 
                        '--inputFaceNegX', negx, 
                        '--inputFacePosY', posy, 
                        '--inputFaceNegY', negy, 
                        '--inputFacePosZ', posz, 
                        '--inputFaceNegZ', negz, 
                        '--output0', output, 
                        '--output0params', 
                        'hdr,rgbe,latlong']
                        
                    else:
                        envpipe = [cmft_path + '--inputFacePosX' + posx 
                        + '--inputFaceNegX' + negx 
                        + '--inputFacePosY' + posy 
                        + '--inputFaceNegY' + negy 
                        + '--inputFacePosZ' + posz 
                        + '--inputFaceNegZ' + negz 
                        + '--output0' + output 
                        + '--output0params' + 'hdr,rgbe,latlong']

                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Calling CMFT with:" + str(envpipe))

                    if bpy.context.scene.TLM_SceneProperties.tlm_create_spherical:
                        subprocess.call(envpipe, shell=True)

                    input2 = output + ".hdr"
                    output2 = directory + "/" + camobj_name

                    if platform.system() == 'Windows':
                        envpipe2 = [cmft_path, 
                        '--input', input2, 
                        '--filter', 'shcoeffs', 
                        '--outputNum', '1', 
                        '--output0', output2]
                        
                    else:
                        envpipe2 = [cmft_path + 
                        '--input' + input2
                        + '-filter' + 'shcoeffs'
                        + '--outputNum' + '1'
                        + '--output0' + output2]
                        
                    if bpy.context.scene.TLM_SceneProperties.tlm_write_sh:
                        subprocess.call(envpipe2, shell=True)

                    if bpy.context.scene.TLM_SceneProperties.tlm_write_radiance:

                        use_opencl = 'false'
                        cpu_count = 2

                        # 4096 = 256 face
                        # 2048 = 128 face
                        # 1024 = 64 face
                        target_w = int(512)
                        face_size = target_w / 8
                        if target_w == 2048:
                            mip_count = 9
                        elif target_w == 1024:
                            mip_count = 8
                        else:
                            mip_count = 7

                        output_file_rad = directory + "/" + camobj_name + "_rad.hdr"
                        
                        if platform.system() == 'Windows':

                            envpipe3 = [
                                cmft_path,
                                '--input', input2,
                                '--filter', 'radiance',
                                '--dstFaceSize', str(face_size),
                                '--srcFaceSize', str(face_size),
                                '--excludeBase', 'false',
                                # '--mipCount', str(mip_count),
                                '--glossScale', '8',
                                '--glossBias', '3',
                                '--lightingModel', 'blinnbrdf',
                                '--edgeFixup', 'none',
                                '--numCpuProcessingThreads', str(cpu_count),
                                '--useOpenCL', use_opencl,
                                '--clVendor', 'anyGpuVendor',
                                '--deviceType', 'gpu',
                                '--deviceIndex', '0',
                                '--generateMipChain', 'true',
                                '--inputGammaNumerator', '1.0',
                                '--inputGammaDenominator', '1.0',
                                '--outputGammaNumerator', '1.0',
                                '--outputGammaDenominator', '1.0',
                                '--outputNum', '1',
                                '--output0', output_file_rad,
                                '--output0params', 'hdr,rgbe,latlong'
                            ]

                            subprocess.call(envpipe3)

                        else:

                            envpipe3 = cmft_path + \
                                ' --input "' + input2 + '"' + \
                                ' --filter radiance' + \
                                ' --dstFaceSize ' + str(face_size) + \
                                ' --srcFaceSize ' + str(face_size) + \
                                ' --excludeBase false' + \
                                ' --glossScale 8' + \
                                ' --glossBias 3' + \
                                ' --lightingModel blinnbrdf' + \
                                ' --edgeFixup none' + \
                                ' --numCpuProcessingThreads ' + str(cpu_count) + \
                                ' --useOpenCL ' + use_opencl + \
                                ' --clVendor anyGpuVendor' + \
                                ' --deviceType gpu' + \
                                ' --deviceIndex 0' + \
                                ' --generateMipChain true' + \
                                ' --inputGammaNumerator ' + '1.0' + \
                                ' --inputGammaDenominator 1.0' + \
                                ' --outputGammaNumerator 1.0' + \
                                ' --outputGammaDenominator 1.0' + \
                                ' --outputNum 1' + \
                                ' --output0 "' + output_file_rad + '"' + \
                                ' --output0params hdr,rgbe,latlong'

                            subprocess.call([envpipe3], shell=True)

                    for obj in bpy.context.scene.objects:
                        obj.select_set(False)

                    cam_obj.select_set(True)
                    bpy.ops.object.delete()
                    bpy.context.scene.render.resolution_x = prevResx
                    bpy.context.scene.render.resolution_y = prevResy
                    bpy.context.scene.camera = prevCam
                    bpy.context.scene.render.engine = prevEngine

                    print("Finished building environment probes")


        return {'RUNNING_MODAL'}

class TLM_CleanBuildEnvironmentProbes(bpy.types.Operator): 
    bl_idname = "tlm.clean_environmentprobe"
    bl_label = "Clean Environment Probes"
    bl_description = "Clean Environment Probes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        savedir = os.path.dirname(bpy.data.filepath)
        dirpath = os.path.join(savedir, "Probes")

        if os.path.isdir(dirpath):
            for file in os.listdir(dirpath):
                os.remove(os.path.join(dirpath + "/" + file))

        return {'FINISHED'}

class TLM_MergeAdjacentActors(bpy.types.Operator): 
    bl_idname = "tlm.merge_adjacent_actors"
    bl_label = "Merge adjacent actors"
    bl_description = "Merges the adjacent faces/vertices of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        return {'FINISHED'}

class TLM_PrepareUVMaps(bpy.types.Operator): 
    bl_idname = "tlm.prepare_uvmaps"
    bl_label = "Prepare UV maps"
    bl_description = "Prepare UV lightmaps for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene



        return {'FINISHED'}

class TLM_LoadLightmaps(bpy.types.Operator): 
    bl_idname = "tlm.load_lightmaps"
    bl_label = "Load Lightmaps"
    bl_description = "Load lightmaps from selected folder"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        utility.transfer_load()

        build.finish_assemble()

        return {'FINISHED'}

class TLM_ToggleTexelDensity(bpy.types.Operator): 
    bl_idname = "tlm.toggle_texel_density"
    bl_label = "Toggle Texel Density"
    bl_description = "Toggle visualize lightmap texel density for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                uv_layers = obj.data.uv_layers

                #if the object has a td_vis in the uv maps, toggle off
                #else toggle on

                if obj.TLM_ObjectProperties.tlm_use_default_channel:

                    for i in range(0, len(uv_layers)):
                        if uv_layers[i].name == 'UVMap_Lightmap':
                            uv_layers.active_index = i
                            break
                else:

                    for i in range(0, len(uv_layers)):
                        if uv_layers[i].name == obj.TLM_ObjectProperties.tlm_uv_channel:
                            uv_layers.active_index = i
                            break

                #filepath = r"C:\path\to\image.png"

                #img = bpy.data.images.load(filepath)

                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        space_data = area.spaces.active
                        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
                        new_window = context.window_manager.windows[-1]

                        area = new_window.screen.areas[-1]
                        area.type = 'VIEW_3D'
                        #bg = space_data.background_images.new()
                        print(bpy.context.object)
                        bpy.ops.object.bake_td_uv_to_vc()

                        #bg.image = img
                        break

                
                #set active uv_layer to 
                

        print("TLM_Viz_Toggle")

        return {'FINISHED'}


def TLM_DoubleResolution():
    pass

def TLM_HalfResolution():
    pass

def TLM_DivideLMGroups():
    pass