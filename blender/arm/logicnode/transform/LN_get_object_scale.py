from arm.logicnode.arm_nodes import *

class GetScaleNode(ArmLogicTreeNode):
    """Returns the scale of the given object."""
    bl_idname = 'LNGetScaleNode'
    bl_label = 'Get Object Scale'
    arm_version = 1

    def init(self, context):
        super(GetScaleNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Scale')

add_node(GetScaleNode, category=PKG_AS_CATEGORY, section='scale')
