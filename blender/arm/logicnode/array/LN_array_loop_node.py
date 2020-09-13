from arm.logicnode.arm_nodes import *


class ArrayLoopNode(ArmLogicTreeNode):
    """ArrayLoop node"""
    bl_idname = 'LNArrayLoopNode'
    bl_label = 'Array Loop'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('NodeSocketShader', 'Value')
        self.add_output('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')


add_node(ArrayLoopNode, category=PKG_AS_CATEGORY)
