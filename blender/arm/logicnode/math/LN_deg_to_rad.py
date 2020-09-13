from arm.logicnode.arm_nodes import *

class DegToRadNode(ArmLogicTreeNode):
    """Degrees to radians node"""
    bl_idname = 'LNDegToRadNode'
    bl_label = 'Deg to Rad'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'Degrees')
        self.add_output('NodeSocketFloat', 'Radians')

add_node(DegToRadNode, category=PKG_AS_CATEGORY, section='angle')
