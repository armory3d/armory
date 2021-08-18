from arm.logicnode.arm_nodes import *

class SetLocationNode(ArmLogicTreeNode):
    """Set the location of the given object in world coordinates.

    @input Parent Relative: If enabled, transforms the world coordinates into object parent local coordinates

    @seeNode Get Object Location
    @seeNode World Vector to Local Space
    @seeNode Vector to Object Orientation
    """
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Object Location'
    arm_section = 'location'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmBoolSocket', 'Parent Relative')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
        return NodeReplacement.Identity(self)
