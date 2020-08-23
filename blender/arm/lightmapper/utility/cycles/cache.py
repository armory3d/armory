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
    print("Restore cache")

def backup_material_rename(obj):
    if "TLM_PrevMatArray" in obj:
        print("Has PrevMat B")
        for slot in obj.material_slots:
            if slot.material.name.endswith("_Original"):
                newname = slot.material.name[1:-9]
                if newname in bpy.data.materials:
                    bpy.data.materials.remove(bpy.data.materials[newname])
                slot.material.name = newname

        del obj["TLM_PrevMatArray"]

def backup_material_restore(obj):
    print("RESTORE")

    if "TLM_PrevMatArray" in obj:

        print("Has PrevMat A")
        #Running through the slots
        prevMatArray = obj["TLM_PrevMatArray"]
        slotsLength = len(prevMatArray)

        if len(prevMatArray) > 0:
            for idx, slot in enumerate(obj.material_slots): #For each slot, we get the index
                #We only need the index, corresponds to the array index
                try:
                    originalMaterial = prevMatArray[idx]
                except IndexError:
                    originalMaterial = ""

                slot.material.user_clear()

                if "." + originalMaterial + "_Original" in bpy.data.materials:
                    slot.material = bpy.data.materials["." + originalMaterial + "_Original"]
                    slot.material.use_fake_user = False


        #slot.material = 

        #Remove material after changin
        #We only rename after every change is complete

        #if "." + material.name + "_Original" in bpy.data.materials:

    # material = slot.material
    # if "." + material.name + "_Original" in bpy.data.materials:
    #     original = bpy.data.materials["." + material.name + "_Original"]
    #     slot.material = original
    #     material.name = material.name
    #     original.name = original.name[1:-9]
    #     original.use_fake_user = False
    #     material.user_clear()
    #     bpy.data.materials.remove(material)
    #     #Reset number
    # else:
    #     pass
        #Check if material has nodes with lightmap prefix