from arm.logicnode.arm_nodes import *

class SetMeshNode(ArmLogicTreeNode):
    """Set mesh node"""
    bl_idname = 'LNSetMeshNode'
    bl_label = 'Set Mesh'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Mesh')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMeshNode, category=PKG_AS_CATEGORY, section='props')
