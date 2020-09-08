from arm.logicnode.arm_nodes import *

class SubStringNode(ArmLogicTreeNode):
    """Sub string node"""
    bl_idname = 'LNSubStringNode'
    bl_label = 'Sub String'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketInt', 'Start')
        self.add_input('NodeSocketInt', 'End')

add_node(SubStringNode, category=MODULE_AS_CATEGORY)
