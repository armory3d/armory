from arm.logicnode.arm_nodes import *

class ScaleObjectNode(ArmLogicTreeNode):
    """Scale object node"""
    bl_idname = 'LNScaleObjectNode'
    bl_label = 'Scale Object'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ScaleObjectNode, category=PKG_AS_CATEGORY, section='scale')
