import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BlendActionNode(ArmLogicTreeNode):
    """Blend action node"""
    bl_idname = 'LNBlendActionNode'
    bl_label = 'Blend Action'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action 1')
        self.add_input('ArmNodeSocketAnimAction', 'Action 2')
        self.add_input('NodeSocketFloat', 'Factor', default_value = 0.5)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(BlendActionNode, category=MODULE_AS_CATEGORY)
