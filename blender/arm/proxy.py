import bpy

def proxy_sync_loc(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_loc:
        sync_location(context.object)

def proxy_sync_rot(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_rot:
        sync_rotation(context.object)

def proxy_sync_scale(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_scale:
        sync_scale(context.object)

def proxy_sync_materials(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_materials:
        sync_materials(context.object)

def proxy_sync_modifiers(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_modifiers:
        sync_modifiers(context.object)

def proxy_sync_traits(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_traits:
        sync_traits(context.object)

def make(obj):
    traverse(obj, is_parent=True)

def traverse(obj, is_parent=False):
    if obj == None or obj.library == None or obj.proxy != None:
        return

    # Make proxy for all linked children
    for c in obj.children:
        traverse(c)

    override = bpy.context.copy()
    override['object'] = obj
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.proxy_make(override)

    # Reparent created proxies
    for c in obj.children:
        if c.proxy != None:
            c.parent = bpy.context.view_layer.objects.active
            c.matrix_parent_inverse = bpy.context.view_layer.objects.active.matrix_world.inverted()

    active = bpy.context.view_layer.objects.active
    sync_modifiers(active)
    # No transform sync for parent
    if is_parent:
        active.arm_proxy_sync_loc = False
        active.arm_proxy_sync_rot = False
        active.arm_proxy_sync_scale = False

def sync_location(obj):
    obj.location = obj.proxy.location

def sync_rotation(obj):
    obj.rotation_euler = obj.proxy.rotation_euler

def sync_scale(obj):
    obj.scale = obj.proxy.scale

# https://blender.stackexchange.com/questions/4878
def sync_modifiers(obj):
    proxy = obj.proxy
    obj.modifiers.clear()
    for mSrc in obj.proxy.modifiers:
        mDst = obj.modifiers.get(mSrc.name, None)
        if not mDst:
            mDst = obj.modifiers.new(mSrc.name, mSrc.type)

        # collect names of writable properties
        properties = [p.identifier for p in mSrc.bl_rna.properties
                      if not p.is_readonly]

        # copy those properties
        for prop in properties:
            setattr(mDst, prop, getattr(mSrc, prop))

def sync_collection(cSrc, cDst):
    cDst.clear()
    for mSrc in cSrc:
        mDst = cDst.get(mSrc.name, None)
        if not mDst:
            mDst = cDst.add()

        # collect names of writable properties
        properties = [p.identifier for p in mSrc.bl_rna.properties
                      if not p.is_readonly]

        # copy those properties
        for prop in properties:
            setattr(mDst, prop, getattr(mSrc, prop))

def sync_traits(obj):
    sync_collection(obj.proxy.arm_traitlist, obj.arm_traitlist)
    for i in range(0, len(obj.arm_traitlist)):
        sync_collection(obj.proxy.arm_traitlist[i].arm_traitpropslist, obj.arm_traitlist[i].arm_traitpropslist)

def sync_materials(obj):
    # Blender likes to crash here:(
    pass
    # proxy_mats = []
    # for slot in obj.proxy.material_slots:
    #     proxy_mats.append(slot.name)
    # override = bpy.context.copy()
    # override['object'] = obj
    # obj.active_material_index = 0
    # for i in range(len(obj.material_slots)):
    #     bpy.ops.object.material_slot_remove(override)
    # for slot in proxy_mats:
    #     bpy.ops.object.material_slot_add(override)
    #     obj.material_slots[-1].material = bpy.data.materials[slot]
