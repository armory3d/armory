from arm.logicnode.arm_nodes import *

class GetPropertyNode(ArmLogicTreeNode):
    """Get property node"""
    bl_idname = 'LNGetPropertyNode'
    bl_label = 'Get Property'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Property')
        self.add_output('NodeSocketShader', 'Value')
        self.add_output('NodeSocketString', 'Property')

add_node(GetPropertyNode, category=MODULE_AS_CATEGORY, section='props')
