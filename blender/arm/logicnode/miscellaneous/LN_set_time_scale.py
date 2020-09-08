import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetTimeScaleNode(ArmLogicTreeNode):
    """Set time scale node"""
    bl_idname = 'LNSetTimeScaleNode'
    bl_label = 'Set Time Scale'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Scale', default_value=1.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetTimeScaleNode, category=MODULE_AS_CATEGORY)
