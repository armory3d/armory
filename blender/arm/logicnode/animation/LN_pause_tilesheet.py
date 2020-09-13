from arm.logicnode.arm_nodes import *

class PauseTilesheetNode(ArmLogicTreeNode):
    """Pause tilesheet node"""
    bl_idname = 'LNPauseTilesheetNode'
    bl_label = 'Pause Tilesheet'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseTilesheetNode, category=PKG_AS_CATEGORY, section='tilesheet')
