from arm.logicnode.arm_nodes import *

class SetMeshNode(ArmLogicTreeNode):
    """Sets the mesh of the given object."""
    bl_idname = 'LNSetMeshNode'
    bl_label = 'Set Object Mesh'
    arm_section = 'props'
    arm_version = 1

    def init(self, context):
        super(SetMeshNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Mesh')
        self.add_output('ArmNodeSocketAction', 'Out')
