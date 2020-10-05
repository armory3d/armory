from arm.logicnode.arm_nodes import *

class GetObjectOffscreenNode(ArmLogicTreeNode):
    """Returns if the given object is offscreen. Don't works if culling is disabled."""
    bl_idname = 'LNGetObjectOffscreenNode'
    bl_label = 'Get Object Offscreen'
    arm_version = 1

    def init(self, context):
        super(GetObjectOffscreenNode, self).init(context)
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Is Object Offscreen')
        self.outputs.new('NodeSocketBool', 'Is Mesh Offscreen')
        self.outputs.new('NodeSocketBool', 'Is Shadow Offscreen')

add_node(GetObjectOffscreenNode, category=PKG_AS_CATEGORY, section='props')
