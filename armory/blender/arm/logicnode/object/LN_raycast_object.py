from arm.logicnode.arm_nodes import *

class RaycastObjectNode(ArmLogicTreeNode):
    """Casts a ray from the given screen coordinates and checks whether it hits the given object.

    The ray is tested against the object's oriented bounding box, so rotated
    and scaled objects are handled correctly.

    @input Object: The object to test.
    @input X: Screen X coordinate.
    @input Y: Screen Y coordinate.
    @input Camera: The camera to cast the ray from.
    @input Exact Mesh: If enabled, after the bounding box check passes, the ray
        is tested against the mesh triangles to get the exact hit location.
        Skinned and morphed meshes fall back to the bounding box result.

    @output True: Activated if the object is hit.
    @output False: Activated if the object is not hit.
    @output Location: The world location of the hit.
    """
    bl_idname = 'LNRaycastObjectNode'
    bl_label = 'Raycast Object'
    arm_section = 'props'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmBoolSocket', 'Exact Mesh', default_value=False)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
        self.add_output('ArmVectorSocket', 'Location')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)

