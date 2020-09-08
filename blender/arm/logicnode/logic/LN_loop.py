from arm.logicnode.arm_nodes import *

class LoopNode(ArmLogicTreeNode):
    """Loop node"""
    bl_idname = 'LNLoopNode'
    bl_label = 'Loop'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketInt', 'From')
        self.add_input('NodeSocketInt', 'To')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(LoopNode, category=MODULE_AS_CATEGORY, section='flow')
