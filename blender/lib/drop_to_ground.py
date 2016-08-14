# http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Object/Drop_to_ground
import bpy
from bpy.props import *
import bmesh
from random import seed, uniform
import math
import mathutils
from mathutils import *

def transform_ground_to_world(sc, ground):
    tmpMesh = ground.to_mesh(sc, True, 'PREVIEW')
    tmpMesh.transform(ground.matrix_world)
    tmp_ground = bpy.data.objects.new('tmpGround', tmpMesh)
    sc.objects.link(tmp_ground)
    sc.update()
    return tmp_ground

def get_lowest_world_co_from_mesh(ob, mat_parent=None):
    bme = bmesh.new()
    bme.from_mesh(ob.data)
    mat_to_world = ob.matrix_world.copy()
    if mat_parent:
        mat_to_world = mat_parent * mat_to_world
    lowest = None
    # bme.verts.index_update()
    for v in bme.verts:
        if not lowest:
            lowest = v
        if (mat_to_world * v.co).z < (mat_to_world * lowest.co).z:
            lowest = v
    lowest_co = mat_to_world * lowest.co
    bme.free()
    return lowest_co

def drop_objects(self, context, ground, obs, use_origin, offset, drop_random):
    # Random distribution
    if drop_random:
        halfX = ground.dimensions.x / 2
        halfY = ground.dimensions.y / 2
        for ob in obs:
            # if spherical is True:
                # ob.matrix_world = Matrix.Translation((0, 0, 100))
            # else:
            ob.location = (
                ground.location.x + uniform(-halfX, halfX),
                ground.location.y + uniform(-halfY, halfY),
                ground.location.z + 1000)

    # if spherical is True:
        # ground.matrix_world.translation = ((0, 0, 0))
    tmp_ground = transform_ground_to_world(context.scene, ground)
    down = Vector((0, 0, -10000))
    mat_original = ground.matrix_world.copy()

    for ob in obs:
        if use_origin:
            lowest_world_co = ob.location
        else:
            lowest_world_co = get_lowest_world_co_from_mesh(ob)

        if not lowest_world_co:
            continue

        was_hit, hit_location, hit_normal, hit_index = \
            tmp_ground.ray_cast(lowest_world_co, lowest_world_co + down)

        if hit_index is -1:
            continue

        to_ground_vec = hit_location - lowest_world_co
        ob.matrix_world *= Matrix.Translation(to_ground_vec)
        ob.location.z += offset

    ground.matrix_world = mat_original

    bpy.ops.object.select_all(action='DESELECT')
    tmp_ground.select = True
    bpy.ops.object.delete('EXEC_DEFAULT')
    for ob in obs:
        ob.select = True
    ground.select = True
    bpy.context.scene.objects.active = ground

class OBJECT_OT_drop_to_ground(bpy.types.Operator):
    bl_idname = "object.drop_on_active"
    bl_label = "Drop to Ground"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Drop selected objects on active object"

    use_origin = BoolProperty(
            name="Use Center",
            description="Drop to objects origins",
            default=False)

    drop_random = BoolProperty(
            name="Random",
            description="Drop to random point",
            default=False)

    offset = FloatProperty(
            name="Margin",
            description="Offset from the ground",
            default=0.0)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) >= 2
    
    def execute(self, context):
        ground = context.object
        obs = context.selected_objects
        obs.remove(ground)
        drop_objects(self, context, ground, obs, self.use_origin, self.offset, self.drop_random)
        return {'FINISHED'}

# http://blenderartists.org/forum/showthread.php?229346-AddOn-Duplicate-Multiple-Linked
def duplicate_object(context, numCopies, transVec, doParent):
    activeObj = context.active_object
    dupCopies = []
    dupCopies.append(activeObj)
    while numCopies > 0:
        bpy.ops.object.duplicate_move_linked(OBJECT_OT_duplicate={"linked":True, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":transVec, "release_confirm":False})
        dupCopies.append(context.active_object)
        numCopies -= 1
    if doParent:
        groupName = activeObj.name + "_Copies"
        bpy.ops.object.add(type='EMPTY')
        groupEmpty = context.active_object
        groupEmpty.name = groupName
        for i in dupCopies:
            bpy.data.objects[i.name].select = True
            bpy.data.objects[groupEmpty.name].select = True
        bpy.ops.object.parent_set(type="OBJECT")
    else:
        for i in dupCopies:
            bpy.data.objects[i.name].select = True

class OBJECT_OT_multi_duplicate(bpy.types.Operator):
    bl_idname = "object.multi_duplicate"
    bl_label = "Duplicate Multiple Linked"
    bl_options = {"REGISTER", "UNDO"}
    
    num_copies = bpy.props.IntProperty(name="Number of Copies:", default=1, description="Number of copies", min=1, max=5000, subtype="NONE")
    xyz_offset = bpy.props.FloatVectorProperty(name="XYZ Offset:", default=(0.0,0.0,0.0), min=-1000, max=1000, description="XYZ Offset")
    do_parent = bpy.props.BoolProperty(name="Parent under Empty", default=True)
 
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob == None:
            return False
        elif ob.select:
            return True
        return False

    def execute(self, context):
        duplicate_object(context, self.num_copies, self.xyz_offset, self.do_parent)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)

class ArmToolsPanel(bpy.types.Panel):
    bl_label = "Armory Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("object.drop_on_active")
        self.layout.operator("object.multi_duplicate")

def register():
    bpy.utils.register_class(OBJECT_OT_drop_to_ground)
    bpy.utils.register_class(OBJECT_OT_multi_duplicate)
    bpy.utils.register_class(ArmToolsPanel)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_drop_to_ground)
    bpy.utils.unregister_class(OBJECT_OT_multi_duplicate)
    bpy.utils.unregister_class(ArmToolsPanel)
