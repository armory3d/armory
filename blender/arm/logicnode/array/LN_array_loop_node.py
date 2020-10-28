from arm.logicnode.arm_nodes import *


class ArrayLoopNode(ArmLogicTreeNode):
    """Loops through each item of the given array."""
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
