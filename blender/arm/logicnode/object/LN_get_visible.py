from arm.logicnode.arm_nodes import *

class GetVisibleNode(ArmLogicTreeNode):
    """Get Visible node"""
    bl_idname = 'LNGetVisibleNode'
    bl_label = 'Get Visible'
    arm_version = 1

    def init(self, context):
        super(GetVisibleNode, self).init(context)
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Object')
        self.outputs.new('NodeSocketBool', 'Mesh')
        self.outputs.new('NodeSocketBool', 'Shadow')

add_node(GetVisibleNode, category=PKG_AS_CATEGORY, section='props')
