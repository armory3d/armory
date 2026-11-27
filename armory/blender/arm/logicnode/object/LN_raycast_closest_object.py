from arm.logicnode.arm_nodes import *

class RaycastClosestObjectNode(ArmLogicTreeNode):
    """Casts a ray from the given screen coordinates and returns the closest hit object of the given array.

    The ray is tested against each object's oriented bounding box, so rotated
    and scaled objects are handled correctly. The closest object is the one
    with the nearest hit along the ray.

    @input Obj Array: The objects to test.
    @input X: Screen X coordinate.
    @input Y: Screen Y coordinate.
    @input Camera: The camera to cast the ray from.
    @input Exact Mesh: If enabled, after the bounding box check passes, the ray
        is tested against the mesh triangles to get the exact hit location.
        Skinned and morphed meshes fall back to the bounding box result.

    @output True: Activated if an object is hit.
    @output False: Activated if no object is hit.
    @output Object: The closest hit object.
    @output Location: The world location of the hit.
    """
    bl_idname = 'LNRaycastClosestObjectNode'
    bl_label = 'Raycast Closest Object'
    arm_section = 'props'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Obj Array')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmBoolSocket', 'Exact Mesh', default_value=False)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
        self.add_output('ArmNodeSocketObject', 'Object')
        self.add_output('ArmVectorSocket', 'Location')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)

