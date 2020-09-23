from arm.logicnode.arm_nodes import *

class GetMeshNode(ArmLogicTreeNode):
    """Use to get the mesh of an object."""
    bl_idname = 'LNGetMeshNode'
    bl_label = 'Get Mesh'
    arm_version = 1

    def init(self, context):
        super(GetMeshNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Mesh')

add_node(GetMeshNode, category=PKG_AS_CATEGORY, section='props')
