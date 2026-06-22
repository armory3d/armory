from arm.logicnode.arm_nodes import *

class SetParentNode(ArmLogicTreeNode):
    """Sets the direct parent (nearest in the hierarchy) of the given object.
    @input Object: Object to be parented.
    @input Parent: New parent object. Use `Get Scene Root` node to unparent object.
    @input Keep Transform: Keep transform after unparenting from old parent
    @input Parent Inverse: Preserve object transform after parenting to new object.

    @seeNode Get Object Parent"""
    bl_idname = 'LNSetParentNode'
    bl_label = 'Set Object Parent'
    arm_section = 'relations'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent')
        self.add_input('ArmBoolSocket', 'Keep Transform', default_value = True)
        self.add_input('ArmBoolSocket', 'Parent Inverse')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement(
            'LNSetParentNode', self.arm_version, 'LNSetParentNode', 2,
            in_socket_mapping={0:0, 1:1, 2:2}, out_socket_mapping={0:0}
        )
