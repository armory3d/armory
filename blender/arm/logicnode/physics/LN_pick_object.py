from arm.logicnode.arm_nodes import *

class PickObjectNode(ArmLogicTreeNode):
    """Pick closest object node"""
    bl_idname = 'LNPickObjectNode'
    bl_label = 'Pick Object'
    arm_version = 1

    def init(self, context):
        super(PickObjectNode, self).init(context)
        self.add_input('NodeSocketVector', 'Screen Coords')
        self.add_output('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('NodeSocketVector', 'Hit')

add_node(PickObjectNode, category=PKG_AS_CATEGORY, section='ray')
