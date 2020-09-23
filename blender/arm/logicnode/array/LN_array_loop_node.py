from arm.logicnode.arm_nodes import *


class ArrayLoopNode(ArmLogicTreeNode):
    """Use to loop trought an array."""
    bl_idname = 'LNArrayLoopNode'
    bl_label = 'Array Loop'
    arm_version = 1

    def init(self, context):
        super(ArrayLoopNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('NodeSocketShader', 'Value')
        self.add_output('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')


add_node(ArrayLoopNode, category=PKG_AS_CATEGORY)
