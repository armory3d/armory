from arm.logicnode.arm_nodes import *

class PickObjectNode(ArmLogicTreeNode):
    """Pick closest object node"""
    bl_idname = 'LNPickObjectNode'
    bl_label = 'Pick Object'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Screen Coords')
        self.add_output('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Hit')

add_node(PickObjectNode, category=MODULE_AS_CATEGORY, section='ray')
