import bpy

#Todo - Check if already exists, in case multiple objects has the same material

def backup_material_copy(slot):
    material = slot.material
    dup = material.copy()
    dup.name = "." + material.name + "_Original"
    dup.use_fake_user = True

def backup_material_cache(slot, path):
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)

def backup_material_cache_restore(slot, path):
    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Restore cache")

# def backup_material_restore(obj): #??
#     if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
#         print("Restoring material for: " + obj.name)

#Check if object has TLM_PrevMatArray
#   if yes
#       - check if array.len is bigger than 0:
#           if yes:
#               for slot in object:
#                   originalMaterial = TLM_PrevMatArray[index]
#
#
#           if no:
#               - In which cases are these?

#   if no:
#    - In which cases are there not?
#    - If a lightmapped material was applied to a non-lightmap object?


                # if bpy.data.materials[originalMaterial].users > 0: #TODO - Check if all lightmapped

                #     print("Material has multiple users")
                
                #     if originalMaterial in bpy.data.materials:
                #         slot.material = bpy.data.materials[originalMaterial]
                #         slot.material.use_fake_user = False
                #     elif "." + originalMaterial + "_Original" in bpy.data.materials:
                #         slot.material = bpy.data.materials["." + originalMaterial + "_Original"]
                #         slot.material.use_fake_user = False
                
                # else:

                #     print("Material has one user")

                #     if "." + originalMaterial + "_Original" in bpy.data.materials:
                #         slot.material = bpy.data.materials["." + originalMaterial + "_Original"]
                #         slot.material.use_fake_user = False
                #     elif originalMaterial in bpy.data.materials:
                #         slot.material = bpy.data.materials[originalMaterial]
                #         slot.material.use_fake_user = False

def backup_material_restore(obj): #??
    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Restoring material for: " + obj.name)

    if "TLM_PrevMatArray" in obj:

        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("Material restore array found: " + str(obj["TLM_PrevMatArray"]))
        #Running through the slots
        prevMatArray = obj["TLM_PrevMatArray"]
        slotsLength = len(prevMatArray)

        if len(prevMatArray) > 0:
            for idx, slot in enumerate(obj.material_slots): #For each slot, we get the index
                #We only need the index, corresponds to the array index
                try:
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Attempting to set material")
                    originalMaterial = prevMatArray[idx]
                except IndexError:
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        print("Material restore failed - Resetting")
                    originalMaterial = ""

                if slot.material is not None:
                    #if slot.material.users < 2:
                    #slot.material.user_clear() #Seems to be bad; See: https://developer.blender.org/T49837
                    #bpy.data.materials.remove(slot.material)

                    if "." + originalMaterial + "_Original" in bpy.data.materials:
                        slot.material = bpy.data.materials["." + originalMaterial + "_Original"]
                        slot.material.use_fake_user = False

        else:

            print("No previous material for " + obj.name)

    else:

        print("No previous material for " + obj.name)

def backup_material_rename(obj): #??
    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Renaming material for: " + obj.name)


    if "TLM_PrevMatArray" in obj:

        for slot in obj.material_slots:

            if slot.material is not None:
                if slot.material.name.endswith("_Original"):
                    newname = slot.material.name[1:-9]
                    if newname in bpy.data.materials:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("Removing material: " + bpy.data.materials[newname].name)
                        #if bpy.data.materials[newname].users < 2:
                            #bpy.data.materials.remove(bpy.data.materials[newname]) #TODO - Maybe remove this
                    slot.material.name = newname

        del obj["TLM_PrevMatArray"]

    else:

        print("No Previous material array for: " + obj.name)