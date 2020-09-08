import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class DynamicNode(ArmLogicTreeNode):
    '''Dynamic node'''
    bl_idname = 'LNDynamicNode'
    bl_label = 'Dynamic'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketShader', 'Dynamic', is_var=True)

add_node(DynamicNode, category=MODULE_AS_CATEGORY)
