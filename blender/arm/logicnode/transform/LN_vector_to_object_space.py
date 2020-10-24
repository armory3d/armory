from arm.logicnode.arm_nodes import *

class VectorToObjectSpaceNode(ArmLogicTreeNode):
    """Converts a world space vector to the given object space."""
    bl_idname = 'LNVectorToObjectSpaceNode'
    bl_label = 'Vector To Object Space'
    arm_version = 1

    def init(self, context):
        super(VectorToObjectSpaceNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'World Space')
        self.add_output('NodeSocketVector', 'Object Space')

add_node(VectorToObjectSpaceNode, category=PKG_AS_CATEGORY, section='location')
