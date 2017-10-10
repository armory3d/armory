
import bpy

def make(obj):
    traverse(obj)

def traverse(obj):
    if obj == None or obj.library == None or obj.proxy != None:
        return

    # Make proxy for all linked children
    for c in obj.children:
        traverse(c)

    override = bpy.context.copy()
    override['object'] = obj
    bpy.context.scene.objects.active = obj
    bpy.ops.object.proxy_make(override)

    # Reparent created proxies
    for c in obj.children:
        if c.proxy != None:
            c.parent = bpy.context.scene.objects.active
            c.matrix_parent_inverse = bpy.context.scene.objects.active.matrix_world.inverted()
